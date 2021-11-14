class CLHelper(object):
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

    def header(self):
        if self.headerprinted:
            return
        print()
        print(f"{'Current':{self.flen}}   "
              f"{'Total':{self.fsize}} | "
              f"{'File':>{self.ncsize}} |")
        print(f"{'File':{self.flen}} | "
              f"{'Size':{self.fsize}} | "
              f"{'Count':>{self.ncsize}} | "
              f"{'Progress':^{self.psize}}")


    @property
    def headerprinted(self):
        return self._headerprinted

    @headerprinted.setter
    def headerprinted(self, val):
        self._headerprinted = val
