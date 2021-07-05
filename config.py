from PyQt5.QtGui import QColor, QFont
import platform
import sys
import os


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# Setting Configure
COLOR_GREEN = QColor(77, 174, 81)
COLOR_WHITE = QColor(255, 255, 255)
COLOR_SUCCESS = QColor(180, 225, 220)
COLOR_FAIL = QColor(250, 189, 211)

FONT_BASIC = QFont()
FONT_BOLD = QFont()
FONT_BOLD.setBold(True)

WINDOW_TITLE = 'MMLAB Video Editor'
WINDOW_POS_X = 100  # - 2560
WINDOW_POS_Y = 100
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 850

VIDEO_TABLE_WIDTH = 280

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480
INFO_WIDTH = CANVAS_WIDTH - 20

SCRIPT_DIALOG_WIDTH = 720
SCRIPT_DIALOG_HEIGHT = 480

RESULT_DIALOG_WIDTH = 1024
RESULT_DIALOG_HEIGHT = 480

VIDEO_EXTENSIONS = ('.3g2', '.3gp', '.3gp2', '.3gpp', '.asf', '.avchd', '.avi', '.flv', '.m1v', '.m4v', '.mkv', '.mov',
                    '.mp2', '.mp4', '.mpe', '.mpeg', '.mpg', '.mpv', '.qt', '.rm', '.swf', '.webm', '.wmv')

VIDEO_EXTENSION_FILTER = 'All Media Files |' + ';'.join([f'*{i}' for i in VIDEO_EXTENSIONS])
FILE_DIALOG_ROOT = os.path.abspath(os.curdir)

PRESET_DEFAULT_ROOT = os.path.abspath(os.path.curdir)
PRESET_DEFAULT_FILE = os.path.join(PRESET_DEFAULT_ROOT, 'preset.pkl')

TARGET_DEFAULT_ROOT = os.path.join(FILE_DIALOG_ROOT, 'outputs')

SCRIPT_EXT = 'bat'
if platform.system() == 'Linux':
    default_script_ext = 'sh'
SCRIPT_DEFAULT_FILE = os.path.join(TARGET_DEFAULT_ROOT, f'script.{SCRIPT_EXT}')
RESULT_DEFAULT_FILE = os.path.join(TARGET_DEFAULT_ROOT, f'result.json')
LOG_DEFAULT_FILE = os.path.join(TARGET_DEFAULT_ROOT, f'result.log')

THUMBNAIL_RESPONSE_TIME = 1000

VIDEO_SELECTED_COLOR = COLOR_GREEN

LOGO_DEFAULT = resource_path('default_logo.jpg')
FONT_DEFAULT = resource_path('NanumMyeongjo.ttf')
CAPTION_DEFAULT = ''
