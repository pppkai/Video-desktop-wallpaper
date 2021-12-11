# -*- coding: utf-8 -*-

import cv2
#from threading import Thread
from PyQt5.QtCore import QThread
import win32gui
import sys, time, os
import screeninfo
import pywintypes

from myLog import log


class Producer(QThread):
    """ docstring for ClassName """
    def __init__(self, str_video, stopevt=None):
        super(Producer, self).__init__()
        self.str_video = str_video
        self.stopevt = stopevt
        self.cap = None
        self.window_name = 'frame'
        self.parent = self.pretreatmentHandle()
        self.screen = screeninfo.get_monitors()[0]
        self.frame_winid = None
        self.logger = log('in producer')
        self.rename = None
        self.stopped = False


    def pretreatmentHandle(self):
        ret_hwnd = None
        hwnd = win32gui.FindWindow("Progman", "Program Manager")
        win32gui.SendMessageTimeout(hwnd, 0x052C, 0, None, 0, 0x03E8)
        hwnd_WorkW = None
        while 1:
            hwnd_WorkW = win32gui.FindWindowEx(None, hwnd_WorkW, "WorkerW", None)
            # print('hwmd_workw: ', hwnd_WorkW)
            if not hwnd_WorkW:
                continue
            ret_hwnd = hwnd_WorkW

            hView = win32gui.FindWindowEx(hwnd_WorkW, None, "SHELLDLL_DefView", None)
            # print('hwmd_hView: ', hView)
            if not hView:
                continue
            ret_hwnd = hView

            hViewv = win32gui.FindWindowEx(None, hwnd_WorkW, "WorkerW", None)
            # print('hViewv: ', hViewv)
            while hViewv:
                win32gui.SendMessage(hViewv, 0x0010, 0, 0)  # WM_CLOSE
                hViewv = win32gui.FindWindowEx(None, hwnd_WorkW, "WorkerW", None)
                # print(hViewv)

            if hViewv:
                ret_hwnd = hViewv

            break

        return hwnd


    def cv_video_capture(self, file_path):
        root_dir, file_name = os.path.split(file_path)
        pwd = os.getcwd()
        if root_dir:
            os.chdir(root_dir)
        cv_img = cv2.VideoCapture(file_name)
        os.chdir(pwd)
        return cv_img


    def setFilePath(self, path_file=None):
        self.str_video = path_file
        time.sleep(1)
        self.stopped = False
        self.logger.info('cv2p setFilePath %s' % self.str_video)


    def stop(self):
        self.logger.info('cv2p stop')
        self.stopped = True
        time.sleep(1)
        if self.cap:
            self.cap.release()

        try:
            #cv2.destroyWindow(self.window_name)
            cv2.destroyAllWindows()
        except Exception as e:
            print("窗口已关闭 %s" % e)


    #def start(self, file_name=None):
    def run(self, file_name=None):
        print('producer run')
        self.frame_winid = win32gui.FindWindow(None, self.window_name)
        cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
        cv2.moveWindow(self.window_name, self.screen.x - 1, self.screen.y - 1)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        self.frame_winid = win32gui.FindWindow(None, self.window_name)
        win32gui.SetParent(self.frame_winid, self.parent)
        print('producer stopped: %s' % self.stopped)

        self.stopped = False
        while not self.stopped:
            #if self.cap is None:
            ret = True
            self.logger.info('cv2.VideoCapture str_video ' + (file_name if file_name else self.str_video))
            try:
                self.cap = cv2.VideoCapture(file_name if file_name else self.str_video)
                #self.cap = self.cv_video_capture(self.str_video)
                self.logger.info('self.cap %s' % self.cap)

                while self.cap and ret:
                    ret, frame = self.cap.read()
                    self.logger.info('self.cap.read ret %s' % ret)

                    if ret:
                        cv2.imshow(self.window_name, frame)
                        if cv2.waitKey(30) & 0xFF == ord('q'):
                            break

                    time.sleep(0.01)

                if self.cap:
                    self.cap.release()
                    self.cap = None
            except Exception as e:
                print("打开视频出错: %s " % e)
                self.logger.info("打开视频出错: %s " % e)

                """
                if self.rename:
                    root_dir, file_name = os.path.split(self.str_video)
                    if os.path.exists(os.path.join(root_dir, self.rename)):
                        os.rename(os.path.join(root_dir, self.rename), self.str_video)
                        self.logger.info("还原文件名0: %s -> %s" % (self.rename, file_name))
                        """

            time.sleep(0.001)

        #cv2.destroyAllWindows()
        print('producer thread is stopped! %s' % self.stopped)

    """
    def __del__(self):
        
        if self.rename:
            root_dir, file_name = os.path.split(self.str_video)
            if os.path.exists(os.path.join(root_dir, self.rename)):
                os.rename(os.path.join(root_dir, self.rename), self.str_video)
                self.logger.info("还原文件名1: %s -> %s" % (self.rename, file_name))
                """


if __name__ == '__main__':
    print('run program')
    logger = log('producer')

    if os.path.exists("./filename.txt"):
        with open("./filename.txt", 'r', encoding='gbk') as f:
            file_name = f.read()
            logger.info('type(file_name) %s' % type(file_name))

            #print('file_name1', file_name)
            #file_name = file_name.encode('utf-8').decode("unicode_escape")
            logger.info('file_name1 ' + file_name)

            if file_name == '':
                file_name = './video/b.ts'

        print('file_name', file_name)
        logger.info('file_name ' + file_name)

    if not os.path.exists(file_name):
        print('not file_name:', file_name)
        logger.info('not file_name: ' + file_name)
        sys.exit()

    producer = Producer(file_name)
    producer.start()
