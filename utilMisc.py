import gettext
import locale
from contextlib import contextmanager
# import wx
# import os, sys
# from cusLogger import *
# import numpy as np
# from typing import List
# import typing
# import pathlib


#======================================================================================================================
# nMin <= ReturnVal <= nMax
# if nVal < nMin : return nMin
# if nVal > nMax : return nMax
def LimitRng_EQ(nVal, nMin, nMax):
    return max(nMin, min(nVal, nMax))

# nMin <= ReturnVal < nMax
def LimitRng_NE(nVal, nMin, nMax):
    return max(nMin, min(nVal, nMax - 1))

#======================================================================================================================
# usage example :
# print(IncInt.reset())
# print(IncInt.val)
# print(IncInt.val)
# print(IncInt.reset())
# print(IncInt.val)
# print(IncInt.val)
#
# output :
# 0
# 1
# 2
# 0
# 1
# 2
class IncInt:
    nVal = -1   #type: int
    @classmethod
    def reset(cls) -> int:
        cls.nVal = 0
        return cls.nVal
    @classmethod
    @property
    def val(cls) -> int:
        cls.nVal += 1
        return cls.nVal

#======================================================================================================================
# usage example :
#     ## 須先在特定目錄準備好 test.mo
#     SetTransLID('test', localedir='locale', languages=['zh_TW'])
#     print(LID('this is multi-lang string'))
#     # if arg languages=[None] : get system default language

def SetTransLID(*args, **kwargs):
    if kwargs['languages'][0] is None:
        kwargs['languages'][0] = locale.getdefaultlocale()[0]
    es = gettext.translation(*args, **kwargs)
    # es.install()
    # 以下模仿 install() source code, 也將 LID 加入 buid-in namespace
    import builtins
    builtins.__dict__['LID'] = es.gettext
    return es.gettext

# just for PyCharm code completion
if False:
    def LID(s : str):
        pass

#======================================================================================================================
# usage example :
# with SelectAndFree(wx.MemoryDC(), bmp, wx.NullBitmap) as dc:
#     dc.SetBackground(wx.Brush(bg_color))
#     dc.Clear()
#     dc.SetTextForeground(text_color)
#     dc.DrawText(text, text_x, text_y)
# //等於 dc = wx.MemoryDC();  dc.SelectObject(bmp);  .....;  dc.SelectObject(wx.NullBitmap);

@contextmanager
def SelectAndFree(dc, objSel, objFree):
    try:
        dc.SelectObject(objSel)
        yield dc
    finally:
        dc.SelectObject(objFree)


