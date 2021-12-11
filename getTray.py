# -*- coding: utf-8 -*-

import win32api, win32gui
import win32con, winerror
import sys, os
import commctrl
from ctypes import *
import time

# represent the TBBUTTON structure
# note this is 32 bit, 64 bit padds 4 more reserved bytes
class TBBUTTON(Structure):
    _pack_ = 1
    _fields_ = [
        ('iBitmap', c_int),
        ('idCommand', c_int),
        ('fsState', c_ubyte),
        ('fsStyle', c_ubyte),
        ('bReserved', c_ubyte * 2),
        ('dwData', c_ulong),
        ('iString', c_int),
    ]


class RECT(Structure):
    _pack_ = 1
    _fields_ = [
        ('left', c_ulong),
        ('top', c_ulong),
        ('right', c_ulong),
        ('bottom', c_ulong),
    ]



# get the handle to the sytem tray
hWnd = windll.user32.FindWindowA("Shell_TrayWnd", None)
hWnd = windll.user32.FindWindowExA(hWnd, None, "TrayNotifyWnd", None)
hWnd = windll.user32.FindWindowExA(hWnd, None, "SysPager", None)
hWnd = windll.user32.FindWindowExA(hWnd, None, "ToolbarWindow32", None)

# get the count of icons in the tray
numIcons = windll.user32.SendMessageA(hWnd, commctrl.TB_BUTTONCOUNT, 0, 0)
print(numIcons)

# allocate memory within the system tray
pid = c_ulong()
windll.user32.GetWindowThreadProcessId(hWnd, byref(pid))
hProcess = windll.kernel32.OpenProcess(win32con.PROCESS_ALL_ACCESS, 0, pid)
lpPointer = windll.kernel32.VirtualAllocEx(hProcess, 0, sizeof(TBBUTTON), win32con.MEM_COMMIT, win32con.PAGE_READWRITE)

# rProcess = windll.kernel32.OpenProcess(win32con.PROCESS_ALL_ACCESS, 0, pid)
rlpPointer = windll.kernel32.VirtualAllocEx(hProcess, 0, sizeof(RECT), win32con.MEM_COMMIT, win32con.PAGE_READWRITE)

# init our tool bar button and a handle to it
tbButton = TBBUTTON()
butHandle = c_int()
foxmail_rect = RECT()


for i in range(numIcons):
    # query the button into the memory we allocated
    windll.user32.SendMessageA(hWnd, commctrl.TB_GETBUTTON, i, lpPointer)
    # read the memory into our button struct
    windll.kernel32.ReadProcessMemory(hProcess, lpPointer, addressof(tbButton), 20, None)
    # read the 1st 4 bytes from the dwData into the butHandle var
    # these first 4 bytes contain the handle to the button
    windll.kernel32.ReadProcessMemory(hProcess, tbButton.dwData, addressof(butHandle), 4, None)

    # get the pid that created the button
    butPid = c_ulong()
    windll.user32.GetWindowThreadProcessId(butHandle, byref(butPid))
    #

    #     print hex(win32gui.GetParent(hWnd))
    wszBuff = create_unicode_buffer(win32con.MAX_PATH)
    windll.kernel32.ReadProcessMemory(hProcess, tbButton.iString, wszBuff, win32con.MAX_PATH, None)
    print(wszBuff.value, '  ---  ', tbButton.idCommand)

    #     if True:
    #         print wszBuff.value
    #         print tbButton.idCommand

    #         idCommand = c_int()
    #         windll.kernel32.ReadProcessMemory(hProcess, tbButton.idCommand, idCommand, sizeof(int), 0)
    #         PostMessage(GetParent(hwndTB), WM_COMMAND, idCommand, (LPARAM)hwndTB);
    #         print idCommand
    #         win32gui.SendMessage(win32gui.GetParent(hWnd), win32con.WM_COMMAND, tbButton.idCommand, hWnd)
    #         time.sleep(2)
    #         win32gui.SendMessage(win32gui.GetParent(hWnd), win32con.WM_COMMAND, tbButton.idCommand, hWnd)

    #         win32api.PostMessage(hWnd,win32con.WM_LBUTTONDOWN,win32con.MK_MBUTTON,0)
    #         win32api.PostMessage(hWnd,win32con.WM_LBUTTONUP,tbButton.idCommand,0)
    #         win32api.PostMessage(hWnd,win32con.WM_LBUTTONDOWN,tbButton.idCommand,0)
    #         win32api.PostMessage(hWnd,win32con.WM_LBUTTONUP,tbButton.idCommand,0)

    #         win32api.SendMessage(hWnd, commctrl.TB_PRESSBUTTON, tbButton.idCommand, True)
    #         win32api.PostMessage(hWnd,commctrl.TB_PRESSBUTTON,tbButton.idCommand,0)

    win32api.SendMessage(hWnd, commctrl.TB_GETRECT, tbButton.idCommand, rlpPointer)
    windll.kernel32.ReadProcessMemory(hProcess, rlpPointer, addressof(foxmail_rect), sizeof(foxmail_rect), None)
    xpos = int((foxmail_rect.right - foxmail_rect.left) / 2) + foxmail_rect.left
    ypos = int((foxmail_rect.bottom - foxmail_rect.top) / 2) + foxmail_rect.top

    #         print foxmail_rect.top,foxmail_rect.bottom,foxmail_rect.left,foxmail_rect.right,wszBuff.value

    print(xpos, ypos, ' --- ', wszBuff.value)
    print('wszBuff --- ', wszBuff)

    lParam = ypos << 16 | xpos
    win32api.PostMessage(hWnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32api.PostMessage(hWnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, lParam)
    win32api.PostMessage(hWnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, lParam)

#         win32gui.SendMessage(win32gui.GetParent(hWnd), win32con.WM_COMMAND, tbButton.idCommand, hWnd)
#         win32api.PostMessage(hWnd,win32con.WM_LBUTTONDOWN,win32con.MK_LBUTTON,lParam)
#         win32api.SendMessage(hWnd,win32con.WM_LBUTTONDOWN,win32con.MK_LBUTTON,lParam)
    print (win32api.PostMessage(hWnd,commctrl.TB_GETBUTTONSIZE,tbButton.idCommand,0))


