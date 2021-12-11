# -*- coding: utf-8 -*-
# 创建桌面快捷方式及反查快捷方式所指向的目录


import os
import pythoncom
from win32com.shell import shell, shellcon
import win32api
import locale

class FindLnkPath(object):
    def __init__(self):
        super(FindLnkPath, self).__init__()

    def getpathFromLink(self, lnkpath):
        shortcut = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
        shortcut.QueryInterface(pythoncom.IID_IPersistFile).Load(lnkpath)
        path = shortcut.GetPath(shell.SLGP_SHORTPATH)[0]
        return path


    def createURLShortcut(self, url, name):
        shortcut = pythoncom.CoCreateInstance(
            shell.CLSID_InternetShortcut, None,
            pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IUniformResourceLocator)
        shortcut.SetURL(url)
        if os.path.splitext(name)[-1] != '.url':
            name += '.url'
        shortcut.QueryInterface(pythoncom.IID_IPersistFile).Save(name, 0)


    def createLnkPath(self, filename, lnkname):
        shortcut = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink, None,
            pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
        shortcut.SetPath(filename)
        if os.path.splitext(lnkname)[-1] != '.lnk':
            lnkname += ".lnk"
        shortcut.QueryInterface(pythoncom.IID_IPersistFile).Save(lnkname, 0)


    def getDesktopPath(self):
        ilist = shell.SHGetSpecialFolderLocation(0, shellcon.CSIDL_DESKTOP)
        dtpath = shell.SHGetPathFromIDList(ilist)
        dtpath = dtpath.decode('gbk')
        return dtpath


    def getStartMenuPath(self):
        ilist = shell.SHGetSpecialFolderLocation(0, shellcon.CSIDL_STARTMENU)
        dtpath = shell.SHGetPathFromIDList(ilist)
        dtpath = dtpath.decode('gbk')
        return dtpath


    def findFilesByName(self, path, src_name=None):
        files = []
        for file in os.listdir(path):
            file_or_dir = os.path.join(path, file)
            if os.path.isdir(file_or_dir) and not os.path.islink(file_or_dir):
                self.findFilesByName(file_or_dir, src_name)
            elif file.find(src_name) > -1:
                files.append(file_or_dir)

        return files


if __name__ == '__main__':
    # test
    app = FindLnkPath()
    desktop = app.getDesktopPath()
    startmenu = app.getStartMenuPath()
    files = app.findFilesByName(desktop, '夜神模拟器')
    real_path0 = app.getpathFromLink(files[0])

    print('desktop :', desktop)
    print('startmenu :', startmenu)
    print('files :', files)
    print('real_path0 :', real_path0)
