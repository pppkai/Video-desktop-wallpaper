import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning. python setup.py bdist_msi

# 中文需要显式用gbk方式编码
product_name = u'视频桌面'.encode('gbk')
product_desc = u"视频桌面 Ver1.0".encode("gbk")

#'C:\\Python38\\Lib\\site-packages\\pywin32_system32',
#'C:\\Python38\\Lib\\site-packages\\PyQt5\\Qt5\\bin',

# 主程序命名
target_name= 'PDesktop.exe'

buildOptions = dict(
    packages = [
        'os', 'sys', 'cv2', 'numpy', 'screeninfo', 'win32gui', 'pywintypes', 'winreg', 'subprocess','requests', 'math', 'PIL', 'random', 'ctypes',
    ],
    include_files = [
        'C:\\Python38\\Lib\\site-packages\\cv2',
        'C:\\Python38\\Lib\\site-packages\\PyQt5\\Qt5\\plugins\\imageformats',
        'C:\\Python38\\Lib\\site-packages\\PyQt5\\Qt5\\plugins\\platforms',
        'd:\\work_home\\project_python\\liveWallPager\\p.ico',
        'd:\\work_home\\project_python\\liveWallPager\\res',
        'd:\\work_home\\project_python\\liveWallPager\\downloads'
    ],
    optimize = 2,
    path = sys.path,
    zip_include_packages = ['PyQt5'],
    includes = [],
    excludes = ['tkinter']
)

base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable(
        'd:\\work_home\\project_python\\liveWallPager\\main.py',
        base=base,
        targetName=target_name,
        icon="d:\\work_home\\project_python\\liveWallPager\\p.ico"
    )
]

shortcut_table = [
    ("DesktopShortcut",  # Shortcut
        "DesktopFolder",  # Directory_
        product_name.decode('gbk'),  # Name
        "TARGETDIR",  # Component_
        "[TARGETDIR]"+target_name,  # Target
        None,  # Arguments
        product_desc.decode('gbk'),  # Description
        None,  # Hotkey
        "",  # Icon
        0,  # IconIndex
        None,  # ShowCmd
        'TARGETDIR'  # WkDir
    ),
    ("StartupShortcut",  # Shortcut
        "StartupFolder",  # Directory_
        product_name.decode('gbk'),  # Name
        "TARGETDIR",  # Component_
        "[TARGETDIR]"+target_name,  # Target
        None,  # Arguments
        product_desc.decode('gbk'),  # Description
        None,  # Hotkey
        "",  # Icon
        0,  # IconIndex
        None,  # ShowCmd
        'TARGETDIR'  # WkDir
    )
]

msi_data = {"Shortcut": shortcut_table}
#bdist_msi_options = {'data': msi_data}
bdist_msi_options = {
    'data': msi_data,
    'upgrade_code': '{9f21e33d-48f7-cf34-33e9-efcfd80eed10}',
    'add_to_path': False,
    'initial_target_dir': r'[ProgramFilesFolder]\%s' % product_name.decode('gbk')
}

setup(
    name = 'PDesktop',
    version = '1.0.1',
    description = product_desc.decode('gbk'),
    author = 'pengzl',
    author_email = '249247321@qq.com',
    options = {"build_exe": buildOptions, "bdist_msi": bdist_msi_options},
    executables = executables
)
