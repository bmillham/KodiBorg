class Helper(object):
    """ CLHelper
        A class for using the module from the command line
        instead of from kodi """

    def __init__(self, flen="<40.40",
                 fsize=">9.9",
                 psize="8.8",
                 ncsize="6"):
        self.flen = flen
        self.fsize = fsize
        self.psize = psize
        self.ncsize = ncsize
        self.headerprinted = False
        self.estimated = 0

    def header(self):
        if self.headerprinted:
            return
        print()
        
        hline = (f"{'Current':{self.flen}}   "
                 f"{'Total':{self.fsize}}")
        if self.estimated > 1:
            hline += " | "
        print(hline)

        hline = (f"{'File':{self.flen}} | "
                 f"{'Size':{self.fsize}} | "
                 f"{'Count':>{self.ncsize}}")
        if self.estimated > 1:
            hline += f" | {'Progress':^{self.psize}}"
        self.headerprinted = True
        print(hline)

    def format_status_line(self, line):
        sline = (f"{line['path']:{self.flen}} | "
                  f"{self.format_bytes(line['original_size']):{self.fsize}} | "
                  f"{line['nfiles']:{self.ncsize}d}")
        if self.estimated > 1:
            sline += f" | {line['nfiles'] / self.estimated:0.1%}"
        return sline

    def format_summary(self, results=None):
        if results is None:
            return ["No summary is available"]
        archive = results['archive']
        cache = results['cache']
        a_stats = archive['stats']
        c_stats = cache['stats']
        summary = [f"Archive name: {archive['name']}",
                   f"Archive fingerprint: {archive['id']}",
                   f"Time (start): {archive['start']}",
                   f"Time (end):   {archive['end']}",
                   f"Duration: {archive['duration']} seconds",
                   f"Number of files: {archive['stats']['nfiles']}",
                   f"Utilization of max. archive size: {archive['limits']['max_archive_size']:.0f}%",
                   "",
                   (f"{'':13.13} "
                    f"{'Original Size':13.13} "
                    f"{'Compressed Size':15.15} "
                    f"{'Deduplicated Size':17.17}"),
                   (f"{'This archive:':13.13} "
                    f"{self.format_bytes(a_stats['original_size']):>13.13} "
                    f"{self.format_bytes(a_stats['compressed_size']):>15.15} "
                    f"{self.format_bytes(a_stats['deduplicated_size']):>17.17}"),
                   (f"{'All archives:':13.13} "
                    f"{self.format_bytes(c_stats['total_size']):>13.13} "
                    f"{self.format_bytes(c_stats['total_csize']):>15.15} "
                    f"{self.format_bytes(c_stats['unique_size']):>17.17}"),
                   "",
                   (f"{'':13.13} "
                    f"{'Unique chunks':13.13} "
                    f"{'Total chunks':>15.15}"),
                   (f"{'Chunk index:':13.13} "
                    f"{c_stats['total_unique_chunks']:>13d} "
                    f"{c_stats['total_chunks']:>15d}")]
        return summary

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
    def headerprinted(self):
        return self._headerprinted

    @headerprinted.setter
    def headerprinted(self, val):
        self._headerprinted = val

    @property
    def estimated(self):
        return self._estimated

    @estimated.setter
    def estimated(self, val):
        self._estimated = val
