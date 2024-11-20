# import wx, time, os
# import typing
# from typing import List
import logging
import inspect
import traceback
import wx
import sys

# usage example :
# ======================================================================================
# from cusLogger import *
#
# TCustomLog.SetLogFile('./foo.log')
# TCustomLog.SetLogLevel(fileLv = logging.DEBUG, consoleLv = logging.DEBUG)
# AddLogDug("hello {} {val}", "this_by_pos", val="this_by_name")
# ======================================================================================
# 注意 AddLogXXX 故意將傳入的 bool 由 True/False 顯示成 T1/F0, ex:
# AddLogDug('result={}', 1>0)  ## output "result=T1"
# ======================================================================================


# 若未定義 __all__, 則 import * 的預設行為是除了 _xx 外的全部
# __all__ = ['TCustomLog', 'AddLogDug', 'AddLogInf', 'AddLogERR']

def GetKeyboardName(keycode):
    key_map = {
        wx.WXK_BACK: "Backspace",
        wx.WXK_TAB: "Tab",
        wx.WXK_RETURN: "Enter",
        wx.WXK_ESCAPE: "Escape",
        wx.WXK_SPACE: "Space",
        wx.WXK_DELETE: "Delete",
        wx.WXK_SHIFT: "Shift",
        wx.WXK_CONTROL: "Ctrl",
        wx.WXK_ALT: "Alt",
        wx.WXK_LEFT: "Left",
        wx.WXK_UP: "Up",
        wx.WXK_RIGHT: "Right",
        wx.WXK_DOWN: "Down",
        wx.WXK_PAGEUP: "Page Up",
        wx.WXK_PAGEDOWN: "Page Down",
        wx.WXK_HOME: "Home",
        wx.WXK_END: "End",
        wx.WXK_F1: "F1",
        wx.WXK_F2: "F2",
        wx.WXK_F3: "F3",
        wx.WXK_F4: "F4",
        wx.WXK_F5: "F5",
        wx.WXK_F6: "F6",
        wx.WXK_F7: "F7",
        wx.WXK_F8: "F8",
        wx.WXK_F9: "F9",
        wx.WXK_F10: "F10",
        wx.WXK_F11: "F11",
        wx.WXK_F12: "F12"
    }
    keyname = key_map.get(keycode, "Unknown")
    return f'<{keyname}>'

# 列出目前函數名, 及其各層級呼叫函數
# 過濾掉(不列出)內建or安裝的 module 之函數, 但保留最上層函數 (ex OnChar, OnMouse)
# ex :
#   [2024-02-06 14:01:08,922 DEB] <on_MyTimer / onPlayTimer / SetSnte_NextMain_AndPlay / update_MainSnteRange> zli cnt=9, iRow=0
#   [2024-02-07 09:42:02,007 DEB] <OnMouse / onSelect / SetSnte_ByRow_AndPlay / set_TimePos> pos=10.30
class _CallerFunctionFilter(logging.Filter):
    def filter(self, record):
        stack = inspect.stack()  # stack[0]=目前函數名, [1]=上層, [2]=更上層, ...
        record.levelname = record.levelname[:3]
        sSysPath = r'c:\Program Files\Python'.lower()  # C:\Program Files\Python39\lib\...
        lExclFucName = ['AddLogDug', 'AddLogInf', '_custom_excepthook', '_LogCustomArg',
                        '_log', 'debug', 'info', 'MainLoop', '<module>', 'filter', 'handle', 'callHandlers']
        liObjAll = [m for m in stack[::-1]  if m.function not in lExclFucName]
        # print(f"* {' > '.join([m.function for m in liObjAll])}")  #原始呼叫階層
        # 原始 'OnMouse > ReverseHighlight > HighlightLine > SendNotify > onSelect'
        # 改成 'OnMouse > onSelect'
        # 原始 'on_timer > onPlayTimer > SetSnte_NextMain_AndPlay > update_MainSnteRange > Select > SetItemState > SetItemState > HighlightLine > SendNotify > onSelect'
        # 改成 'on_timer > onPlayTimer > SetSnte_NextMain_AndPlay > update_MainSnteRange > onSelect'

        # 不列出內建or安裝的 module 之函數, 但保留最上層函數 (ex OnChar, OnMouse)
        liName = [m.function for m in liObjAll[0:1]]  # ok if liObjAll==[]
        for m in liObjAll[1:]:
            # module = inspect.getmodule(m)  # module.__name__ == 'inspect'
            # print(f'!!{module}!!{m.filename}!!')
            #   !!<module 'inspect' from 'C:\\Program Files\\Python39\\lib\\inspect.py'>!!C:\Program Files\Python39\lib\site-packages\wx\lib\agw\ultimatelistctrl.py!!
            #   !!<module 'inspect' from 'C:\\Program Files\\Python39\\lib\\inspect.py'>!!C:\DriveD\MyPro\DataProc\Parser_Script\Python\+media\+voice\pjMusicRepeater\pjMusicRepeater.py!!
            if m.filename.lower().find(sSysPath) < 0:
                liName.append(m.function)
        fuName = ' / '.join(liName[:])
        record.caller_function = f'<{fuName}>'
        return True

# if TCustomLog.SetLogFile('./foo.log') has ever been called  ==> log to console & foo.log
# else  ==> log to console only
class TCustomLog:
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)  ##
    _formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(caller_function)s %(message)s')

    _handlerConsole = logging.StreamHandler()
    _handlerConsole.setLevel(logging.INFO)  ##
    _handlerConsole.addFilter(_CallerFunctionFilter())
    _handlerConsole.setFormatter(_formatter)

    _logger.addHandler(_handlerConsole)
    _handlerFile = None

    @classmethod
    def SetLogFile(cls, fna):
        cls._handlerFile = logging.FileHandler(fna, mode='w')  #type: logging.FileHandler
        cls._handlerFile.setLevel(logging.DEBUG)  ##
        cls._handlerFile.addFilter(_CallerFunctionFilter())
        cls._handlerFile.setFormatter(cls._formatter)
        # cls._handlerFile.buffer_size = 1024 * 100   # bytes
        cls._logger.addHandler(cls._handlerFile)
        sys.excepthook = cls._custom_excepthook

    # ex: TCustomLog.SetLogLevel(fileLv = logging.DEBUG, consoleLv = logging.INFO)
    @classmethod
    def SetLogLevel(cls, fileLv = None, consoleLv = None):
        if fileLv:
            cls._handlerFile.setLevel(fileLv)
        if consoleLv:
            cls._handlerConsole.setLevel(consoleLv)

    @classmethod
    def isLogLevel(cls, level):
        return cls._logger.isEnabledFor(level)

    @classmethod
    def getFileLevel(cls):
        return cls._handlerFile.level

    @classmethod
    def _custom_excepthook(cls, exc_type, exc_value, exc_traceback):
        # https://stackoverflow.com/questions/6234405/logging-uncaught-exceptions-in-python
        # Do not print exception when user cancels the program (Ctrl+C)
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        cls._logger.error("An uncaught exception occurred:")
        cls._logger.error("Type: %s", exc_type)
        cls._logger.error("Value: %s", exc_value)
        if exc_traceback:
            format_exception = traceback.format_tb(exc_traceback)
            for line in format_exception:
                cls._logger.error(repr(line))
            # or try below :
            # ErrorMessage = traceback.format_exception(exc_type, exc_value, exc_traceback)
            # cls._logger.error(ErrorMessage)

# - by Dutch Masters : https://stackoverflow.com/questions/13131400/logging-variable-data-with-new-format-string
#   then can AddLogDug("hello {} {val}", "Python", val="World")
# - org version :
# def AddLogDug(msg: str, *args, **kwargs):
#     if TCustomLog._logger.isEnabledFor(logging.DEBUG):
#         TCustomLog._logger.debug(msg.format(*args, **kwargs))

# 自訂 bool 格式 : True/False -> T1/F0
def _LogCustomArg(level, fnLog, msg: str, *args, **kwargs):
    if TCustomLog._logger.isEnabledFor(level):
        lb = ('F0', 'T1')
        li = [lb[int(m)] if isinstance(m, bool) else m for m in args]
        di = {key : (lb[int(val)] if isinstance(val, bool) else val)  for (key, val) in kwargs.items()}
        # dict comprehension :  {(key cond):(value cond) for (key, value) in dict.items() }
        fnLog(msg.format(*li, **di))
        # TCustomLog._handlerFile.flush()

# - 太常用, 故移至 class 外面, 且命名以[打字快]為原則 (ex Dug=Debug)
def AddLogDug(msg: str, *args, **kwargs):
    _LogCustomArg(logging.DEBUG, TCustomLog._logger.debug, msg, *args, **kwargs)
def AddLogInf(msg: str, *args, **kwargs):
    _LogCustomArg(logging.INFO, TCustomLog._logger.info, msg, *args, **kwargs)
def AddLogERR(msg: str, *args, **kwargs):
    _LogCustomArg(logging.ERROR, TCustomLog._logger.error, msg, *args, **kwargs)

