

class NameDefault(Exception):
    def __init__(self, iIndex):
        super(NameDefault, self).__init__(iIndex)
        self.__strMessage = 'please change position or group of "Video%d" in config file' % iIndex


class OpenFault(Exception):
    def __init__(self, strVideoName):
        super(OpenFault, self).__init__(strVideoName)
        self.__strMessage = "can't open %s video stream" % strVideoName

