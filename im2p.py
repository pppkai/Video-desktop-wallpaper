# -*- coding: utf-8 -*-

import cv2
#from threading import Thread
import win32gui
import sys, time, os, random
import screeninfo
import pywintypes

from myLog import log
from specEffects import SpecEffects

class IMProducer(object):
    def __init__(self, im_path=None, index=0):
        super(IMProducer, self).__init__()
        self.im_path = im_path
        self.window_name = 'im_frame'
        self.parent = self.pretreatmentHandle()
        self.screen = screeninfo.get_monitors()[0]
        self.frame_winid = None
        self.logger = log('in IMProducer')
        self.stopped = False
        self.effect = SpecEffects(self.im_path)
        self.index_random = index


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


    def stop(self):
        self.logger.info('in im2p stop')
        self.stopped = True
        #cv2.destroyWindow(self.window_name)
        cv2.destroyAllWindows()


    def start(self):
        print('in IMProducer run')
        if os.path.isfile(self.im_path) and not self.stopped:
            cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.moveWindow(self.window_name, self.screen.x - 1, self.screen.y - 1)
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            self.frame_winid = win32gui.FindWindow(None, self.window_name)
            win32gui.SetParent(self.frame_winid, self.parent)

            #img = cv2.imread(self.im_path)
            #img = self.effect.effectByCV2(self.index_random)
            img = self.effect.effectByPILFilter(self.index_random)

            height, width = img.shape[:2]
            width_new = self.screen.width
            height_new = self.screen.height

            # 判断图片的长宽比率
            if width / height >= width_new / height_new:
                img = cv2.resize(img, (width_new, int(height * width_new / width)))
            else:
                img = cv2.resize(img, (int(width * height_new / height), height_new))

            cv2.imshow(self.window_name, img)
            cv2.waitKey(0)


if __name__ == '__main__':
    print('run IMProducer')
    producer = IMProducer(im_path='d:\\12.jpg')
    producer.start()
