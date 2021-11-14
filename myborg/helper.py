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
        if self.estimated > 0:
            hline += " | "
        print(hline)
        #f"{'File':>{self.ncsize}} |")
        hline = (f"{'File':{self.flen}} | "
                 f"{'Size':{self.fsize}} | "
                 f"{'Count':>{self.ncsize}}")
        if self.estimated > 0:
            hline += f" | {'Progress':^{self.psize}}"
        self.headerprinted = True
        print(hline)

    def format_status_line(self, line):
        sline = (f"{line['path']:{self.flen}} | "
                  f"{self.format_bytes(line['original_size']):{self.fsize}} | "
                  f"{line['nfiles']:{self.ncsize}d}")
        if self.estimated > 0:
            sline += f" | {line['nfiles'] / self.estimated:0.1%}"
        return sline

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
