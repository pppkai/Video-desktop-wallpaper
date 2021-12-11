# -*- coding: utf-8 -*-


import os
import sys
import random
import subprocess
#from threading import Thread
from time import sleep
from PIL import Image
import winreg
import ctypes

import cv2
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QGridLayout, QPushButton, QMainWindow, QFileDialog, QLabel, QSystemTrayIcon, QAction, QMenu, QMessageBox, QInputDialog

from myLog import log
from cv2p import Producer
from im2p import IMProducer as IMGProducer
from specEffects import SpecEffects
from findLnkPath import FindLnkPath
from threads import AdDownloader, AdWorker

path_file = ''


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


class UiPWindow(QMainWindow):
    def __init__(self, parent=None):
        super(UiPWindow, self).__init__(parent)
        self.frame = []
        self.cap = []

        self.trayIcon = None
        self.tpMenu = None
        self.vdProducer = None
        self.imProducer = None
        self.index_random = 0
        self.stopped = False

        self.timer_camera = QTimer()
        #self.timer_images = QTimer()

        self.iconTray()
        self.logger = log('main')
        self.ad_url = 'https://api.zp996.com/api/v1/ads?sign=f029cedc9eab9d8d6ceaa0a70ad6678c'

        # 刷广告图
        self.ad_dir = os.path.join(os.path.dirname(sys.executable), 'downloads') \
            if getattr(sys, 'frozen', False) \
            else os.path.join(os.path.dirname(os.path.realpath(__file__)), 'downloads')
        self.flushAd = AdDownloader(self, self.ad_dir)
        self.flushAd.finished.connect(self.flushAd.deleteLater)
        self.flushAd.start()

        self.switch = AdWorker(self)
        self.switch.finished.connect(self.switch.deleteLater)
        self.switch.start()

        # 特效处理
        self.effect = SpecEffects()


    def setupUi(self, mWindow):
        mWindow.setObjectName("PDesktop")
        mWindow.resize(505, 595)
        mWindow.setFixedSize(505, 595)
        mWindow.setMinimumSize(QtCore.QSize(505, 595))
        mWindow.setMaximumSize(QtCore.QSize(505, 595))
        mWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)

        self.centralwidget = QtWidgets.QWidget(mWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(22, 10, 89, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.openmp4)
        self.pushButton.setStyleSheet('''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')

        self.pushButtonImage = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonImage.setGeometry(QtCore.QRect(121, 10, 89, 31))
        self.pushButtonImage.setObjectName("pushButtonImg")
        self.pushButtonImage.clicked.connect(self.openimage)
        self.pushButtonImage.setStyleSheet('''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')

        self.pushButtonWeixin = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonWeixin.setGeometry(QtCore.QRect(220, 10, 89, 31))
        self.pushButtonWeixin.setObjectName("pushButtonWeixin")
        self.pushButtonWeixin.clicked.connect(self.get_choice_wx)
        self.pushButtonWeixin.setStyleSheet('''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')

        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(22, 50, 452, 320))
        self.groupBox.setObjectName("groupBox")
        self.widget = QtWidgets.QWidget(self.groupBox)
        self.widget.setGeometry(QtCore.QRect(11, 20, 432, 290))
        self.widget.setObjectName("widget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label = QLabel(self)
        self.label.resize(400, 290)
        self.label.setText("Waiting for select...")
        self.gridLayout_3.addWidget(self.label)

        self.close_widget = QtWidgets.QWidget(self.centralwidget)
        self.close_widget.setGeometry(QtCore.QRect(420, 0, 93, 41))
        self.close_widget.setObjectName("close_widget")

        self.close_layout = QGridLayout()  # 创建左侧部件的网格布局层
        self.close_widget.setLayout(self.close_layout)  # 设置左侧部件布局为网格

        self.left_close = QPushButton("")  # 关闭按钮
        self.left_close.clicked.connect(self.close)
        #self.left_visit = QPushButton("")  # 空白按钮
        # self.left_visit.clicked.connect(myWindow.big)
        self.left_mini = QPushButton("")  # 最小化按钮
        self.left_mini.clicked.connect(myWindow.mini)

        self.close_layout.addWidget(self.left_mini, 0, 1, 1, 1)
        self.close_layout.addWidget(self.left_close, 0, 2, 1, 1)
        #self.close_layout.addWidget(self.left_visit, 0, 0, 1, 1)

        self.left_close.setFixedSize(15, 15)  # 设置关闭按钮的大小
        #self.left_visit.setFixedSize(15, 15)  # 设置按钮大小
        self.left_mini.setFixedSize(15, 15)  # 设置最小化按钮大小
        self.left_close.setStyleSheet('''QPushButton{background:#F76677;border-radius:5px;}QPushButton:hover{background:red;}''')
        #self.left_visit.setStyleSheet('''QPushButton{background:#F7D674;border-radius:5px;}QPushButton:hover{background:yellow;}''')
        self.left_mini.setStyleSheet('''QPushButton{background:#6DDF6D;border-radius:5px;}QPushButton:hover{background:green;}''')

        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(77, 380, 100, 41))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.play)
        self.pushButton_2.setStyleSheet('''QPushButton{background:#6DDF6D;border-radius:5px;}QPushButton:hover{background:green;}''')
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(308, 380, 100, 41))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.close_wall)
        self.pushButton_3.setStyleSheet('''QPushButton{background:#F76677;border-radius:5px;}QPushButton:hover{background:red;}''')

        self.groupBoxAd = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBoxAd.setGeometry(QtCore.QRect(22, 431, 452, 120))
        self.groupBoxAd.setObjectName("groupBoxAd")
        self.gridLayoutAd = QtWidgets.QGridLayout(self.groupBoxAd)
        self.gridLayoutAd.setObjectName("gridLayoutAd")
        self.labelAd = QLabel(self.groupBoxAd)
        self.labelAd.resize(430, 100)
        self.labelAd.setText("loading...")
        self.gridLayoutAd.addWidget(self.labelAd)

        myWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(myWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 505, 23))
        self.menubar.setObjectName("menubar")
        myWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(myWindow)
        self.statusbar.setObjectName("statusbar")
        myWindow.setStatusBar(self.statusbar)

        self.retranslateUi(myWindow)
        QtCore.QMetaObject.connectSlotsByName(myWindow)

        #
        self.centralwidget.setStyleSheet('''
             QWidget#centralwidget{
                 color:#F7D674;
                 background:#4169E1;
                 border-top:1px solid #4169E1;
                 border-bottom:1px solid #4169E1;
                 border-right:1px solid #4169E1;
                 border-left:1px solid #4169E1;
                 border-top-left-radius:10px;
                 border-top-right-radius:10px;
                 border-bottom-left-radius:10px;
                 border-bottom-right-radius:10px;
             }    
        ''')
        self.groupBox.setStyleSheet('''color:#F7D674''')
        self.groupBoxAd.setStyleSheet('''border:1px solid #d8d9d9;border-radius:5px;''')

        myWindow.setWindowOpacity(0.95)  # 设置窗口透明度
        myWindow.setAttribute(Qt.WA_TranslucentBackground)
        myWindow.setWindowFlag(Qt.FramelessWindowHint)  # 隐藏边框


    # 弹出输入框
    def get_choice_wx(self):
        items = (str(i) for i in range(2, 10))
        item, ok = QInputDialog.getItem(self, u"微信多开", u"数量:", items, 0, False)
        if ok and item:
            #CREATE_NO_WINDOW = 0x08000000
            #DETACHED_PROCESS = 0x00000008
            #si = subprocess.STARTUPINFO()
            #si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # si.wShowWindow = subprocess.SW_HIDE # default
            # creationflags=CREATE_NO_WINDOW startupinfo=si
            try:
                subprocess.call('taskkill /F /IM WeChat.exe')
            except: pass

            try:
                # reg table search
                reg_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion"
                key = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, reg_path)
                ProgramFilesDir_x86 = winreg.QueryValueEx(key, 'ProgramFilesDir (x86)')
                ProgramFilesDir = winreg.QueryValueEx(key, 'ProgramFilesDir')

                cmd_path_x86 = os.path.join(ProgramFilesDir_x86[0] if len(ProgramFilesDir_x86) > 0 else '', 'Tencent\\WeChat')
                cmd_path_no = os.path.join(ProgramFilesDir[0] if len(ProgramFilesDir) > 0 else '', 'Tencent\\WeChat')
                if os.path.exists(cmd_path_x86):
                    cmd_path = cmd_path_x86
                elif os.path.exists(cmd_path_no):
                    cmd_path = cmd_path_no
                else:
                    # 查找桌面快捷方式
                    cmd_path = None
                    search_wx = FindLnkPath()
                    desktop = search_wx.getDesktopPath()
                    files = app.findFilesByName(desktop, '微信')
                    self.logger.info('getDesktopPath %s' % files)

                    # 开始菜单
                    if not len(files):
                        startmenu = app.getStartMenuPath()
                        files = app.findFilesByName(startmenu, '微信')
                        self.logger.info('getStartMenuPath %s' % files)

                    if len(files) > 0:
                        wx_lnk_path = app.getpathFromLink(files[0])
                        if wx_lnk_path:
                            cmd_path_tmp = os.path.join(os.path.dirname(wx_lnk_path), 'WeChat.exe')
                            if os.path.exists(cmd_path_tmp):
                                cmd_path = cmd_path_tmp

                    if not cmd_path:
                        QtWidgets.QMessageBox.question(self, '提示', "多开了个寂寞, PC版微信都没有安装呢", QtWidgets.QMessageBox.Yes)
                        return

                #cmd_str = ['WeChat.exe'] * int(item)
                #print('get_choice_wx start %s ' % ('&'.join(cmd_str)))
                #os.system('start /d "%s"' % cmd_path)

                # 改成写脚本执行
                bat_file = os.path.join(cmd_path, "WeChatStart.bat")
                with open(bat_file, 'w', encoding='gbk') as f:
                    f.write("{}\n".format('@echo off'))
                    f.write("{}\n".format('cd /d "%~d0"'))
                    f.write("{}\n".format('cd "%~dp0"'))
                    for t in ['WeChat.exe'] * int(item):
                        f.write("{}\n".format('start %s' % t))

                # 执行bat
                os.system('start "" /d "%s" WeChatStart.bat' % cmd_path)
            except:
                QtWidgets.QMessageBox.question(self, '提示', "多开失败，小蓝真的尽力了", QtWidgets.QMessageBox.Yes)
        return


    def iconTray(self):
        self.tpMenu = QMenu(myWindow)
        self.tpMenu.addAction(QAction('主界面', myWindow, triggered=myWindow.show))
        self.tpMenu.addAction(QAction('关闭', myWindow, triggered=self.close_wall))
        self.tpMenu.addAction(QAction('退出', myWindow, triggered=self.quitApp))

        self.trayIcon = QSystemTrayIcon(QIcon('./p.ico'), myWindow)
        #self.trayIcon.setIcon(QIcon('./p.ico'))
        self.trayIcon.setContextMenu(self.tpMenu)
        self.trayIcon.show()

        self.trayIcon.messageClicked.connect(self.message)
        self.trayIcon.activated.connect(self.act)


    def message(self):
        print("弹出的信息被点击了")


    def act(self, reason):
        if reason == 2 or reason == 3:
            myWindow.show()


    def quitApp(self):
        self.logger.info('main quitApp')
        if self.vdProducer:
            self.vdProducer.stop()
            self.vdProducer = None

        if self.imProducer:
            self.imProducer.stop()
            self.imProducer = None

        try:
            # 结束线程
            if self.flushAd and self.flushAd.isRunnig():
                self.flushAd.terminate()

            if self.switch and self.switch.isRunnig():
                self.switch.terminate()

            if self.vdProducer and self.vdProducer.isRunnig():
                self.vdProducer.terminate()
        except:
            pass

        sleep(1)
        sys.exit()


    def retranslateUi(self, mWindow):
        _translate = QtCore.QCoreApplication.translate
        mWindow.setWindowTitle(_translate("PDesktop", "PDesktop"))
        self.pushButton.setText(_translate("PDesktop", "选择视频"))

        self.pushButtonImage.setText(_translate("PDesktop", "选择图片"))
        self.pushButtonWeixin.setText(_translate("PDesktop", "微信多开"))

        self.groupBox.setTitle(_translate("PDesktop", "预览"))
        self.pushButton_2.setText(_translate("PDesktop", "应用"))
        self.pushButton_3.setText(_translate("PDesktop", "关闭"))


    def openmp4(self):
        try:
            global path_file
            path_file, filetype = QFileDialog.getOpenFileName(None, "选择视频文件", '.', "视频文件(*.AVI;*.mov;*.rmvb;*.rm;*.FLV;*.mp4;*.3GP;*.ts)")  # ;;All Files (*)
            if path_file == "":  # 未选择文件
                return

            self.stopped = False
            self.slotStart()

            #t = Thread(target=self.Stop)
            #t.start()
        except Exception as e:
            print (e)


    def openimage(self):
        try:
            global path_file
            path_file, filetype = QFileDialog.getOpenFileName(None, "选择图片文件", '.', "图片文件(*.jpg;*.JPG;*.png;*.jpeg;*.JPEG;*.PNG)")  # ;;All Files (*)
            if path_file == "":  # 未选择文件
                return

            self.slotImageStart()
        except Exception as e:
            print (e)


    def slotImageStart(self):
        global path_file
        img_name = path_file
        self.logger.info(' slotImageStart img_name:' + img_name)
        self.logger.info(' slotImageStart type(img_name): %s ' % type(img_name))

        if img_name != "":  # “”为用户取消
            # 重新关联方法
            self.pushButton_2.disconnect()
            self.pushButton_3.disconnect()
            self.pushButton_2.clicked.connect(self.play_im)
            self.pushButton_3.clicked.connect(self.close_im_wall)

            # 关闭视频预览
            if self.cap:
                self.cap.release()
                self.timer_camera.stop()  # 停止计时器

            # 读取图像
            self.index_random = random.randint(0, 9)
            #img = self.effect.effectByCV2(self.index_random, img_name)
            img = self.effect.effectByPILFilter(self.index_random, img_name)

            self.logger.info(' slotImageStart type(img): %s ' % type(img))

            """
            if self.index_random > 9:
                img = self.effect.effectByCV2(self.index_random, img_name)
            elif random.randint(0, 1) is 0:
                img = self.effect.effectByPILFilter(self.index_random, img_name)
            else:
                img = self.effect.effectByCV2(self.index_random, img_name)
            """

            img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # opencv读取的bgr格式图片转换成rgb格式
            im_image = QtGui.QImage(img2[:], img2.shape[1], img2.shape[0], img2.shape[1] * 3, QtGui.QImage.Format_RGB888)
            self.label.setPixmap(QtGui.QPixmap(im_image).scaled(self.label.width(), self.label.height()))  # 设置图片显示


    def close_im_wall(self):
        if self.imProducer:
            self.imProducer.stop()
            self.imProducer = None


    def slotStart(self):
        global path_file
        """ Slot function to start the progamme """
        videoName = path_file
        self.logger.info(' slotStart videoName:' + videoName)
        self.logger.info(' slotStart type(videoName): %s ' % type(videoName))

        # 重新关联方法
        self.pushButton_2.disconnect()
        self.pushButton_3.disconnect()
        self.pushButton_2.clicked.connect(self.play)
        self.pushButton_3.clicked.connect(self.close_wall)

        if videoName != "":  # ""为用户取消
            self.cap = cv2.VideoCapture(videoName)
            self.logger.info(' cv2.VideoCapture(videoName): %s ' % type(self.cap))
            self.timer_camera.start(40)
            self.logger.info(' self.timer_camera.start: %s ' % type(self.timer_camera))
            self.timer_camera.timeout.connect(self.openFrame)


    def openFrame(self):
        """ Slot function to capture frame and process it  """
        self.logger.info('openFrame self.cap.isOpened(): %s ' % self.cap.isOpened())
        self.logger.info('openFrame self.stopped: %s ' % self.stopped)
        if self.cap.isOpened() and not self.stopped:
            ret, self.frame = self.cap.read()
            self.logger.info('openFrame ret: %s ' % ret)

            if ret:
                frame_image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                height, width, bytesPerComponent = frame_image.shape
                bytesPerLine = bytesPerComponent * width
                q_image = QImage(frame_image.data, width, height, bytesPerLine, QImage.Format_RGB888).scaled(self.label.width(), self.label.height())
                self.label.setPixmap(QPixmap.fromImage(q_image))
            else:
                self.cap.release()
                self.timer_camera.stop()  # 停止计时器
        elif self.stopped and self.timer_camera:
            self.timer_camera.stop()


    def play_im(self):
        global path_file
        if path_file == '':
            QtWidgets.QMessageBox.question(self, '提示', "你选了个寂寞", QtWidgets.QMessageBox.Yes)
            return

        # 关闭视频层
        print('vdProducer %s' % type(self.vdProducer))

        if self.vdProducer:
            self.close_wall()

        # 关闭图片层
        if self.imProducer:
            self.close_im_wall()

        # 打开图片层
        self.imProducer = IMGProducer(path_file, self.index_random)
        self.imProducer.start()


    def play(self):
        global path_file
        if path_file == '':
            QtWidgets.QMessageBox.question(self, '提示', "你选了个寂寞", QtWidgets.QMessageBox.Yes)
            return

        # 关闭视频预览
        self.stopped = True
        if self.cap:
            self.cap.release()
            self.timer_camera.stop()  # 停止计时器

        # 关闭视频层
        if self.vdProducer:
            self.close_wall()

        # 关闭图片层
        if self.imProducer:
            self.close_im_wall()

        self.vdProducer = Producer(path_file)
        self.vdProducer.start()


    def close_wall(self):
        self.vdProducer.stop()


    def close(self):
        if myWindow:
            myWindow.hide()
            self.trayIcon.showMessage('动态桌面', '程序已经最小化到系统托盘', QIcon('./p.ico'))
            self.logger.info('MainWindow is close!')


class MainWindow(QMainWindow):
    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(
            self,
            '提示',
            "是否要退出程序？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        global big
        big = False
        self.setWindowState(Qt.WindowNoState)
        self.m_flag = True
        self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
        event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        global big
        big = False
        self.setWindowState(Qt.WindowNoState)
        self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
        QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        global big
        big = False
        self.setWindowState(Qt.WindowNoState)
        self.m_flag = False

    def mousePressEvent(self, event):
        global big
        big = False
        self.setWindowState(Qt.WindowNoState)
        self.m_flag = True
        self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
        event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        global big
        big = False
        self.setWindowState(Qt.WindowNoState)
        self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
        QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        global big
        big = False
        self.setWindowState(Qt.WindowNoState)
        self.m_flag = False

    def big(self):
        global big
        print('最大化：{}'.format(big))
        if not big:
            self.setWindowState(Qt.WindowMaximized)
            big = True
        elif big:
            self.setWindowState(Qt.WindowNoState)
            big = False

    def mini(self):
        self.showMinimized()


if __name__ == "__main__":
    # 授权申请
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, sys.executable if getattr(sys, 'frozen', False) else __file__, None, 1)
        sys.exit(0)

    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    path_ico = os.path.join(os.path.dirname(sys.executable), 'p.ico') \
                if getattr(sys, 'frozen', False) \
                else os.path.join(os.path.dirname(os.path.realpath(__file__)), 'p.ico')
    app.setWindowIcon(QIcon(path_ico))

    myWindow = MainWindow()
    ui = UiPWindow()
    ui.setupUi(myWindow)

    # 显示广告图片
    """
    img_file = os.path.join(os.path.dirname(sys.executable), 'res\\default_ad.jpg') \
                if getattr(sys, 'frozen', False) \
                else os.path.join(os.path.dirname(os.path.realpath(__file__)), 'res\\default_ad.jpg')
    """

    myWindow.show()
    sys.exit(app.exec_())
