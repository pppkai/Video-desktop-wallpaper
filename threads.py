# -*- coding: utf-8 -*-


import cv2
import json
import os
import sys
import requests
from shutil import copyfile
from PyQt5 import QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from time import sleep
import numpy as np


# 广告图片下载
class AdDownloader(QThread):
    sig = pyqtSignal(str)
    def __init__(self, parent=None, folder='download'):
        super(AdDownloader, self).__init__(parent)
        self.parent = parent
        self.folder = folder

    def run(self):
        try:
            response = requests.get(self.parent.ad_url, timeout=(1, 5))
            data = json.loads(response.text)

            if not data.get('data'):
                return None

            if not os.path.exists(self.folder):
                os.makedirs(self.folder)
            else:
                # clear old files
                [os.remove(os.path.join(root, name)) for root, dirs, files in os.walk(self.folder, topdown=False)
                 for name in files if os.path.isfile(os.path.join(root, name))]

            for a in data['data']:
                filename = os.path.basename(a['pic'])
                pic_file = os.path.join(self.folder, filename)
                response = requests.get(a['pic'])
                with open(pic_file, 'wb') as file:
                    file.write(response.content)
        except Exception as e:
            print("Ad Down Exception: %s " % e)

            if not os.path.exists(self.folder):
                os.makedirs(self.folder)

            # 写一张默认广告图到目录
            source = './res/default_ad.jpg'
            filename = os.path.basename(source)
            pic_file = os.path.join(self.folder, filename)

            try:
                copyfile(source, pic_file)
            except:
                print("Unexpected error:", sys.exc_info())
                Image.open(source)
                Image.save(pic_file)


# 广告轮换
class AdWorker(QThread):
    sig = pyqtSignal(str)
    def __init__(self, parent=None):
        super(AdWorker, self).__init__(parent)
        self.parent = parent

    # 取广告图片
    def get_files(self):
        if not os.path.exists(self.parent.ad_dir):
            os.makedirs(self.parent.ad_dir)

            # 写一张默认广告图到目录
            source = './res/default_ad.jpg'
            filename = os.path.basename(source)
            pic_file = os.path.join(self.parent.ad_dir, filename)

            try:
                copyfile(source, pic_file)
            except:
                print("Unexpected error on copyfile:", sys.exc_info())
                Image.open(source)
                Image.save(pic_file)

        files = os.listdir(self.parent.ad_dir)
        for x in files:
            if not (x.endswith('.jpg') or x.endswith('.JPG') or x.endswith('.png')):
                files.remove(x)
        return files

    def run(self):
        files = self.get_files()
        while True:
            for name in files:
                file_name = os.path.join(self.parent.ad_dir, name)
                if os.path.exists(file_name):
                    img2 = cv2.imdecode(np.fromfile(file_name, dtype=np.uint8), cv2.IMREAD_COLOR)
                    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
                    tc_image = QtGui.QImage(img2[:], img2.shape[1], img2.shape[0], img2.shape[1] * 3,
                                          QtGui.QImage.Format_RGB888)
                    jpg_out = QtGui.QPixmap(tc_image).scaled(self.parent.labelAd.width(), self.parent.labelAd.height())
                    self.parent.labelAd.setPixmap(jpg_out)
                    sleep(10)
            sleep(0.001)

