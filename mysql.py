#!/usr/bin/python3

# mysqldump is required for this script to work.
# sudo apt install mysql-client-core
#  OR
# sudo apt install mariadb-client

from shutil import which
from myborg.myborg import MyBorg
from myborg.helper import Helper

helper = Helper()

dump = which('mysqldump')
if dump is None:
    print("ERROR: mysqldump not installed")
    exit(1)

# A little crude right now, to backup databases you need to supply the
# path to the kodi advancedsettings.xml. Only mysql databases can be
# backed up. video and music databases are backed up in different 'files'

borg = MyBorg(advanced_file="/home/brian/.kodi/userdata/advancedsettings.xml")
borg.showcmd=True

print("Backing up databases")
for db in [borg.videodatabase, borg.musicdatabase]:
    flen="<40.40"
    fsize=">9.9"
    psize="8.8"
    ncsize="6"
    helper.headerprinted = False
    helper.estimated = 0
    saved_lines = []
    progress_status = {}

    for i in db():
        if i['type'] == 'progress_percent':
            if i['msgid'] not in progress_status:
                print()
                progress_status[i['msgid']] = i['finished']
            if i['finished']:
                print(f"Completed: {i['msgid']}")
            else:
                print(f"{i['message']}")
        elif i['type'] == 'log_message':
            print(f"{i['message']}")
            if i['msgid'] == "Repository.DoesNotExist":
                print("Please run do-borg-init.py to create the borg repository!")
                break
        elif i['type'] == 'progress_message':
            if i['msgid'] not in progress_status:
                progress_status[i['msgid']] = i['finished']
                if i['msgid'] == 'cache.begin_transaction':
                    print(f"{i['message']}")
            else:
                if i['finished']:
                    progress_status[i['msgid']] = True
                    if i['msgid'] == 'cache.begin_transaction':
                        print(f"Cache initialized")
                        if not helper.headerprinted:
                            helper.header()
                            helper.headerprinted = True
                            for l in saved_lines:
                                print(l, end="\r", flush=True)
                else:
                    print(f"{i['message']}")

        elif i['type'] == 'backup_done':
            results = i['results']
            if results is None:
                print("Backup failed")
                continue
            archive = results['archive']
            cache = results['cache']
            print(f"\nArchive name: {archive['name']}")
            print(f"Archive fingerprint: {archive['id']}")
            print(f"Time (start): {archive['start']}")
            print(f"Time (end):   {archive['end']}")
            print(f"Duration: {archive['duration']} seconds")
            print(f"Number of files: {archive['stats']['nfiles']}")
            print(f"Utilization of max. archive size: {archive['limits']['max_archive_size']:.0f}%")
            print()
            a_stats = archive['stats']
            c_stats = cache['stats']
            print(f"{'':13.13} "
                  f"{'Original Size':13.13} "
                  f"{'Compressed Size':15.15} "
                  f"{'Deduplicated Size':17.17}")
            print(f"{'This archive:':13.13} "
                  f"{borg.format_bytes(a_stats['original_size']):>13.13} "
                  f"{borg.format_bytes(a_stats['compressed_size']):>15.15} "
                  f"{borg.format_bytes(a_stats['deduplicated_size']):>17.17}")
            print(f"{'All archives:':13.13} "
                  f"{borg.format_bytes(c_stats['total_size']):>13.13} "
                  f"{borg.format_bytes(c_stats['total_csize']):>15.15} "
                  f"{borg.format_bytes(c_stats['unique_size']):>17.17}")
            print()
            print(f"{'':13.13} "
                  f"{'Unique chunks':13.13} "
                  f"{'Total chunks':>15.15}")
            print(f"{'Chunk index:':13.13} "
                  f"{c_stats['total_unique_chunks']:>13d} "
                  f"{c_stats['total_chunks']:>15d}")
        else:
            if i['type'] == 'return_code':
                if i['code'] != 0:
                    print(f"The backup was aborted ({i['code']})")
                    exit(i['code'])
                else:
                    continue
            if i['path'] == '':
                continue
            line = helper.format_status_line(i)
            # borg returns backup status before actually starting
            # the backup. Save the lines until the cache init is done, then
            # Show them.
            if not helper.headerprinted:
                saved_lines.append(line)
            else:
                print(line, end="\r", flush=True)
