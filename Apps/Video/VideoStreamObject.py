
import os
import configparser
from Apps.Settings.Settings import strRootPath
from Apps.Video.VideoStreamControl import jyVideoStreamControl


class jyVideoStreamObject:
    def __init__(self):
        self.__pConfig = configparser.ConfigParser()
        self.__strPath = strRootPath + '/Apps/Config/'
        self.__pConfig.read(self.__strPath + 'System.ini', 'utf-8')
        if not os.path.exists(self.__strPath):
            os.mkdir(self.__strPath)

        if not self.__pConfig.has_section('System'):
            self.__pConfig['System'] = {
                'VideoNum': 0
            }
        self.__iVideoNum = int(self.__pConfig['System']['VideoNum'])

        with open(self.__strPath + 'System.ini', 'w', encoding='utf-8') as configfile:
            self.__pConfig.write(configfile)

        strImageRootPath = strRootPath + '/Apps/Resource/CatchFrame'
        if not os.path.exists(strImageRootPath):
            os.mkdir(strImageRootPath)

        self.__listVideoControl = []
        for i in range(self.__iVideoNum):
            pVideoStream = jyVideoStreamControl(i)
            self.__listVideoControl.append(pVideoStream)
            pVideoStream.deamonStart()


