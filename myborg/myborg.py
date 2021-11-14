import json
import subprocess
import os
from .config import ReadConfig

class MyBorg(object):
    """ MyBorg
        A class to wrap borg command lines
    """
    def __init__(self, repo_location=None,
                 showoutput=False,
                 showcmd=False,
                 advanced_file=None,
                 backup_name='{now:%Y-%m-%d %H:%M:%S}',
                 args=[], excludes=[], locs=[]):

        self.config = ReadConfig(advanced_file=advanced_file)
        self.program = self.config.program
        self.args = self.config.default_args
        self.repo_path = self.config.repo_path
        self.repo_dif = self.config.repo_dir
        self.repo_name = self.config.repo_name
        self.repo = self.config.repo
        self.backup_name = self.config.backup_name
        self.excludes = self.config.exclude_locs
        self.locs = self.config.backup_locs
        self.estimatefiles = self.config.estimate_files
        self.prune_keep = self.config.prune_keep
        self.storage_quota = self.config.storage_quota
        self.make_parent_dirs = self.config.make_parent_dirs
        self.showoutput = showoutput
        self.showcmd = showcmd

    def _build_cmd(self, precmd="", dbtype=None, borgcmd=None, args=[], additional_args=[]):
        """ Used to build the borg command line to spawn """
        realborgcmd = borgcmd
        if borgcmd == 'prune' or borgcmd == 'info' or borgcmd == 'init':
            repo = self.config.repo_path
        elif borgcmd == 'videosdatabase' or borgcmd == 'musicdatabase':
            repo = f"{self.config.repo_path}::{borgcmd} {self.config.backup_name}"
            realborgcmd = 'create'
            precmd = self.__createmysqldump(dbtype=borgcmd)
        else:
            repo = self.config.repo
        cmd = (f"{precmd} "
               f"{self.program} "
               f"{realborgcmd} "
               f"{' '.join(self.config.default_args[borgcmd])} "
               f"{' '.join(additional_args)}")
        if borgcmd == 'create':
            cmd += f" {' '.join(self.excludes)} "
        if borgcmd == 'prune':
            cmd += f" {' '.join(self.prune_keep)} "
        if borgcmd == 'videosdatabase' or borgcmd == 'musicdatabase':
            cmd += f" --stdin-name MySQL-{borgcmd}"
        if borgcmd == 'init':
            cmd += f" --encryption {self.config.encryption}"
        cmd += f" '{repo}' "
        if borgcmd == 'create':
            cmd += f" {' '.join(self.locs)}"
        if borgcmd == 'videosdatabase' or borgcmd == 'musicdatabase':
            cmd += " -"
        return cmd

    def videodatabase(self):
        return self.__run(borgcmd="videosdatabase")


    def musicdatabase(self):
        return self.__run(borgcmd="musicdatabase")
        
    def __createmysqldump(self, dbtype=None):
        # Define the current database versions. This should be
        # done much better than this ugly hardcoded way!
        # Probably can be read from kodi. Or use mysql commands to
        # find the latest version automatically. Or run kodi --version and
        # keep a map of the latest versions?
        dbversions = {'videosdatabase': 119,
                      'musicdatabase': 82}
        
        if self.config.dbs[dbtype]['type'].lower() != 'mysql':
            print(f"Unable to backup database type {self.config.dbs[dbtype]['type']}. Only mysql databases may be backed up")
            return []
        dbname = f"{self.config.dbs[dbtype]['name']}{dbversions[dbtype]}"
        try:
            dbport = self.config.dbs[dbtype]['port']
        except:
            dbport = 3306
        dbuser = self.config.dbs[dbtype]['user']
        dbpass = self.config.dbs[dbtype]['pass']
        dbhost = self.config.dbs[dbtype]['host']
        # Assumes that mysqldump is in the path. Probably should check
        # before trying to run if it's actually installed!
        dbdumpcmd = f"mysqldump -u{dbuser} -p{dbpass} -h{dbhost} -P{dbport} {dbname} |"
        return dbdumpcmd

    def init(self):
        additional_args = []
        if self.storage_quota is not None:
            additional_args += [f"--storage-quota {self.storage_quota}"]
        if self.make_parent_dirs:
            additional_args += ["--make-parent-dirs"]
        return self.__run(borgcmd="init", additional_args=additional_args)

    def prune(self):
        return self.__run(borgcmd="prune")

    def create(self):
        return self.__run(borgcmd="create", additional_args=['--stats'])

    def info(self, lastfilecount=False, archive_count=5, additional_args=[]):
        if lastfilecount:
            archive_count=1
        if archive_count >= 1:
            additional_args = [f'--last {archive_count}']

        gen = self.__run(borgcmd="info", additional_args=additional_args)
        if lastfilecount:
            rc = None
            for g in gen:
                if 'results' in g.keys():
                    if g['results'] is None:
                        return None
                    return g['results']['archives'][0]['stats']['nfiles']
        else:
            return gen

    def estimate(self, status_update_count=1000):
        if self.estimatefiles == 'fast':
            return self.info(lastfilecount=True)
        elif self.estimatefiles == 'slow':
            return self.__run(borgcmd="create",
                              additional_args=['--dry-run', '--list'],
                              status_update_count=status_update_count)
        elif self.estimatefiles == 'none':
            return None
        else:
            print(f"Invalid value {self.estimatefiles} for estimate-files in config")
            print("Accepted values are: fast, slow, none")
            return None

    def __run(self, borgcmd=None, additional_args=[], status_update_count=0, dbinfo=None):
        """ Spawn a borg process. Output will be sent
            line by line to the calling script. Most lines are
            untouched, but some will have additional info added
            to what borg sent
        """
        if self.estimatefiles == 'slow':
            count = 0
            estimate_status = {'type': 'estimating',
                               'finished': False,
                               'nfile': 0}

        cmd = self._build_cmd(borgcmd=borgcmd, args=self.args, additional_args=additional_args)
        if self.showcmd:
            print(f"Running: {cmd}")
        if self.config.encryption is not None:
            env = {'BORG_PASSPHRASE': self.config.encryption_passphrase}
        else:
            env = {}
        proc = subprocess.Popen(cmd,
                                shell=True,
                                encoding='utf-8',
                                env=env,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        for j in self._get_json(proc):
            if self.showoutput:
                print(j)
            if type(j) is not dict:
                # Non json, just print it and continue
                print(j)
                continue
            if 'rc' in j.keys():
                print('got rc', j)
            if j['type'] == 'file_status':
                if j['status'] == '-' and os.path.isfile(j['path']): # A file
                    count += 1
                    if count % status_update_count == 0:
                        estimate_status['nfiles'] = count
                        yield estimate_status
            elif j['type'] == 'archive_progress':
                yield j
            elif j['type'] == 'progress_message':
                yield j
            elif j['type'] == 'progress_percent':
                yield j
            elif j['type'] == 'log_message':
                if j['name'] == 'borg.output.list':
                    message_parts = j['message'].split(' archive: ')
                    prune_stat = message_parts[0]
                    archive_parts = message_parts[1].split('     ')
                    archive_name = archive_parts[0]
                    archive_date, archive_id = archive_parts[-1].strip().split(' [')
                    archive_id = '[' + archive_id
                    yield {'type': 'prune_message',
                           'stat': prune_stat,
                           'name': archive_name,
                           'date': archive_date,
                           'id': archive_id}
                else:
                    yield j
            else:
                yield j
        try:
            json_results = json.loads(proc.stdout.read())
        except json.decoder.JSONDecodeError:
            json_results = None

        if self.estimatefiles == 'slow':
            estimate_status['nfiles'] = count
            estimate_status['finished'] = True
            yield estimate_status
        else:
            rc = {'type': 'backup_done', 'results': json_results}
            if self.showoutput:
                print(rc)
            yield rc
        self.estimatefiles = 'none' # Turn off dryrun

    def _get_json(self, proc):
        """ Read the json returned from borg, line by line until
            a complete json line was received. Then decode the json
            to a python dict
        """
        line = ''
        while True:
            out = proc.stderr.read(1)
            if proc.poll() is not None:
                break
            if out == '\n':
                try:
                    yield json.loads(line)
                except json.decoder.JSONDecodeError:
                    yield line
                line = ""
            else:
                line += out
        if proc.returncode != 0:
            rc = {'code': proc.returncode,
                   'type': 'return_code'}
            if self.showoutput:
                print(rc)
            yield rc

    def format_bytes(self, size):
        """ Instead of requiring humanize to be installed
            use this simple bytes converter.
        """
        power = 2**10
        n = 0
        labels = {0: '',
                  1: 'K',
                  2: 'M',
                  3: 'G',
                  4: 'T'}
        while size > power:
            size /= power
            n += 1
        return f"{size:0.3f}{labels[n]}B"

    @property
    def estimatefiles(self):
        return self.__estimatefiles

    @estimatefiles.setter
    def estimatefiles(self, val):
        self.__estimatefiles = val.lower()
        if self.__estimatefiles not in ['slow', 'fast', 'none']:
            self.__estimatefiles = 'none'

    @property
    def showcmd(self):
        return self.__showcmd

    @showcmd.setter
    def showcmd(self, val):
        self.__showcmd = val

    @property
    def showoutput(self):
        return self.__showoutput

    @showoutput.setter
    def showoutput(self, val):
        self.__showoutput = val

