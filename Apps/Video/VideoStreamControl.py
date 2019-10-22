
import configparser
import os
import cv2
import time
import datetime
import threading
from Apps.Settings.Settings import strRootPath
from Libs.MyException import NameDefault, OpenFault


class jyVideoStreamControl:
    def __init__(self, iIndex):
        self.__pConfig = configparser.ConfigParser()
        self.__pConfig.read(strRootPath + '/Apps/Config/System.ini', 'utf-8')
        self.__iIndex = iIndex
        strVideoIndex = 'Video%d' % iIndex
        strPositionLabel = 'Position'
        strPosition = 'Default'
        strGroupLabel = 'Group'
        strGroup = 'Default'
        strIPLabel = 'IP'
        strIP = '127.0.0.1'
        strPortLabel = 'Port'
        strPort = '554'
        strAdminLabel = 'Admin'
        strAdmin = 'admin'
        strPasswordLabel = 'Password'
        strPassword = 'admin123'
        strFrameRateLabel = 'FrameRate'
        iFrameRate = 0
        strCatchTickLabel = 'CatchTick'
        # 单位秒
        iCatchTick = 0
        if not self.__pConfig.has_section(strVideoIndex):
            self.__pConfig[strVideoIndex] = {
                strPositionLabel: strPosition,
                strGroupLabel: strGroup,
                strIPLabel: strIP,
                strPortLabel: strPort,
                strAdminLabel: strAdmin,
                strPasswordLabel: strPassword,
                strFrameRateLabel: iFrameRate,
                strCatchTickLabel: iCatchTick
            }

        # 记录摄像头位置
        if not self.__pConfig.has_option(strVideoIndex, strPositionLabel):
            self.__pConfig[strVideoIndex][strPositionLabel] = strPosition
        self.__strPosition = self.__pConfig[strVideoIndex][strPositionLabel]

        # 记录摄像头机组
        if not self.__pConfig.has_option(strVideoIndex, strGroupLabel):
            self.__pConfig[strVideoIndex][strGroupLabel] = strGroup
        self.__strGroup = self.__pConfig[strVideoIndex][strGroupLabel]

        # IP地址
        if not self.__pConfig.has_option(strVideoIndex, strIPLabel):
            self.__pConfig[strVideoIndex][strIPLabel] = strIP
        self.__strIP = self.__pConfig[strVideoIndex][strIPLabel]

        # 端口
        if not self.__pConfig.has_option(strVideoIndex, strPortLabel):
            self.__pConfig[strVideoIndex][strPortLabel] = strPort
        self.__strPort = self.__pConfig[strVideoIndex][strPortLabel]

        # 用户名
        if not self.__pConfig.has_option(strVideoIndex, strAdminLabel):
            self.__pConfig[strVideoIndex][strAdminLabel] = strAdmin
        self.__strAdmin = self.__pConfig[strVideoIndex][strAdminLabel]

        # 密码
        if not self.__pConfig.has_option(strVideoIndex, strPasswordLabel):
            self.__pConfig[strVideoIndex][strPasswordLabel] = strPassword
        self.__strPassword = self.__pConfig[strVideoIndex][strPasswordLabel]

        # 帧率
        if not self.__pConfig.has_option(strVideoIndex, strFrameRateLabel):
            self.__pConfig[strVideoIndex][strFrameRateLabel] = str(iFrameRate)
        self.__iFrameRate = int(self.__pConfig[strVideoIndex][strFrameRateLabel])

        # 提取间隔(秒)
        if not self.__pConfig.has_option(strVideoIndex, strCatchTickLabel):
            self.__pConfig[strVideoIndex][strCatchTickLabel] = str(iCatchTick)
        self.__iCatchTick = int(self.__pConfig[strVideoIndex][strCatchTickLabel])

        self.__iCount = self.__iCatchTick * self.__iFrameRate

        with open(strRootPath + '/Apps/Config/System.ini', 'w', encoding='utf-8') as configfile:
            self.__pConfig.write(configfile)

        # rtsp地址
        self.__strRTSPAddress = 'rtsp://%s:%s@%s:%s/h264/ch1/main/av_stream' % (self.__strAdmin,
                                                                                self.__strPassword,
                                                                                self.__strIP,
                                                                                self.__strPort)

        self.__pStream = cv2.VideoCapture()
        # 图片存放路径
        self.__strIMGPath = None
        if self.__strPosition != 'Default' and self.__strGroup != 'Default':
            self.__strIMGPath = (strRootPath + '/Apps/Resource/CatchFrame/%s/%s' % (self.__strGroup, self.__strPosition))
            if not os.path.exists(self.__strIMGPath):
                os.makedirs(self.__strIMGPath)

        self.__pThreadCatch = None

        self.__pDeamon = threading.Thread(target=jyVideoStreamControl.deamon, args=(self, ),
                                          name='Deamon: %s_%s' % (self.__strGroup, self.__strPosition))

    def deamonStart(self):
        self.__pDeamon.start()

    def deamon(self):
        while True:
            if self.__pThreadCatch is None or not self.__pThreadCatch.isAlive():
                self.__pThreadCatch = threading.Thread(target=jyVideoStreamControl.catchFrame, args=(self,),
                                                       name='%s_%s' % (self.__strGroup, self.__strPosition))
                self.__pThreadCatch.start()
            time.sleep(5)

    def catchFrame(self):
        if self.__strPosition == 'Default' or self.__strGroup == 'Default':
            raise NameDefault(self.__iIndex)

        self.__pStream.open(self.__strRTSPAddress)

        if not self.__pStream.isOpened():
            self.__pStream.release()
            raise OpenFault('%s_%s' % (self.__strGroup, self.__strPosition))

        ret, frame = self.__pStream.read()
        strLastDay = datetime.datetime.now().strftime('%Y-%m-%d')
        strFolderName = strLastDay

        if not os.path.exists(self.__strIMGPath + '/' + strFolderName):
            os.mkdir(self.__strIMGPath + '/' + strFolderName)

        while ret:
            print(self.__iIndex)
            ret, frame = self.__pStream.read()
            strDay = datetime.datetime.now().strftime('%Y-%m-%d')
            if strLastDay != strDay:
                strFolderName = strDay
                if not os.path.exists(self.__strIMGPath + '/' + strFolderName):
                    os.mkdir(self.__strIMGPath + '/' + strFolderName)

            strIMGName = datetime.datetime.now().strftime('%H_%M_%S')
            try:
                # print(self.__strIMGPath + '/' + strFolderName + '/' + strIMGName + '.jpg')
                strIMGPath = str(self.__strIMGPath + '/' + strFolderName + '/' + strIMGName + '.jpg')
                # cv2.imwrite(strIMGPath, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                cv2.imencode('.jpg', frame)[1].tofile(strIMGPath)
            except Exception as e:
                print(e)
            # 提取频率 也可以换一种定义方式
            time.sleep(self.__iCatchTick)


