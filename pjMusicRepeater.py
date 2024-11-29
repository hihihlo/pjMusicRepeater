import logging
import re
import wx, time, os, sys
from cusLogger import *
from infSetting import *
from TAudio import *
from utilMisc import *
from simulateKey import *
import typing
from typing import List
from plum import dispatch  # pip install plum-dispatch   # for function overloading
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.ticker as ticker
from matplotlib import collections as pltCollections
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
# from matplotlib.figure import Figure
import mpv

from wx.lib.agw import ultimatelistctrl as ULC
import wx.lib.colourutils as cutils
# import threading
from copy import deepcopy
import Forms_
import fmSettingBase as fmBase

def find_nearest_index(ary, goal):
    index = np.searchsorted(ary, goal, side="left")

    if index == 0:
        return 0
    elif index == len(ary):
        return len(ary) - 1
    else:
        # 檢查前一個元素和後一個元素，找出距離goal更近的索引
        before = ary[index - 1]
        after = ary[index]
        if after - goal < goal - before:
            return index
        else:
            return index - 1

class TBackground:
    def __init__(self, canvas : FigureCanvas, autoSaveBg_OnDraw):
        self.background = None
        self.canvas = canvas
        if autoSaveBg_OnDraw:
            self.canvas.mpl_connect('draw_event', self.onDraw_)

    def onDraw_(self, event):
        self.background = self.canvas.copy_from_bbox(self.canvas.figure.bbox)

    def saveToBg(self):
        self.background = self.canvas.copy_from_bbox(self.canvas.figure.bbox)

    def restore(self):
        if self.background is not None:
            self.canvas.restore_region(self.background)

    #單純使全部的 draw_artist 顯示在 canvas 上, 不影響 .background  (需要時須自行呼叫 saveToBg)
    def blit(self):
        self.canvas.blit()
        # self.canvas.flush_events()

    def clear(self):
        self.canvas.ClearBackground()


# https://blog.csdn.net/weixin_52071682/article/details/112298659
# https://matplotlib.org/stable/tutorials/advanced/blitting.html#minimal-example
# ex usage : cursor = TCrossCursor(fig.canvas, ax, color='w', lw=0.5)
class TCrossCursor:
    def __init__(self, bg: TBackground, ax: plt.axes, **lineprops):
        self.connMove = None
        self.connDraw = None
        self.ax = ax
        self.bg = bg
        lineprops['animated'] = True  # for blit, draw_artist() 時才會真正畫
        self.lines = [
            # ax.axhline(20, visible=False, **lineprops),  # axHorLine
            ax.axvline(20, visible=False, **lineprops)  # axVerLine
        ]
        self.EnableEvent(True)

    def EnableEvent(self, bEnable):
        if bEnable:
            self.connMove = self.bg.canvas.mpl_connect('motion_notify_event', self.onMouseMove)
            self.connDraw = self.bg.canvas.mpl_connect('draw_event', self.onDraw)
        else:
            if self.connMove:
                self.bg.canvas.mpl_disconnect(self.connMove)
                self.connMove = None
            if self.connDraw:
                self.bg.canvas.mpl_disconnect(self.connDraw)
                self.connDraw = None

    def onDraw(self, event):
        for line in self.lines:
            line.set_visible(False)

    def onMouseMove(self, event):
        if event.inaxes is None: return  # ////
        if not self.bg.canvas.widgetlock.available(self): return  # ////

        if event.inaxes == self.ax:
            # line = self.lines[0]
            # line.set_ydata((event.ydata, event.ydata))
            # line.set_visible(True)
            # line = self.lines[1]
            # line.set_xdata((event.xdata, event.xdata))
            # line.set_visible(True)
            line = self.lines[0]
            line.set_xdata((event.xdata, event.xdata))
            line.set_visible(True)
        # else:
        #     self.lines[1].set_visible(False)

        self.bg.restore()
        for line in self.lines:
            if line.get_visible():
                line.axes.draw_artist(line)
        self.bg.blit()


"""
class MyUltimateHeaderRenderer(object):
    def __init__(self, parent):
        self._hover = False
        self._pressed = False

    def DrawHeaderButton(self, dc, rect, flags):
        return
        self._hover = False
        self._pressed = False
        color = wx.Colour(255, 0, 0)

        if flags & wx.CONTROL_DISABLED:
            color = wx.Colour(wx.WHITE)
        elif flags & wx.CONTROL_SELECTED:
            color = wx.Colour(wx.BLUE)

        if flags & wx.CONTROL_PRESSED:
            self._pressed = True
            color = cutils.AdjustColour(color, -50)
        elif flags & wx.CONTROL_CURRENT:
            self._hover = True
            color = cutils.AdjustColour(color, -50)

        dc.SetBrush(wx.Brush(color, wx.SOLID))
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetPen(wx.TRANSPARENT_PEN)
        # dc.DrawRectangleRect(rect)
        # dc.SetBackgroundMode(wx.TRANSPARENT)

    def GetForegroundColour(self):
        # if self._hover:
        #     return wx.Colour(255,255,255)
        # else:
        #     return wx.Colour(0,0,0)
        return wx.Colour(0, 0, 255)
"""

class TMsgTip:
    def __init__(self, fmMain):
        self.fmMain = fmMain  #type: FmMain
    def CheckContent(self):
        fm = self.fmMain
        msg = ''
        # 須符合 USnte.esntyMain/Sub/Copy 之順序
        for pair in [(fm.edDefSn_MainCnt, LID('MainSnte')), (fm.edDefSn_SubCnt, LID('SubSnte')), (fm.edDefSn_CopyCnt, LID('CopySnte'))]:
            # allow GetValue() = '0'  (plcnt = 0 means skip / not play that snte)
            if pair[0].GetValue() == '':
                msg = LID("def cnt of {} can't be empty !").format(pair[1])
        if msg == '':
            self.fmMain.ztxtMsg.Hide()
            AddLogDug('ok')
        else:
            AddLogDug('chk msg={}', msg)
            msg += ' '
            self.fmMain.ztxtMsg.SetLabel(msg)
            self.fmMain.ztxtMsg.Show(True)
        self.fmMain.panelMsg.GetParent().Layout()
        return msg == ''


# 斷句/srt/複讀
class TRepInf:
    # ezl : enum / zListCtrl field num
    ezlId = IncInt.reset()
    ezlEnablePlay = IncInt.val
    ezlSpeed = IncInt.val
    ezlPlayCnt = IncInt.val
    ezlOrgText = IncInt.val
    ezlTraText = IncInt.val
    ezlLen = IncInt.val
    ezlNote = IncInt.val

    # 播完本句後: stop, next, repeat Num, repeat forever
    # 播完本首後:
    # epm = enum Play Mode
    epmStop = IncInt.reset()
    epmNext = IncInt.val
    epmRepNum = IncInt.val
    epmRepLoop = IncInt.val
    epmCnt_ = IncInt.val

    # epp = enum Play Plan
    eppMain = IncInt.reset()
    eppSub = IncInt.val
    eppCopy = IncInt.val

    lSpeedOpt = np.array([0.5, 0.58, 0.66, 0.75, 1, 1.25, 1.5, 1.75])

    class UPlanItem:
        def __init__(self, epp, cnt, speed = None):
            self.ePlan = epp    # eppMain, ...
            self.MaxInCnt = cnt # None = by row setting (count in this plan)
            self.nSpeed = speed # None = by row setting
        def __repr__(self):
            return f"UPlanItem(plan={'MSC'[self.ePlan]}, cnt={self.MaxInCnt}, sp={self.nSpeed})"

    # for <<one>> MainSnte !
    class UPlan:
        def __init__(self):
            self.__luPlan = []      # type: List[TRepInf.UPlanItem]
            self.__iPlan = 0        # 0 <= __iPlan  < len(__luPlan)
            self.iInCnt = 0         # 0 <= iInCnt < __luPlan[].MaxInCnt
            self._addPlan(TRepInf.eppMain, None)
            self._addPlan(TRepInf.eppSub, None)
            self._addPlan(TRepInf.eppCopy, None)
            self._addPlan(TRepInf.eppMain, 1)
            self.reset()
        def __repr__(self):
            return f'UPlan(len={len(self.__luPlan)}, iPl={self.__iPlan}, iIn={self.iInCnt})'
        def _addPlan(self, epp, cnt, speed = None):
            self.__luPlan.append(TRepInf.UPlanItem(epp, cnt, speed))
        # ex sPlan = "M*S*C*M1"
        def makeFromStr(self, sPlan):
            pass
        def reset(self):
            AddLogDug('UPlan_reset')
            self.__iPlan = 0
            self.iInCnt = 0
        def NextInCnt(self, MaxCnt_inRow):
            self.iInCnt += 1
            cit = self.CurPlan   #cit = Current ITem
            MaxCnt = MaxCnt_inRow
            if cit and cit.MaxInCnt is not None:
                MaxCnt = cit.MaxInCnt   # CurItem.MaxInCnt 優先於 MaxCnt_inRow 之值
            if self.iInCnt > MaxCnt:
                return False  #////
            AddLogDug('{} {} MaxCnt={}:{}', self, cit, cit.MaxInCnt if cit else None, MaxCnt_inRow)  # "MaxCnt=ItemCnt:RowCnt", 優先值:row值
            return True
        @property
        def CurPlan(self):   #type: TRepInf.UPlanItem
            return self.__luPlan[self.__iPlan]   if self.__iPlan < len(self.__luPlan) else   None
        def NextPlan(self):   #type: TRepInf.UPlanItem
            if self.__iPlan + 1 >= len(self.__luPlan):
                AddLogDug('ret None')
                return None  #////
            self.__iPlan += 1
            self.iInCnt = 0
            AddLogDug('{} {}', self, self.CurPlan)
            return self.__luPlan[self.__iPlan]
            # if self.__iPlan >= len(self.__luPlan):
            #     return None  #////
            # uItem = self.__luPlan[self.__iPlan]
            # if self.iPledCnt < uItem.nCnt:
            #     self.iPledCnt += 1
            # else:
            #     self.iPledCnt = 0
            #     self.__iPlan += 1
            # return uItem  #////

    def __init__(self,
                 audio :TAudio,
                 player :TPlayer,
                 fmMain):
        self.PlayMode_Snte = self.epmNext  # 播完[本句]後的行為
        self.audio = audio
        self.player = player
        self.fmMain = fmMain  #type: FmMain
        # selection range, A B point time (float sec)
        self.lSelRangeNarr = [None, None]   # List[typing.Union[None, float]]
        AddLogDug('fn TRepInf.__init__')
        self.__lRow2Snte = None

        self.reInit()

    def reInit(self):
        if not self.audio.isInit:
            AddLogDug('fn TRepInf.reInit -- NOT audio isInit')
            return  #////
        AddLogDug('fn TRepInf.reInit')
        self.__lRepDat = gInfFile.uInfUnit.lSnte   # type: List[USnte]
        self.__SnteNone = USnte(0, 0)
        self.__SnteNone.SetSnteEx(None, None, None, None)
        self.__lRow2Snte = []  #type: List[USnte]
        # current playing snte (mainSnte or subSnte)
        self.__CurrSntePlay = self.__SnteNone  #type: USnte

        self.iPledCnt_Unit = 0      # played cnt of track/unit
        self.uPlan = self.UPlan()
        self.iPlayMainSnte = 0      # which MainSnte playing
        self._updMapping(bDrawSelRange=False)  # not yet set fmMain.drawNarr now !
        self.SetSnte_ByRow(0)

    def _updMapping(self, bDrawSelRange = True):
        AddLogDug('bDraw={}', bDrawSelRange)
        level = TCustomLog.getFileLevel()
        TCustomLog.SetLogLevel(fileLv=logging.INFO)
        self.__lRow2Snte = []
        iRow = 0
        for iTop, uTop in enumerate(self.__lRepDat):
            self.__lRow2Snte.append(uTop)
            uTop.SetSnteEx(iTop, None, iRow, None)  # iSub=None
            iRow += 1
            # if bDrawSelRange:
            #     self.fmMain.drawWide.SelRange_draw(uTop, uTop.bgn, uTop.end, bLight=False)
            for iSub, uSub in enumerate(uTop.lSub):
                self.__lRow2Snte.append(uSub)
                uSub.SetSnteEx(iTop, iSub, iRow, uTop)
                iRow += 1
                AddLogDug('sub{}, isCopy={}', uSub, uSub.isCopySnte)
                # draw exist sub SelRanges (isCopySnte 會和其它 SubSnte 重疊, 故不畫它)
                if bDrawSelRange and not uSub.isCopySnte:
                    self.fmMain.drawNarr.SelRange_draw(uSub, uSub.bgn, uSub.end, bLight=False)
        TCustomLog.SetLogLevel(fileLv=level)

    # def GetInd_ByFindSnte(self, haystack: list, needle: USnte) -> typing.Union[USnte, None]:
    #     # snte = next((m for m in haystack if m == needle), None)
    #     if needle in haystack:
    #         ii = haystack.index(needle)
    #     else:
    #         return None

    @property
    def CurInd(self) -> UInd:
        return UInd(self.CurSnte_Play.i_top, self.CurSnte_Play.i_sub)
    # sntePlay = 目前播放範圍, is mainSnte or subSnte !
    # snteMain = sntePlay 之 par snte, is mainSnte always
    # ex: 當選擇 main snte 時 二者相同
    # ex: 當選擇 sub snte 時 二者不相同 (sntePlay=子句 snteMain=母句)
    @property
    def CurSnte_Play(self) -> USnte:
        return self.__CurrSntePlay
    @CurSnte_Play.setter
    def CurSnte_Play(self, newVal):
        AddLogDug('SetCurSntePl row= {}->{}, {}', self.__CurrSntePlay.iRow, newVal.iRow, newVal)
        self.__CurrSntePlay = newVal
    @property
    def CurSnte_Main(self) -> USnte:
        snplay = self.__CurrSntePlay
        return snplay  if snplay.isPar else  self.__lRepDat[snplay.i_top]
            # the latter same as ==>             self.GetSnte_ByInd(snplay.i_top, None)
    @dispatch
    def GetSnte_ByInd(self, uInd: UInd) -> USnte:
        if not self.__lRepDat:  # 已含 len(self.__lRepDat) == 0
            snte = self.__SnteNone
        elif not (0 <= uInd.itop < len(self.__lRepDat)):
            snte = self.__SnteNone
        elif uInd.isub is None:  # isPar/MainSnte
            snte = self.__lRepDat[uInd.itop]
        elif not (0 <= uInd.isub < len(self.__lRepDat[uInd.itop].lSub)):
            snte = self.__SnteNone
        else:
            snte = self.__lRepDat[uInd.itop].lSub[uInd.isub]
        return snte
    @dispatch
    def GetSnte_ByInd(self, itop, isub) -> USnte:
        return self.GetSnte_ByInd(UInd(itop, isub))
    def GetSnte_ByRow(self, iRow) -> USnte:
        # AddLogDug('iRow={}, lRow.cnt={}', iRow, len(self.__lRow2Snte))
        return self.__lRow2Snte[iRow]
    def GetSnteCnt(self, isMain):
        return len(self.__lRepDat)  if isMain else  len(self.__lRow2Snte)
    # auto removeRow of zlc
    def DelSnte(self, sntePlay: USnte,  bUpdMapping, bDelCopy):
        AddLogDug('del{}, bUpdMapping={}', sntePlay, bUpdMapping)
        if sntePlay.isPar:
            cnt = len(self.__lRepDat[sntePlay.i_top].lSub)
            for ii in reversed(range(cnt)):
                self.DelSnte(self.__lRepDat[sntePlay.i_top].lSub[ii], False, bDelCopy=True)  # recursion
        elif sntePlay.isCopySnte and not bDelCopy:
            sntePlay.plcnt = 0
            self.fmMain.lire.updatePlayCnt(sntePlay, updSubSntes=True)
        else:   # is-normal-SubSnte or isCopySnte-and-bDelCopy
            snteMain = self.__lRepDat[sntePlay.i_top]
            self.fmMain.lire.removeRow(sntePlay.pEx.iRow)
            if sntePlay.pEx.SelRangeArtist:
                sntePlay.pEx.SelRangeArtist.remove()
                AddLogDug('{} Art-', sntePlay)
            snteMain.lSub.pop(sntePlay.i_sub)
        if bUpdMapping:
            self._updMapping(bDrawSelRange=False)
    # goto Snte
    def SetSnte_ByRow(self, iRow, bUpdGui = True):
        if not (0 <= iRow < self.GetSnteCnt(isMain=False)):
            return False  #////
        AddLogDug('row={}, gui={}', iRow, bUpdGui)
        if hasattr(self.fmMain, 'lire') and not self.CurSnte_Play.isNone:  # hasattr : avoid init_ing...
            self.fmMain.lire.highlightSubSnte(self.CurSnte_Play.iRow, False)
        self.CurSnte_Play = self.GetSnte_ByRow(iRow)
        if bUpdGui and self.CurSnte_Play.isSub:
            self.fmMain.lire.highlightSubSnte(self.CurSnte_Play.iRow, True)
        return True  #////
    # goto Snte & play
    def SetSnte_ByRow_AndPlay(self, iRow, changeZLC):
        if not self.SetSnte_ByRow(iRow):
            return False  #////
        AddLogDug('go new{}', self.CurSnte_Play)
        self.player.set_TimePos(self.CurSnte_Play.bgn, self.CurSnte_Play)
        self.fmMain.update_MainSnteRange()
        if changeZLC:
            self.fmMain.lire.SelectRow(self.CurSnte_Play.iRow)
        self.fmMain.update_vline_position()
        self.fmMain.audio_play()
        self.fmMain.lire.EnsureVisible()
        # self.fmMain.lire.highlightSubSnte(self.CurSnte_Play.iRow, False)   # did in SetSnte_ByRow
        return True  #////
    def SetSnte_ToMain(self, bAndPlay = False):
        AddLogDug('org SntePlay{}', self.CurSnte_Play)
        if not self.CurSnte_Play.isNone:
            self.fmMain.lire.highlightSubSnte(self.CurSnte_Play.iRow, False)
        self.fmMain.lire.highlightSubSnte(self.CurSnte_Main.iRow, True)
        self.CurSnte_Play = self.GetSnte_ByInd(self.CurSnte_Main.i_top, None)
        if bAndPlay:
            self.fmMain.lire.SelectRow(self.CurSnte_Main.iRow)

    # goto Next Main Snte & play
    # dire : 1 (Next) or -1 (Prev)
    def SetSnte_NextMain_AndPlay(self, dire, bPlay):
        iTopOld = self.CurSnte_Main.i_top
        AddLogDug('org SntePlay{}, iTopOld={}', self.CurSnte_Play, iTopOld)
        NewSnte = self.CurSnte_Main
        while True:
            NewSnte = self.GetSnte_ByInd(NewSnte.i_top + dire, None)
            AddLogDug('trySnte{}', NewSnte)
            if NewSnte.i_top == iTopOld and NewSnte.plcnt <= 0:
                # 已循環一圈了 !  case: 在唯一可播的句子上 令 plcnt=0
                AddLogInf('No sentences can be played')
                self.fmMain.audio_pause()
                return  #////
            if NewSnte.isNone:
                NewSnte = self.GetSnte_ByInd(0, None)
            if NewSnte.plcnt <= 0:
                continue  #////
            if NewSnte.isSub:
                continue  #////
            break  #////
        AddLogDug('new SntePlay{}', NewSnte)

        if not self.CurSnte_Play.isNone:
            self.fmMain.lire.highlightSubSnte(self.CurSnte_Play.iRow, False)
        self.fmMain.lire.highlightSubSnte(NewSnte.iRow, True)
        self.CurSnte_Play = NewSnte
        self.fmMain.update_MainSnteRange()
        self.fmMain.lire.SelectRow(self.CurSnte_Play.iRow)
        if bPlay:
            self.player.set_TimePos(self.CurSnte_Play.bgn, self.CurSnte_Play)
            self.fmMain.update_vline_position()
        self.fmMain.lire.EnsureVisible()

    # - AddCnt & Play,  NOT change index
    # - if plcnt == 0 or OverMaxInCnt :  return,
    #   then goto next SubSnte or plan (MainSnte/SubSnte/CopySnte) by caller
    def PlayPlan_raw_(self):
        plan = self.uPlan
        if plan.CurPlan.ePlan == self.eppMain:
            snte = self.CurSnte_Main
            AddLogDug('case eppMain play{} rawCnt={}, plCnt={}', snte, snte.plcnt_raw, snte.plcnt)
            if not plan.NextInCnt(snte.plcnt):
                return False  #////
            self.fmMain.player.SetSpeed(snte.speed)
            self.player.set_TimePos(snte.bgn, snte)  # play mainSnte again
            self.SetSnte_ToMain(bAndPlay=True)
        elif plan.CurPlan.ePlan == self.eppCopy:
            if len(self.CurSnte_Main.lSub) <= 0:
                AddLogERR("lSub is empty, can't play CopySnte ! main{}", self.CurSnte_Main)
                return False  #////
            snte = self.CurSnte_Main.lSub[-1]
            AddLogDug('case eppCopy play{} rawCnt={}, plCnt={}', snte, snte.plcnt_raw, snte.plcnt)
            if not plan.NextInCnt(snte.plcnt):
                return False  #////
            self.fmMain.player.SetSpeed(snte.speed)
            self.SetSnte_ByRow_AndPlay(snte.iRow, changeZLC=True)  # play copySnte again
        elif plan.CurPlan.ePlan == self.eppSub:
            snte = self.CurSnte_Play
            AddLogDug('case eppSub play{} isPar={}, isCopy={}', snte, snte.isPar, snte.isCopySnte)
            if snte.isPar:
                snte = self.GetSnte_ByInd(UInd(snte.i_top, 0))  # get first SubSnte
                if snte.isNone:   #ex: no any SubSnte can be play !
                    return False  #////
            if snte.isCopySnte or not plan.NextInCnt(snte.plcnt):
                self.SetSnte_ByRow(snte.iRow, bUpdGui=False)
                return False  #////
            self.fmMain.player.SetSpeed(snte.speed)
            self.SetSnte_ByRow_AndPlay(snte.iRow, changeZLC=True)
        else:
            AddLogERR('loss proc ePlan !')

        # self.fmMain.player.SetSpeed(snte.speed)  #為讓 SetSpeed 儘早生效, 故已不放在此處
        return True  #////

    # plan index 原則 : 先 增加/設定 好 index, 然後才 play (playing 時符合目前 index 值)
    def PlayPlan(self):
        plan = self.uPlan
        while not self.PlayPlan_raw_():
            # now is [over play-cnt of current-snte] or [skip/ignore plcnt=0]
            plan.iInCnt = 0
            bCallNextItem = False
            newItem = None
            snte = self.CurSnte_Play
            # SubSnte 可能多句 : SubSnte row play-cnt-done 是走到下一個 SubSnte, 播完最後的 SubSnte 才走到下一個 plan item
            if plan.CurPlan.ePlan == self.eppSub:
                if snte.i_sub + 1 >= len(self.CurSnte_Main.lSub):    # all SubSnte play done
                    bCallNextItem, newItem  =  True, plan.NextPlan()
                else:
                    self.SetSnte_ByRow(snte.iRow + 1)           # go next SubSnte
            # MainSnte/CopyMainSnte row play-cnt-done 是走到下一個 plan item
            else:
                bCallNextItem, newItem  =  True, plan.NextPlan()

            if bCallNextItem:
                if newItem:
                    # self.SetSnte_ToMain()
                    pass
                else:
                    plan.reset()  # play plan done, go next mainSnte
                    self.SetSnte_NextMain_AndPlay(1, bPlay=False)
                # break  #////

    def onPlayTimer(self):
        # 整個音檔播完後, 有時發生以下情況 :
        #   AddLogDug('isPlaying==false, btnP={}, idle={}, pos={}', self.btnPlay.GetValue(), self.player.idle_active, self.playTimePos.TimePos)
        #   [2024-02-06 08:32:01,697 DEB] <on_timer> isPlaying==false, btnP=True, idle=True, pos=None
        # 故不可 isPlaying==false / self.playTimePos.TimePos None / idle_active True 就 return
        #   須使其開始 audio_play(), 以免因 TimePos 一直為 None 而沒機會開始 play

        timepos = self.player.TimePos
        # 有選擇範圍時 必 replay (直到加入list 或 取消範圍), 此時暫忽略 PlayMode / plan
        if self.isSelRangeMode:
            if (timepos is None) or (timepos >= self.lSelRangeNarr[1]):   # 必定 lSelRangeNarr[1] <= tiEnd
                self.player.set_TimePos(self.lSelRangeNarr[0],  'InSelRange')
            return   #////
        # 在 plcnt/speed setting dialog 時, 為了方便設定操作, 固定在該句不往下走
        if fmBase.FmSpdCntBase.DlgShowing:
            # AddLogDug('pos={}, play{}', timepos, self.CurSnte_Play)
            if (timepos is None) or (timepos >= self.CurSnte_Play.end):
                self.player.set_TimePos(self.CurSnte_Play.bgn,  'DlgShowing')
            return   #////
        # if self.CurSnte_Play.isSub:
        #     AddLogERR("isSub !? {}", self.CurSnte_Play)   # !!
        #     return   #////

        # main snte 播放完畢時的動作
        isMainSnteEnd = timepos is None  # 播完本音檔 (同時也是播完最後一個 snte)
        if isMainSnteEnd:
            AddLogDug('TimePos is None')
        else:
            isMainSnteEnd = timepos >= self.CurSnte_Play.end  # 播完本 snte
            if isMainSnteEnd:
                AddLogDug('TimePos({}) >= snte.end ', f'{timepos:.2f}')
        if isMainSnteEnd:
            if self.PlayMode_Snte == self.epmNext:
                self.PlayPlan()
            elif self.PlayMode_Snte == self.epmRepLoop:
                self.player.set_TimePos(self.CurSnte_Play.bgn,  self.CurSnte_Play)

    # difKey = -1 or 1,   0=refresh/update,  -99=slowest,  99=fastest
    def ChgSpeed_byKey(self, difKey):
        snte = self.CurSnte_Play
        lSpeedOpt = self.lSpeedOpt
        # i-1 <- def -> i+1         //def時按鍵 : 以 def 之真實值(Unit or App)往左/右走
        iOrg = np.abs(lSpeedOpt - snte.speed).argmin()   # 若非完全相等, 則會找最接近者
        AddLogDug('iOrg={}, dif={}', iOrg, difKey)
        iNew = LimitRng_NE(iOrg + difKey, 0, len(lSpeedOpt))

        snte.speed = lSpeedOpt[iNew]
        self.fmMain.player.SetSpeed(snte.speed)     # NOTE: maybe new player.Speed <> snte.speed
        real_Speed = self.fmMain.player.Speed       # obtain real value
        if snte.speed_raw is not None:  # 保持 None 才能顯示出 'def' 而非自動轉成數字
            snte.speed = real_Speed
        self.fmMain.lire.updateColumn(snte.iRow, self.ezlSpeed, TAudio.MpvToGuiP(snte.speed_raw))

    # difKey = -1 or 1
    def ChgPlCnt_byKey(self, difKey):
        snte = self.CurSnte_Play
        snte.plcnt += difKey
        self.fmMain.lire.updatePlayCnt(snte, updSubSntes=True)

    # set single point,  idxAB = A(0) or B(1)
    def SelRange_NarrSetOne(self, idxAB, tiSec):
        SelRng = self.lSelRangeNarr
        if idxAB == 1:
            if SelRng[0] is None or SelRng[0] > tiSec: return  #////
        elif idxAB == 0:
            if SelRng[1] and tiSec > SelRng[1]: return  #////
        SelRng[idxAB] = tiSec
        if SelRng[0] and SelRng[1]:
            self.fmMain.drawNarr.SelRange_draw(self.CurSnte_Play, SelRng[0], SelRng[1], bLight=True)
    # set both point
    def SelRange_NarrSetBoth(self, tiBgn, tiEnd):
        self.lSelRangeNarr[0], self.lSelRangeNarr[1] = tiBgn, tiEnd
        self.fmMain.drawNarr.SelRange_draw(self.CurSnte_Play, tiBgn, tiEnd, bLight=True)
    def SelRange_Cancel(self, bToMain, bUpd):
        AddLogDug("SelRng={}, bToMain={}, bUpd={} {}", self.lSelRangeNarr, bToMain, bUpd, self.CurSnte_Play)
        sel_ing = self.isSelRangeMode
        self.lSelRangeNarr[0] = None
        self.lSelRangeNarr[1] = None
        if sel_ing:
            self.fmMain.drawNarr.SelRange_Cancel(self.CurSnte_Play, True)
            if bToMain and self.CurSnte_Play.isSub:
                self.SetSnte_ToMain()
            if bUpd:   # if .isSub: restore sub SelRange to dark color   # _updMapping do it
                self._updMapping()   # remove highlight range, restore dark range
        return sel_ing
    def SelRange_Del(self):
        if not self.isSelRangeMode:
            return  #////
        snteDel  = self.CurSnte_Play
        if snteDel.isPar:
            return  #////
        self.SelRange_Cancel(bToMain=False, bUpd=False)
        if snteDel.isPar or snteDel.isCopySnte:
            return  #////   SelRange_Cancel also
        # self.fmMain.lire.removeRow(snteDel.iRow)  # did in DelSnte !
        AddLogDug("del{}", snteDel)
        self.DelSnte(snteDel, bUpdMapping=False, bDelCopy=False)  #
        self.SetSnte_ToMain()
        self._updMapping()
        # .SaveUnit()
        AddLogDug("new{}", self.CurSnte_Play)

    # add or modify SelRange (to sub snte)
    def SelRange_AddOrModify(self):
        if not self.isSelRangeMode:
            return  #////
        snteMain = self.CurSnte_Main
        snteDel  = self.CurSnte_Play
        AddLogDug("sntePl{}", snteDel)
        snteNew = USnte(None, None)
        for attr in snteDel.__dict__:
            if attr not in ['cont', 'pEx', '__plcnt', '__speed']:
                setattr(snteNew, attr, deepcopy(getattr(snteDel, attr)))
        # ==========================================================================================
        # <<< NOTE >>>
        # ==========================================================================================
        # 若未加 float(), 則在 yaml.dump 時會發生以下錯誤 :
        #   node = self.yaml_representers[None](self, data)
        #   raise RepresenterError(f'cannot represent an object: {data!s}')
        #   ruamel.yaml.representer.RepresenterError: cannot represent an object: 3.9762034801600024
        # ==========================================================================================
        snteNew.bgn = float(self.lSelRangeNarr[0])
        snteNew.end = float(self.lSelRangeNarr[1])
        if snteDel.isSub:
            # so it is [modify SelRange], not [add SelRange]
            self.DelSnte(snteDel, bUpdMapping=False, bDelCopy=False)  # modify=Del+Add
            self.SetSnte_ToMain()
        snteMain.lSub.append(snteNew)
        snteMain.lSub.sort(key= lambda m: (m.bgn, m.end))  #若 .bgn 也相等則比較 .end
        snteCopy = snteMain.lSub.pop(snteMain.lSub.index(snteMain))  #調整 snteCopy 位置, 保持放在最後面
        snteMain.lSub.append(snteCopy)
        self._updMapping()  #因加入至 lSub, 故會自動判斷到剛加入的 snteNew 屬於 sub snte 而非 main snte
        self.SelRange_Cancel(bToMain=True, bUpd=True)
        gInfFile.SaveUnit()
        iNewSub = snteMain.lSub.index(snteNew)
        AddLogDug('newCur{}', self.CurSnte_Play)
        iNewRow  = self.GetSnte_ByInd(self.CurInd.itop, iNewSub).iRow
        self.fmMain.lire.insertRow(iNewRow)
    @property
    def isSelRangeMode(self):
        return self.lSelRangeNarr[0] is not None and self.lSelRangeNarr[1] is not None
    # @property
    # def isSelRange_Changed(self):

# ListCtrl (for TRepInf)
class TListRep:
    coNorm = wx.Colour(255, 255, 255)       # text foreground color
    coNorm_rowBack = wx.Colour(0,0,0)       # row background color of normal row
    coDisable = wx.Colour(77, 77, 77)       # disable text foreground color
    coCurSel_rowBack = wx.Colour(255,0,0)   # row background color of current select row
    # coCurSubSnte_rowBack = wx.Colour(0, 90, 0)  # current play pos in which SubSnte
    coCurSubSnte_rowBack = coCurSel_rowBack  # current play pos in which SubSnte
    def __init__(self, rep: TRepInf,  zli: ULC.UltimateListCtrl, fm):
        self.rep = rep
        self.zli = zli
        self.fmMain = fm
        # self.coBack = wx.Colour(0,0,0)
        self.__bOnSel_TriggerByUser = True  #__init__ : 是否由 user mouse/keybd 選擇該列, 或由程式移至該列的
            # avoid : SetSnte_ByRow_AndPlay > update_MainSnteRange > Select > onSelect > SetSnte_ByRow_AndPlay
            # allow : mouse/key > Select > onSelect > SetSnte_ByRow_AndPlay

        self.image_list = wx.ImageList(16, 16)
        # self.image_list.Add(wx.Icon('icons/icons8-record-retro-32.ico', wx.BITMAP_TYPE_ICO))
        self.image_list.Add(wx.Icon('icons/icons8-record-retro-16.png', wx.BITMAP_TYPE_PNG))
        self.image_list.Add(wx.Icon('icons/icons8-vertical-line-dotted-16.png', wx.BITMAP_TYPE_PNG))
        # self.image_list.Add(wx.Icon('icons/icons8-border-vertical-plumpy-16.png', wx.BITMAP_TYPE_PNG))
        # self.image_list.Add(wx.Icon('icons/icons8-vertical-line-dotted-16.png', wx.BITMAP_TYPE_PNG))
        self.image_list.Add(wx.Icon('icons/icons8-timer-simple-small-16.png', wx.BITMAP_TYPE_PNG))
        self.image_list.Add(wx.Icon('icons/icons8-timer-office-m-16.png', wx.BITMAP_TYPE_PNG))
        self.zli.AssignImageList(self.image_list, wx.IMAGE_LIST_SMALL)

        self.zli.SetBackgroundColour(self.coNorm_rowBack)
        # self.zli.SetForegroundColour(wx.Colour(0,255,2))  # 連 header row 也被影響 !!
        self.zli.InsertColumn(self.rep.ezlId,       "id", width=32)
        self.zli.InsertColumn(self.rep.ezlEnablePlay, "play", ULC.ULC_FORMAT_CENTRE, width=32)
        self.zli.InsertColumn(self.rep.ezlSpeed,   LID("speed"), width=56)
        self.zli.InsertColumn(self.rep.ezlPlayCnt, LID("cnt"), width=38)
        self.zli.InsertColumn(self.rep.ezlOrgText, LID("original text"), width=670)
        self.zli.InsertColumn(self.rep.ezlTraText, LID("translated text"), width=500)
        self.zli.InsertColumn(self.rep.ezlLen,     LID("len"), width=40)
        self.zli.InsertColumn(self.rep.ezlNote,    LID("Note"), width=600)
        # self.zli.SetHeaderCustomRenderer(MyUltimateHeaderRenderer(None))
        self.zli.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.zli.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onUnSelect)
        if not rep.audio.isInit:
            return  #////

        self.reInit()

    def reInit(self):
        if not self.rep.audio.isInit:
            AddLogDug('fn TListRep.reInit -- NOT audio isInit')
            return  #////
        print(f'TListRep ctor, snte cnt={self.rep.GetSnteCnt(isMain=False)}')
        self.zli.DeleteAllItems()
        for iRow in range(self.rep.GetSnteCnt(isMain=False)):
            self.insertRow(iRow)   # include snteLong/snteMini
        print(f'TListRep ctor, zli cnt={self.zli.GetItemCount()}')

    @property
    def bOnSel_TriggerByUser(self):
        return self.__bOnSel_TriggerByUser
    @bOnSel_TriggerByUser.setter
    def bOnSel_TriggerByUser(self, newVal):
        self.__bOnSel_TriggerByUser = newVal
        AddLogDug('set bOnSel_TriggerByUser={}', newVal)

    # self.rep 內已先有資料, 然後才呼叫此函數更新 ListCtrl
    def insertRow(self, iRow):
        uSnte = self.rep.GetSnte_ByRow(iRow)
        self.zli.InsertStringItem(iRow, "")  # (iRow, text, nKind=0)  insert row
        # self.zli.SetItemBackgroundColour(iRow, self.coBack)
        self.zli.SetItemTextColour(iRow, self.coNorm)

        if uSnte.isPar:  # is Main snte
            checkBox = wx.CheckBox( self.zli, wx.ID_ANY, "", wx.DefaultPosition, wx.DefaultSize, 0)  #name=
            # checkBox.SetBackgroundColour(coBack)
            self.zli.SetItemWindow(iRow, self.rep.ezlEnablePlay, checkBox)  #expand=True
            self.updateColumn(iRow, self.rep.ezlId, uSnte.i_top)
            self.zli.SetStringItem(iRow, self.rep.ezlOrgText, uSnte.cont, [0])  # (iRow, iCol, text, lImage=[], nKind=0)
        else:               # is Sub snte
            cont = '(---copy of main snte---)'  if uSnte.isCopySnte else  uSnte.cont
            self.zli.SetStringItem(iRow, self.rep.ezlOrgText, cont, [1,2])  # (iRow, iCol, text, lImage=[], nKind=0)
        self.zli.SetStringItem(iRow, self.rep.ezlLen, f"{uSnte.end - uSnte.bgn:.1f}")
        self.zli.SetStringItem(iRow, self.rep.ezlSpeed, TAudio.MpvToGuiP(uSnte.speed_raw))
        # self.updateColumn(iRow, self.rep.ezlPlayCnt, uSnte.plcnt)
        self.updatePlayCnt(uSnte, updSubSntes=False)

    def removeRow(self, iRow):
        self.zli.DeleteItem(iRow)

    def highlightSubSnte(self, iRow, bHighlight):
        snte = self.rep.GetSnte_ByRow(iRow)
        if snte.isPar:
            return  #////
        AddLogDug("row={row}, bLight={light}", row=iRow, light=bHighlight)
        if iRow is not None:
            self.zli.SetItemBackgroundColour(iRow, self.coCurSubSnte_rowBack if bHighlight else self.coNorm_rowBack)
            self.zli.SetItemColumnImage(iRow, self.rep.ezlOrgText, [1,3] if bHighlight else [1,2])

    # def addSubRow(self):
    #     iRow = self.zli.GetFocusedItem() + 1
    #     self.zli.InsertStringItem(iRow, "")  # (iRow, text, nKind=0) to insert row
    #     self.zli.SetItemTextColour(iRow, self.coNorm)
    #     self.zli.SetStringItem(iRow, self.rep.ezlOrgText, self.rep.GetSnte_ByRow(iRow).cont)  # (iRow, iCol, text, lImage=[], nKind=0)

    def SelectRow(self, iRow):
        AddLogDug('iRow={}', iRow)
        self.fmMain.lire.bOnSel_TriggerByUser = False
        self.fmMain.zlRep.Select(iRow, on=True)
        unuse = self.fmMain.lire.onSelect(wx.ListEvent()) if 0 else None  # for call-ref to above line

    def onSelect(self, event):
        iRow = event.GetIndex()
        AddLogDug('iRow={}, bOnSel_TriggerByUser={}', iRow, self.bOnSel_TriggerByUser)
        #//did in onUnSelect :
        # if self.rep.isSelRangeMode:
        #     self.rep.SelRange_Cancel()

        snte = self.rep.GetSnte_ByRow(iRow)
        self.fmMain.player.SetSpeed(snte.speed)
        AddLogDug('snteRow{snte}, row={row}', snte=snte, row=iRow)
        if self.bOnSel_TriggerByUser and snte.isPar:
            self.rep.uPlan.reset()
            # if not self.rep.uPlan.NextInCnt(snte.plcnt):
            self.rep.uPlan.NextInCnt(snte.plcnt)  # init after reset,  on user change main snte
        self.rep.SetSnte_ByRow_AndPlay(iRow, changeZLC=False)   # avoid recursion
        # AddLogDug('aft_Speed={}', self.fmMain.player.Speed)
        # if snte.isSub and not snte.isCopySnte:
        if self.bOnSel_TriggerByUser and snte.isSub:  # include isCopySnte
            self.rep.SelRange_NarrSetBoth(snte.bgn, snte.end)

        self.fmMain.edNote.SetRichBuf_frXml(snte.bNote, gInfFile.uInfUnit)
        # AddLogDug('playRow={}, evtRow={}, bNote_to_Rich={}', self.rep.CurSnte_Play.iRow, snte.iRow, snte.bNote)  #bNote type = bytes
        self.bOnSel_TriggerByUser = True  # (reset to default) only disable once
        self.zli.SetItemBackgroundColour(iRow, self.coCurSel_rowBack)

    def onUnSelect(self, event):
        if self.rep.isSelRangeMode:
            self.rep.SelRange_Cancel(bToMain=False, bUpd=True)
        iRow = event.GetIndex()
        if iRow >= self.rep.GetSnteCnt(False):
            return  #////
        snte = self.rep.GetSnte_ByRow(iRow)  # ex row=1 時 OnMouse點選 row=0 : 此時此 snte=1, 但 CurSnte_Play 仍=0 !!!
        snte.bNote = self.fmMain.edNote.GetRichBuf_toXml(gInfFile.uInfUnit)
        # AddLogDug('playRow={}, evtRow={}, Rich_to_bNote={}', self.rep.CurSnte_Play.iRow, snte.iRow, snte.bNote)  #bNote type = bytes
        self.zli.SetItemBackgroundColour(iRow, self.coNorm_rowBack)

    def EnsureVisible(self):
        # 以下內建函數 會維持在最下方, 僅是保證可見
        #   self.zli.EnsureVisible(CurRow)
        # 故使用以下方式, 使捲動至上方 1/4 處
        CurRow = self.rep.CurSnte_Play.iRow
        self.zli.EnsureVisible(CurRow)  # !!! 按<End>至末列, 在 OnSelect 內取得 TopRow 仍為舊值, 須先此 後取TopRow 才會取得更新值 !!!
        TopRow = self.zli.GetTopItem()
        if not (TopRow <= CurRow < TopRow + self.zli.GetCountPerPage()):
            LowRow = CurRow + self.zli.GetCountPerPage() - self.zli.GetCountPerPage() // 4
            if not (0 <= LowRow < self.zli.GetItemCount()):
                LowRow = self.zli.GetItemCount() - 1
            self.zli.EnsureVisible(LowRow)
        secondTopRow = self.zli.GetTopItem()
        self.zli.EnsureVisible(CurRow)  # ensure again
        AddLogDug('CurRow={}, TopRow= {} -> {} -> {}', CurRow, TopRow, secondTopRow, self.zli.GetTopItem())

    def updateColumn(self, iRow, iCol, val):
        self.zli.SetStringItem(iRow, iCol, str(val))

    def updatePlayCnt(self, uSnte, updSubSntes):
        self.updateColumn(uSnte.iRow, self.rep.ezlPlayCnt, 'def' if uSnte.plcnt_raw is None else str(uSnte.plcnt_raw))
        bDisable = uSnte.plcnt <= 0 or (uSnte.isSub and uSnte.pEx.uPar.plcnt <= 0)
        self.zli.SetItemTextColour(uSnte.iRow, self.coDisable  if bDisable  else self.coNorm)
        iCur = self.zli.GetFocusedItem()
        self.zli.SetItemBackgroundColour(uSnte.iRow, self.coCurSel_rowBack if uSnte.iRow == iCur else self.coNorm_rowBack)
        # ParPlcnt=0 則 Sub 皆 disable,  ParPlcnt>0 則依 SubPlcnt (ex 恢復非 disable)
        if updSubSntes and uSnte.isPar:
            for snte in uSnte.lSub:
                bDisable = snte.plcnt <= 0 or snte.pEx.uPar.plcnt <= 0
                self.zli.SetItemTextColour(snte.iRow, self.coDisable  if bDisable  else self.coNorm)


class TDrawBase:
    def __init__(self,
                 canvas :FigureCanvas,
                 axes :plt.Axes,
                 rep :TRepInf):
        self.canvas = canvas
        self.axes = axes
        self.rep = rep
        # global SelRange, 同時間最多只有一個 (when highlight/active SelRange)
        self.SelRangeArtist = None  #type: typing.Union[pltCollections.PolyCollection, None]

    def _xpos_to_time(self, xpos, tiBgn, tiEnd):
        # https://stackoverflow.com/questions/19306510/determine-matplotlib-axis-size-in-pixels
        # PS: 另有 Axes.get_tightbbox 可用
        fig = self.axes.figure
        bbox = self.axes.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

        width = bbox.width * fig.dpi  # bbox.width (inches) ==> width (pixels)
        bboxLeft = bbox.x0 * fig.dpi
        xpos -= bboxLeft  # offset axes left (convert to client pos)

        # if 0:   # all range / bgn from time 0
        #     ii = int(len(self.times) *   xpos / width)
        #     time_at_xpos = self.times[ii]
        # else:
        #     rep = self.__lRepDat[self.__Ind]
        #     time_at_xpos = rep.bgn + (rep.end - rep.bgn) * (xpos / width)
        time_at_xpos = tiBgn + (tiEnd - tiBgn) * (xpos / width)
        # print(f"x={xpos}, ti={time_at_xpos}, playing={self.isPlaying}")
        # CanFigBoWid=784.0, TrBoWid=6.0760000000000005, pixelWid=607.6, audLen=80200 => width 是準確的
        # print(f"    CanFigBoWid={self.canvasNarr.figure.bbox.width}, TrBoWid={bbox.width}, pixelWid={width}")
        return time_at_xpos

    def SelRange_draw(self, snte: USnte, tiBgn, tiEnd, bLight):
        iLeft  = find_nearest_index(self.rep.audio.times, tiBgn)
        iRight = find_nearest_index(self.rep.audio.times, tiEnd)
        # obj may be global or each-snte
        obj = self  if (snte.isPar or snte.isCopySnte) else snte.pEx
        # obj = self  if bLight else snte.pEx
        alpha = 0.75 if bLight else 0.4
        fcolor = 'white' if bLight else 'green'
        if obj.SelRangeArtist:
            obj.SelRangeArtist.remove()  # then draw new immediately
            AddLogDug('{} Art-', snte)
        obj.SelRangeArtist = self.axes.fill_between(
            self.rep.audio.times[iLeft:iRight],
            self.rep.audio.audioMin, self.rep.audio.audioMax,
            facecolor=fcolor, edgecolor = 'white', alpha=alpha)  # where=(y1 <= y2)
        self.canvas.draw_idle()
        sBgnEnd = f"bgn={tiBgn:.3f}, end={tiEnd:.3f}"
        AddLogDug('{} {} Art+, light={lig}, isPar={ispar}, isCopy={iscopy}', snte, sBgnEnd, lig=bLight, ispar=snte.isPar, iscopy=snte.isCopySnte)
    def SelRange_Cancel(self, snte: USnte, bRedraw = True):
        # obj = self  if snte.isPar else  snte.pEx
        obj = self  if (snte.isPar or snte.isCopySnte) else snte.pEx
        sArtDel = ''
        if obj.SelRangeArtist:
            sArtDel = 'Art-'
            obj.SelRangeArtist.remove()
        AddLogDug("{} {} bRedraw={bRedraw}", snte, sArtDel, bRedraw=bRedraw)
        obj.SelRangeArtist = None
        if bRedraw:
            self.canvas.draw_idle()

class TDrawNarr(TDrawBase):
    def __init__(self,
                 canvas :FigureCanvas,
                 axes :plt.Axes,
                 rep :TRepInf):
        TDrawBase.__init__(self, canvas, axes, rep)
    def xpos_to_time(self, xpos):
        snte = self.rep.CurSnte_Main
        return self._xpos_to_time(xpos, snte.bgn, snte.end)

# focus on UltimateListCtrl 時, 按下 Alt+* 時 menu 會沒反應 (不論是否 bind onKeyDown_ListRep)
# 故以本 class 完成 : other.SetFocus + SendKey, 收到 key 後, 再 zList.SetFocus
# NOTE, 不可在 onKeyDown_ListRep 內以如下方法處理 :
#   other.SetFocus + SendKey + sleep + zlRep.SetFocus : 因離開此函數後才會收到鍵, 故下次還是會在本函數收到鍵, 不但無效果 且無限迴圈 send key !!!
#   other.SetFocus + SendKey + CallAfter(zlRep.SetFocus) : 因通常都會先 zlRep.SetFocus 後收到鍵, 故結果同上
class TListKeyAlt:
    def __init__(self, fmMain):
        self.CodeSent = None
        self.fmMain = fmMain  #type: FmMain
    # 暫時 focus 至任意元件後, send Alt+*, 此時 menu 才會收到按鍵
    def SendAltKey(self, nCode):
        self.CodeSent = nCode
        self.fmMain.canvasWide.SetFocus()
        KeySm.press(nCode, [KeySm.alt])  # <---
    # focus 切回 UltimateListCtrl
    def DoneAltKey(self, event):
        if (self.CodeSent is None) or (not event.AltDown()):
            return  #////
        if self.CodeSent != event.GetKeyCode():
            AddLogInf('CodeSent={} <> CodeNew={}', self.CodeSent, event.GetKeyCode())
            return  #////
        AddLogDug('nCode={}', self.CodeSent)
        self.CodeSent = None
        self.fmMain.zlRep.SetFocus()

# noinspection PyAttributeOutsideInit
class FmMain(Forms_.FmMain):
    # 根據測試觀察, 最佳設定值是 canvasHeight=73 時 bottom=0.89;  canvasHeight=114 時 bottom=0.81
    CanvasAdjBot_OnMin = 0.89  # subplots_adjust(bottom=VALUE) on height min;    # bottom大=留白多
    CanvasAdjBot_OnMax = 0.81  # subplots_adjust(bottom=VALUE) on height max
    CanvasAdj_MinHeight = 73
    CanvasAdj_MaxHeight = 114

    def __init__(self, *args, **kwds):
        AddLogInf('FmMain.init')
        self.resized = False
        Forms_.FmMain.__init__(self, *args, **kwds)
        self.audio = TAudio()

        gInfFile.Init(self.audio)
        self.player = TPlayer(self.audio)

        # gInfFile.LoadVox("foo.mp3")
        # gInfFile.LoadVox(r'c:\DriveD\Text\English\vox\英語聽力有救了_基礎篇\Track 004.mp3')
        # gInfFile.LoadVox(r'c:\DriveD\Text\English\vox\【31版】贏戰3800\3-split_ed_TrimAnySlience\long\Track24-13.mp3')
        # gInfFile.LoadVox(r'c:\DriveD\Text\English\vox\【31版】贏戰3800\3-split_ed_TrimAnySlience\long\Track24-13xxx.mp3')
        self.rep = TRepInf(self.audio, self.player, self)
        self.lire = TListRep(self.rep, self.zlRep, fm=self)
        self.liKeyAlt = TListKeyAlt(self)
        self.msg = TMsgTip(self)
        self.timer = wx.Timer(self)

        self.canvasNarr.mpl_connect('draw_event', self.onDraw)
        # self.canvasNarr.mpl_connect('button_press_event', self.on_left_down)
        self.canvasNarr.Bind(wx.EVT_LEFT_DOWN, self.on_MouseLeft_down)
        self.canvasNarr.Bind(wx.EVT_RIGHT_DOWN, self.on_MouseRight_down)
        self.Bind(wx.EVT_ACTIVATE, self.onActivate)
        self.Bind(wx.EVT_ACTIVATE_APP, self.onActivate_App)  # 不會觸發 !
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.Bind(wx.EVT_CLOSE, self.on_SysClose)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyHook)  # 不論 focus 何在, 皆可捕捉到 !
        self.zlRep.Bind(wx.EVT_KEY_DOWN, self.onKeyDown_ListRep)
        # self.zlRep.Bind(wx.EVT_CHAR,     self.onKeyDown_ListRep)
        self.canvasWide.Bind(wx.EVT_KEY_DOWN, self.onKeyDown_canvasWide)
        self.canvasNarr.Bind(wx.EVT_KEY_DOWN, self.onKeyDown_canvasNarr)
        # self.canvasNarr.Bind(wx.EVT_CHAR,     self.onKeyDown_canvasNarr)
        self.slider_SysVol.Bind(wx.EVT_SLIDER, self.OnSlider_SysVol)
        self.slider_AppVol.Bind(wx.EVT_SLIDER, self.OnSlider_AppVol)

        self.slider_SysVol.SetValue(self.audio.SysVolume.GetSysVolume())  # get sys volume
        # self.slider_AppVol.SetValue(100)  # init app volume (100=normal)
        self.slider_AppVol.SetValue(20)  # init app volume (100=normal)
        self.player.volume = self.slider_AppVol.GetValue()  # init app volume (100=normal)
        AddLogDug('vol={}', self.player.volume)
        self.btnPlay.SetFocus()  # see TListKeyAlt
        self.Maximize()
        self.Show(True)

        # self.initNewVox()

    # first call LoadVox, then call this func
    def initNewVox(self):
        if not self.audio.isInit:
            return  #////
        self.timer.Stop()
        self.player.stop(keep_playlist=False)  # <=== 之後 audio_play() > playFile() 才會載入&播放 新的音檔 !
        self.rep.reInit()
        self.lire.reInit()
        self._init_plot()
        self._init_MainCtrl()
        self.connMove = self.BG_WaveNarr.canvas.mpl_connect('motion_notify_event', self.onMouseMove)
        self.rep._updMapping()

        # self.timer.Start(100)  # Timer interval in milliseconds

        # self.btnPlay.SetFocus()
        self.btnPlay.SetLabel(LID("Play"))
        # self.isPlaying = False   # is setter !  #導致啟動後不會移動軸 !!!
        self.lire.bOnSel_TriggerByUser = False
        self.zlRep.SetFocus()
        self.lire.SelectRow(0)    # init : 此時已 bind, 但仍不會觸發 onSelect, 原因不明

        self.tmpUnitTest()

        self.Maximize()
        self.Show(True)
        self.resized = True
        self.OnIdle(None)
        self.Bind(wx.EVT_SIZE, self.OnFrameResize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        self.audio_play()  # load vox
        self.rep.PlayPlan()
        self.lire.bOnSel_TriggerByUser = True   # init

    def OnFrameResize(self, event):
        # 注意 : 此時 canvas.GetSize() or GetClientSize() 取得值 都是上次的大小, 而非目前新的大小 !!!
        self.resized = True
        AddLogDug('resized={}', self.resized)
        event.Skip()

        # self.canvasWide.SendSizeEventToParent()
        # self.canvasWide.Layout()
        # self.canvasWide.Parent.SendSizeEvent()
        # self.canvasWide.Parent.Layout()
        # self.canvasWide.Parent.Parent.SendSizeEvent()
        # self.canvasWide.Parent.Parent.Layout()

        # dpi = self.canvasNarr.figure.dpi
        # width_inch = width_px / dpi
        # self.canvasNarr.figure.set_figheight((self.canvasWide.GetSize().y - 30) // dpi)
        # sizer = self.canvasWide.GetSizer()  #type: wx.Sizer
        # print(f'sizer size={sizer.GetSize()}, cnt={sizer.GetItemCount()}')
        # pan = self.canvasWide.Parent.Parent  #type wx.Panel
        # print(f'type pan={type(pan)}, CliSize={pan.GetClientSize()}')
        # print(f'dpi={fig.dpi}')

    def OnIdle(self, event):
        if self.resized:
            AddLogDug('resized={}', self.resized)
            self.resized = False   # reset the flag
            # GPT Q: 若h=73則r=0.89,  若h=114則r=0.81,  這樣如何算出 h=90時的 r 值
            # GPT A: 可使用線性內插法 (兩點式直線方程式) 來估算$h=90$時的$r$值, 欲求的點是 (h,r), 直線的方程式可以表示為
            #   r = r1 + (r2-r1)*(h-h1) / (h2-h1)
            # ===> (r-r1) / (r2-r1) = (h-h1) / (h2-h1);   h1=73 r1=0.89 h2=114 r2=0.81 h=90
            #   r = 0.89+(0.81-0.89)*(h-73)/(114-73) = 0.88   //h=90
            if self.canvasWide.GetSize().y < self.CanvasAdj_MinHeight:
                bot = self.CanvasAdjBot_OnMin
            else:
                bot = self.CanvasAdjBot_OnMin+(self.CanvasAdjBot_OnMax-self.CanvasAdjBot_OnMin)*(self.canvasWide.GetSize().y-self.CanvasAdj_MinHeight)/(self.CanvasAdj_MaxHeight-self.CanvasAdj_MinHeight)
            AddLogDug(f'canvas size={self.canvasWide.GetSize()}, bot={bot}, CliSi={self.canvasWide.GetClientSize()}')
            self.canvasWide.figure.subplots_adjust(left=0.005, right=0.995, top=1.0, bottom=bot)
            self.canvasNarr.figure.subplots_adjust(left=0.005, right=0.995, top=1.0, bottom=bot)
            # TODO will try :
            #   Python: Resizing the Plot Area: A Python Matplotlib Code Example
            #   https://copyprogramming.com/howto/resize-plot-area-in-python-matplotlib-code-example#google_vignette
            self.canvasWide.draw_idle()
            self.canvasNarr.draw_idle()
            # with wx.EventBlocker(self.edBottom):
            self.edBottom.SetValue(str(bot))

    def _init_MainCtrl(self):
        self.NoteBar = MyNoteBar(self)  # Note Toolbar
        self.edNote.Bind(wx.EVT_KILL_FOCUS, self.onNote_UnFocus)
        # ---------------------------- [def speed]
        lzDefSnSpeed = [self.cboDefSn_MainSpeed, self.cboDefSn_SubSpeed, self.cboDefSn_CopySpeed]  # 須符合 USnte.esntyMain/Sub/Copy 之順序
        lSpeedOpt = self.rep.lSpeedOpt
        for iType, cbo in enumerate(lzDefSnSpeed):
            # -------- val->gui
            cbo.Clear()
            for opt in lSpeedOpt:
                cbo.Append(TAudio.MpvToGuiP(opt))
            unitSp = gInfFile.uInfUnit.lDefSnteSpeed[iType]
            nVal = unitSp   if unitSp is not None else   gInfFile.uInfApp.lDefSnteSpeed[iType]
            cbo.SetSelection( np.abs(lSpeedOpt - nVal).argmin() )   # 若非完全相等, 則會找最接近者
            # -------- bind (for gui->val)
            cbo.Bind(wx.EVT_TEXT, lambda evt, snty=iType : self.onEdDefSn_Speed_Changed(evt, snty))
        # ---------------------------- [def plcnt]
        for iType, zed in enumerate([self.edDefSn_MainCnt, self.edDefSn_SubCnt, self.edDefSn_CopyCnt]):  # 須符合 USnte.esntyMain/Sub/Copy 之順序
            # -------- val->gui
            unitCnt = gInfFile.uInfUnit.lDefSntePlcnt[iType]
            unitCnt = unitCnt   if unitCnt is not None else   gInfFile.uInfApp.lDefSntePlcnt[iType]
            zed.SetValue(str(unitCnt))
            # -------- bind (for gui->val)
            zed.Bind(wx.EVT_CHAR, self.onEdDefSn_PlCnt_Char)
            zed.Bind(wx.EVT_TEXT, lambda evt, snty=iType : self.onEdDefSn_PlCnt_Changed(evt, snty))
        # ---------------------------- zHtml_TopTip
        htmlTop = """
            <p>html 測試</p>
        """
        self.zHtml_TopTip.SetPage(htmlTop)
        # "#ff7f00"
        # ---------------------------- zHtml_RightTip
        def htmlRow(sFunc, sKey):
            ss  = '<tr>'
            ss += f'<td>{sFunc}</td>'
            ss += f'<td>&lt;{sKey}&gt;</td>'  # <KEY>
            ss += '</tr>'
            return ss
        htmlRight = '<table border="1" border-collapse:collapse;' \
                    'style="font-family: Arial, sans-serif; font-size: 10px;">'
        htmlRight += '<tr style="background-color: #add8e6;">'
        htmlRight += '<th>{}</th> <th>{}</th> '.format(
            # function/hotkey of hotkey tip title
            LID('function'), LID('hotkey')
        )
        htmlRight += '</tr>'
        htmlRight += htmlRow(LID('speed dec'), 'Alt+Left')
        htmlRight += htmlRow(LID('speed add'), 'Alt+Right')
        # play count dec
        htmlRight += htmlRow(LID('count dec'), 'Left')
        # play count add
        htmlRight += htmlRow(LID('count add'), 'Right')
        htmlRight += htmlRow(LID('toggle play/pause'), 'S')
        htmlRight += '</table>'
        self.zHtml_RightTip.SetPage(htmlRight, '')
        # ----------------------------
        self.fmSet_PlayCnt = FmSet_PlayCnt(self, self)
        self.fmSet_Speed   = FmSet_Speed(self, self)
        self.__isPlaying   = False

    def _init_plot(self):
        self.axesWaveWide = self.canvasWide.figure.add_subplot(111)  #type: plt.Axes
        self.axesWaveNarr = self.canvasNarr.figure.add_subplot(111)  #type: plt.Axes
        # plt.tight_layout()
        # self.canvasWide.figure.tight_layout()
        # self.canvasWide.figure.subplots_adjust(left=0.005, right=0.995, top=1.0, bottom=self.CanvasAdjBot_OnMin)
        # self.canvasNarr.figure.subplots_adjust(left=0.005, right=0.995, top=1.0, bottom=self.CanvasAdjBot_OnMin)
        self.drawNarr = TDrawNarr(self.canvasNarr, self.axesWaveNarr, self.rep)
        if 1:
            self.panel_test.Hide()
            self.panel_test.GetParent().Layout()
        else:
            pars = self.canvasNarr.figure.subplotpars
            # self.edLeft.Freeze(); self.edRight.Freeze(); self.edTop.Freeze(); self.edBottom.Freeze()
            self.edLeft.SetValue(str(pars.left))
            self.edRight.SetValue(str(pars.right))
            self.edTop.SetValue(str(pars.top))
            self.edBottom.SetValue(str(pars.bottom))
            # self.edLeft.Thaw(); self.edRight.Thaw(); self.edTop.Thaw(); self.edBottom.Thaw()
        
        for axes in [self.axesWaveWide, self.axesWaveNarr]:
            axes.patch.set_facecolor('black')
            axes.plot(self.audio.times, self.audio.audio_data, linewidth=0.5)
            axes.get_yaxis().set_visible(False)  # 不顯示 Y 軸
            # print(f"font size={axes.get_xticklabels()[0].get_fontsize()}")
            axes.tick_params(axis='x', labelsize=8)
            # axes.xaxis.set_major_locator(ticker.MaxNLocator(5))
            # axes.set_title("Audio Waveform")
            # axes.set_xlabel("Time (s)")
            # axes.set_ylabel("Amplitude")
            axes.set_xlim(0, self.audio.duration)  # xPos->time 才會正確, 右邊也才不會有很多空白

        # self.cur = TCrossCursor(self.BG_WaveNarr, self.axesWaveNarr)
        # self.cur.EnableEvent(False)
        lineprops = {}
        lineprops['animated'] = True  # for blit, draw_artist() 時才會真正畫
        self.BG_WaveNarr = TBackground(self.canvasNarr, autoSaveBg_OnDraw=True)
        self.BG_WaveWide = TBackground(self.canvasWide, autoSaveBg_OnDraw=True)
        self.curLine = self.axesWaveNarr.axvline(20, color='#c78541', visible=False, **lineprops)  #type: plt.Line2D
        self.vLine = self.axesWaveNarr.axvline(x=0, color='r', linestyle='--', linewidth=2, **lineprops)  #type: plt.Line2D

        # ylim = self.axesWaveWide.get_ylim()
        # self.RngBox = patches.Rectangle((0, ylim[0]), 1, ylim[1] - ylim[0], linewidth=1, edgecolor='r', facecolor='none', animated=True)
        self.RngBox = patches.Rectangle((0, self.audio.audioMin + 1), 1, self.audio.audioMax - self.audio.audioMin - 1,
                                        linewidth=1, edgecolor='r', facecolor='none', animated=True)  # range of Narr, draw in Wide
        self.axesWaveWide.add_patch(self.RngBox)  # Rectangle((x, y)=左下角!!, width, height, ...)
        # self.axesWaveWide.draw_artist(self.RngBox)
        self.update_MainSnteRange()
        # self.lire.SelectRow(self.rep.CurSnte_Play.iRow)

    # fast update curLine / vLine
    def _BlitNarr(self):
        self.BG_WaveNarr.restore()
        if self.vLine.get_visible():
            self.vLine.axes.draw_artist(self.vLine)
        if self.curLine.get_visible():
            self.curLine.axes.draw_artist(self.curLine)
        self.BG_WaveNarr.blit()

    def onMouseMove(self, event):
        if (event.inaxes is None) or event.inaxes != self.axesWaveNarr:  return  # ////
        if not self.BG_WaveNarr.canvas.widgetlock.available(self): return  # //// ?

        self.curLine.set_xdata((event.xdata, event.xdata))
        self.curLine.set_visible(True)
        self._BlitNarr()

    def on_MouseLeft_down(self, event):
        xpos, _ = event.GetPosition()  # if via Bind
        # xpos = event.x               # if via mpl_connect
        time_at_xpos = self.drawNarr.xpos_to_time(xpos)
        self.player.set_TimePos(time_at_xpos,  'MouseLeft')
        self.rep.SelRange_NarrSetOne(0, time_at_xpos)
        self.update_vline_position()
        AddLogDug("{}, ax={}", self.rep.CurSnte_Play, self.axesWaveNarr.xaxis)

    def on_MouseRight_down(self, event):
        if self.rep.lSelRangeNarr[0] is None:
            return  #////
        xpos, _ = event.GetPosition()  # if via Bind
        # xpos = event.x               # if via mpl_connect
        time_at_xpos = self.drawNarr.xpos_to_time(xpos)
        self.rep.SelRange_NarrSetOne(1, time_at_xpos)

    def onBtnPlay(self, event):  # wxGlade: FmMain.<event_handler>
        #if event.GetEventObject().GetValue():
        AddLogDug('bef playing={}', self.isPlaying)
        if self.isPlaying:
            self.audio_pause()
        else:
            self.audio_play()

    @property
    def isPlaying(self):
        # return self.btnPlay.GetValue()   # 此方式似乎有 bug ?
        return self.__isPlaying
    def setPlaying(self, bState):
        # button play for playing or paused
        self.btnPlay.SetLabel(LID("Play(ing)")  if bState else  LID("Play(ed)"))
        self.btnPlay.SetValue(bState)
        self.__isPlaying = bState
        AddLogDug('isPlaying={}', bState)

    def audio_play(self):
        if self.player.idle_active:
            AddLogDug('a vol={}', self.player.volume)
            self.player.playFile(self.audio.audio_fullFna)
        AddLogDug('b')
        self.player.playFrom_TimePos()
        self.setPlaying(True)
        self.timer.Start(100)  # Timer interval in milliseconds

    def audio_pause(self):
        # 導致卡住不播放 !!!
        # isPlaying = self.isPlaying
        # AddLogDug('isPlaying={}', isPlaying)
        # if not isPlaying:

        AddLogDug('p')
        if True:
            self.player.pause = True
            self.timer.Stop()
            self.setPlaying(False)

    """
    #啟動程式後, 會先 onSelect > audio_play
    update_vline_position : time_pos is None
    on_timer : TimePos > eiEnd
    on_timer : TimePos > eiEnd
    ...
    on_timer : TimePos=None
    update_vline_position : time_pos is None
    on_timer : TimePos > eiEnd
    on_timer : TimePos > eiEnd
    ...
    on_timer : TimePos=None
    update_vline_position : time_pos is None
    on_timer : TimePos > eiEnd
    on_timer : TimePos > eiEnd
    ...
    """
    def on_timer(self, event):
        # if not self.isPlaying:
        #     AddLogDug('isPlaying==false, btnP={}, idle={}, pos={}', self.btnPlay.GetValue(), self.player.idle_active, self.playTimePos.TimePos)
        #     # [2024-02-06 08:32:01,697 DEB] <on_timer> isPlaying==false, btnP=True, idle=True, pos=None
        #     return  #////
        self.rep.onPlayTimer()
        self.update_vline_position()

    # change plot range of SnteLong waveform
    def update_MainSnteRange(self):
        # sntePlay = self.rep.CurSnte_Play    #is mainSnte or subSnte
        snteMain = self.rep.CurSnte_Main    #is mainSnte always
        self.axesWaveNarr.set_xlim(snteMain.bgn, snteMain.end)
        self.canvasNarr.draw_idle()  # 強制重新繪製畫布, OnDraw 時自動 BG_WaveNarr.saveToBg()

        self.BG_WaveWide.restore()
        self.RngBox.set_x(snteMain.bgn)
        self.RngBox.set_width(snteMain.end - snteMain.bgn)
        # self.RngBox.axes.draw_artist(self.RngBox)
        self.axesWaveWide.draw_artist(self.RngBox)
        self.BG_WaveWide.blit()
        # AddLogDug('zli cnt={}, iRow={}', self.zlRep.GetItemCount(), sntePlay.iRow)

    def update_vline_position(self):
        timepos = self.player.TimePos
        if timepos is None:
            AddLogERR('time_pos is None')
            return  #////
        # print(f'{timepos:.2f} ', end='')
        self.vLine.set_xdata([timepos])
        self.vLine.set_visible(True)
        self._BlitNarr()
        self.edCurPos.SetValue(f"{timepos:.2f} secs")
        # try:
        #     self.edCurPos.SetValue(f"{timepos:.2f} secs")
        # except TypeError as e:
        #     AddLogERR('TimePos={}, ERR: {}', timepos, e)
        # except Exception as e:
        #     AddLogERR('TimePos={}, ERR: {}', timepos, e)
        # self.canvasNarr.draw_idle()  # 強制重新繪製畫布
        # wx.Yield()

    def onDraw(self, event):
        pass

    def onNote_UnFocus(self, event):
        # did in onUnSelect()
        # snte = self.rep.CurSnte_Play
        # snte.bNote = self.edNote.GetRichBuf_toXml(gInfFile.uInfUnit)
        # AddLogDug('playRow={} UnFocus, Rich_to_bNote={}', snte.iRow, snte.bNote)  #bNote type = bytes
        event.Skip()  # <--- propagate / 使能繼續傳遞此 event !!

    def onKey_get_(self, event):
        # if not self.initDone:
        #     event.Skip()  # <--- propagate / 使能繼續傳遞此 event !!
        #     return #////
        nCode = event.GetKeyCode()
        modifiers = event.GetModifiers()
        if 32 <= event.UnicodeKey <= 126:
            sChar = chr(event.UnicodeKey)
        else:
            sChar = GetKeyboardName(nCode)
        AddLogDug('mod={mod} code={code} char="{ch}"', code=nCode, mod=modifiers, ch=sChar)
        return nCode, modifiers, sChar

    def onKeyHook(self, event):
        bPropagate = True
        nCode, modifiers, sChar = self.onKey_get_(event)
        wnd = wx.Window.FindFocus()  #type: wx.Window
        AddLogDug('focus_name={}, class={}', wnd.Name, wnd.ClassName)
        if modifiers == wx.WXK_NONE:
            if nCode == wx.WXK_ESCAPE:
                if not self.audio.isInit:
                    self.on_SysClose(event)
                elif self.rep.SelRange_Cancel(bToMain=False, bUpd=True):
                    pass  # to cancel SelRange
                elif fmBase.FmSpdCntBase.DlgShowing:
                    pass  # to close Dlg
                else:
                    snte = self.rep.CurSnte_Play
                    snte.bNote = self.edNote.GetRichBuf_toXml(gInfFile.uInfUnit)
                    # AddLogDug('playRow={} onExit, Rich_to_bNote={}', snte.iRow, snte.bNote)  #bNote type = bytes
                    gInfFile.SaveUnit()   # on exit app
                    gInfFile.SaveApp()   # on exit app
                    self.on_SysClose(event)
            # focus on ULC 時, 收不到 Enter/Up/Down/... 的 KeyDown event, 故由 onKeyHook 代轉
            elif nCode in [wx.WXK_RETURN, wx.WXK_UP, wx.WXK_DOWN] \
                    and isinstance(wnd, ULC.UltimateListCtrl):   # wnd.Name == 'UltimateListCtrl'
                # if nCode != wx.WXK_DOWN:  #TEST
                self.onKeyDown_ListRep(event)
                bPropagate = False
            # 以下的缺點 : 在 edit 內想移動 caret, 也會變成 change play cnt, 故只在 onKeyDown_ListRep 內處理
            # elif nCode in [wx.WXK_LEFT, wx.WXK_RIGHT]:
            #     self.rep.ChgPlCnt_byKey(-1 if nCode == wx.WXK_LEFT else 1)
        elif event.AltDown():    # elif modifiers == wx.WXK_ALT:
            pass
        # elif nCode == ord('I') and modifiers == wx.MOD_ALT:
        #     self.onBtn1(event)
        if bPropagate:
            event.Skip()  # <--- propagate / 使能繼續傳遞此 event !!

    def onKeyDown_ListRep(self, event):
        nCode, modifiers, sChar = self.onKey_get_(event)
        # include key : Alt+Left / Alt+Right / Left / Right
        if nCode in [wx.WXK_LEFT, wx.WXK_RIGHT]:
            iRow = self.zlRep.GetFirstSelected()
            rc = self.zlRep.GetSubItemRect(iRow, self.rep.ezlOrgText, ULC.ULC_RECT_ICON)  #第3個參數沒作用 !
            pntPar = self.panel_zlRep.GetScreenPosition()
            pntFm = wx.Point(rc.left + pntPar.x + 32, rc.top + pntPar.y)
            if modifiers == wx.WXK_NONE:
                self.fmSet_PlayCnt.fmShow(pntFm)  # change play cnt
                self.fmSet_PlayCnt.onKeyDown_pcnt(event)
            elif event.AltDown():
                self.fmSet_Speed.fmShow(pntFm)  # change play speed
                self.fmSet_Speed.onKeyDown_spd(event)
        # ex Enter/Del
        elif modifiers == wx.WXK_NONE:
            # focus on ULC 時, 收不到 <Enter> 的 KeyDown event;
            # 故此時是由 onKeyHook 呼叫 onKeyDown_ListRep 的 !
            if nCode == wx.WXK_RETURN:
                self.rep.SelRange_AddOrModify()
            elif nCode == wx.WXK_DELETE:
                self.rep.SelRange_Del()
            elif nCode in [wx.WXK_UP, wx.WXK_DOWN]:
                self.rep.SetSnte_NextMain_AndPlay( -1 if nCode == wx.WXK_UP else 1 ,  bPlay=False)
                self.rep.uPlan.reset()  # user go next mainSnte
                self.rep.PlayPlan()
            elif sChar == 'S':
                self.onBtnPlay(None)
        # let menu key can work  when focus on UltimateListCtrl
        elif event.AltDown() and ord('A') <= nCode <= ord('Z'):    # elif modifiers == wx.WXK_ALT:
            self.liKeyAlt.SendAltKey(nCode)

        # if nCode != wx.WXK_UP:
        # event.Skip()  # <--- propagate / 使能繼續傳遞此 event : ex 造成 <Down> 按1下變2下 !!!

    def onKeyDown_canvasWide(self, event):
        self.liKeyAlt.DoneAltKey(event)
        event.Skip()  # <--- propagate / 使能繼續傳遞此 event !!

    def onKeyDown_canvasNarr(self, event):
        nCode, modifiers, sChar = self.onKey_get_(event)
        event.Skip()  # <--- propagate / 使能繼續傳遞此 event !!
        if modifiers == wx.WXK_NONE and nCode in [wx.WXK_RETURN, wx.WXK_DELETE]:
            self.onKeyDown_ListRep(event)

    def on_SysClose(self, event):
        self.timer.Stop()
        if hasattr(self, 'connMove') and self.connMove:
            self.BG_WaveNarr.canvas.mpl_disconnect(self.connMove)
        # if result == wx.ID_YES:
        #     event.Skip()  # 繼續處理關閉事件
        # else:
        #     event.Veto()  # 取消關閉事件
        print('on close')

        self.player.stop(keep_playlist=False)
        event.Skip()  # 繼續處理關閉事件
        # 必須呼叫 exit() 才會完全結束程式
        # 以下都無效 :
        #   self.player.wait_for_playback(timeout=1)
        #   self.Destroy()
        #   thread1 = threading.Thread(target=self.inThr_stopMpv)
        #       thread1.start()
        #       thread1.join()
        #   self.player.terminate()
        #   self.player.quit(0)
        exit(0)

    def onEd4_Changed(self, event):  # wxGlade: FmMain.<event_handler>
        if self.edLeft.GetValue() == '' or self.edRight.GetValue() == '' or self.edTop.GetValue() == '' or self.edBottom.GetValue() == '':
            return  #////
        self.canvasNarr.figure.subplots_adjust(left=float(self.edLeft.GetValue()), right=float(self.edRight.GetValue()), top=float(self.edTop.GetValue()), bottom=float(self.edBottom.GetValue()))
        self.canvasNarr.draw_idle()

    def OnSlider_AppVol(self, event):
        # print(f'Obj={event.GetEventObject().GetValue()}')
        # print(f'geV={self.slider_AppVol.GetValue()}')
        self.player.volume = self.slider_AppVol.GetValue()  # 0..100
        # AddLogInf('vol={}', self.player.volume)
    def OnSlider_SysVol(self, event):
        self.audio.SysVolume.SetSysVolume(self.slider_SysVol.GetValue())

    def onEdDefSn_PlCnt_Char(self, event):
        # zed = event.GetEventObject()  #type: wx.TextCtrl
        # value = zed.GetValue()  #type: str
        keycode = event.GetKeyCode()
        if keycode in [wx.WXK_DELETE, wx.WXK_BACK, wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_HOME, wx.WXK_END]\
                or ord('0') <= keycode <= ord('9'):
            event.Skip()  # <--- propagate / 才能出現於 wx.TextCtrl !!
        else:
            # AddLogInf('not allow code={}', keycode)
            return  #////   avoid event.Skip() : 不允許輸入該 char !!

    # [def speed] gui->val
    def onEdDefSn_Speed_Changed(self, event, snty):
        cbo = event.GetEventObject()  #type: wx.ComboBox
        AddLogDug('[def speed] gui->val : cboIdx={}, snty={}', cbo.GetSelection(), snty)   # ex cbo.GetValue() == "66%"
        gInfFile.uInfUnit.lDefSnteSpeed[snty] = self.rep.lSpeedOpt[cbo.GetSelection()]

    # [def plcnt] gui->val
    def onEdDefSn_PlCnt_Changed(self, event, snty):
        if not self.msg.CheckContent():
            return  #////   something error need user fix
        zed = event.GetEventObject()  #type: wx.TextCtrl
        AddLogDug('[def plcnt] gui->val : edVal={}, snty={}', zed.GetValue(), snty)
        gInfFile.uInfUnit.lDefSntePlcnt[snty] = int(zed.GetValue())

    def mnFileOpen(self, event):  # wxGlade: FmMain.<event_handler>
        with wx.FileDialog(self, "Open audio file",
                           wildcard="audio files (*.mp3;*.wav)|*.mp3;*.wav",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlgFi:
            if dlgFi.ShowModal() == wx.ID_CANCEL:
                return  #////
            fullFna = dlgFi.GetPath()
        gInfFile.LoadVox(fullFna, self)
        self.initNewVox()
        event.Skip()



    def mnSetSnte_all(self, event):  # wxGlade: FmMain.<event_handler>
        # print("Event handler 'mnSetSnte_all' not implemented!")
        # event.Skip()
        pass
    def mnSetSnte_MainSntes(self, event):  # wxGlade: FmMain.<event_handler>
        pass
    def mnSetSnte_SubSntes(self, event):  # wxGlade: FmMain.<event_handler>
        pass
    def mnSetSnte_CopySntes(self, event):  # wxGlade: FmMain.<event_handler>
        pass

    def onActivate(self, event):
        # AddLogInf('FmMain GetActive={}', event.GetActive())
        if event.GetActive():
            self.slider_SysVol.SetValue(self.audio.SysVolume.GetSysVolume())  # get/update sys volume
            # if self.DlgShowing:
            #     self.DlgShowing.Raise()  # 將對話框置于頂層
        event.Skip()

    def onActivate_App(self, event):
        AddLogInf('FmMain GetActive={}', self.Raise())
        # if event.GetActive():
        #     self.Raise()  # 將對話框置于頂層
        event.Skip()

    def tmpUnitTest(self):
        # item = self.rep.uPlan.CurItem
        # while True:
        #     AddLogInf('item: {}', item)
        #     item = self.rep.uPlan.NextItem()
        #     if not item:
        #         break  #////
        assert self.rep.uPlan.iInCnt == 0
        assert TRepInf.eppMain == 0
        assert TRepInf.eppSub == 1
        assert TRepInf.eppCopy == 2
        AddLogDug('CurSnte_Main {}', self.rep.CurSnte_Main)
        # for i in range(30):
        #     self.rep.PlayPlan()
        # self.rep.uPlan.reset()
        # self.rep.SetSnte_ByRow(0)

        # snte = self.rep.CurSnte_Play
        # AddLogDug('T snte :{}', snte)
        # assert snte.plcnt_raw is None
        # assert snte.plcnt == 2

        # AddLogDug('Unit.defSpeed={}', gInfFile.uInfUnit.lDefSnteSpeed[USnte.esntyMain] )
        # AddLogDug('App.defSpeed={}', gInfFile.uInfApp.lDefSnteSpeed[USnte.esntyMain] )

        # gInfFile.uInfUnit.lDefSntePlcnt[1] = None
        # gInfFile.SaveUnit()
        # self.on_SysClose(wx.ListEvent())

class FmSet_PlayCnt(fmBase.FmSpdCntBase):
    def __init__(self, fmMain, *args, **kwds):
        Forms_.FmSpdCnt.__init__(self, *args, **kwds)
        self.fmMain = fmMain  #type: FmMain
        # setting of play-count
        self.btnDel.SetLabel(LID('set to 0 //cnt'))
        # setting of play-count
        self.btnEnd.SetLabel(LID('set to Def //cnt'))
        # setting of play-count
        self.btnUp.SetLabel(LID('go Prev snte //cnt'))
        # setting of play-count
        self.btnDown.SetLabel(LID('go Next snte //cnt'))
        # setting of play-count
        self.btnLeft.SetLabel(LID('count - 1 //cnt'))
        # setting of play-count
        self.btnRight.SetLabel(LID('count + 1 //cnt'))

        self.sizer_frame.Hide(self.zHtml, recursive=True)
        # self.sizer_top.Layout()   # <--- 似會自動 .Layout();  雖不必主動呼叫, 但 sizer_top 須存在 !
        self.Fit()

        # self.Bind(wx.EVT_ACTIVATE_APP, self.on_activate)  # 不會觸發 !
        self.Bind(wx.EVT_ACTIVATE, self.on_activate)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown_pcnt)

    def on_activate(self, event):
        # AddLogInf('GetActive={}', event.GetActive())
        if event.GetActive():
            # self.fmMain.Show()
            # self.Raise()  # 將對話框置于頂層
            pass
        else:   # 當 form unfocus 時就關閉 form
            self.fmHide()
        event.Skip()

    def onKeyDown_pcnt(self, event):
        nCode, modifiers, sChar = self.fmMain.onKey_get_(event)
        if modifiers == wx.WXK_NONE:
            if nCode == wx.WXK_ESCAPE:
                self.fmHide()
            elif nCode == wx.WXK_DELETE:
                self.onBtnDel(event)
            elif nCode == wx.WXK_END:
                self.onBtnEnd(event)
            elif nCode == wx.WXK_LEFT:
                self.onBtnLeft(event)
            elif nCode == wx.WXK_RIGHT:
                self.onBtnRight(event)
            elif nCode == wx.WXK_UP:
                self.onBtnUp(event)
            elif nCode == wx.WXK_DOWN:
                self.onBtnDown(event)
        elif event.AltDown():    # elif modifiers == wx.WXK_ALT:
            pass
        # elif nCode == ord('I') and modifiers == wx.MOD_ALT:
        #     self.onBtn1(event)

        # event.Skip()  # <--- propagate / 使能繼續傳遞此 event !!

    def onBtnDel(self, event):  # wxGlade: FmSpdCnt.<event_handler>
        self.fmMain.rep.CurSnte_Play.plcnt = 0
        self.fmMain.lire.updatePlayCnt(self.fmMain.rep.CurSnte_Play, updSubSntes=True)
    def onBtnEnd(self, event):  # wxGlade: FmSpdCnt.<event_handler>
        self.fmMain.rep.CurSnte_Play.plcnt = None
        self.fmMain.lire.updatePlayCnt(self.fmMain.rep.CurSnte_Play, updSubSntes=True)
    def onBtnLeft(self, event):  # wxGlade: FmSpdCnt.<event_handler>
        self.fmMain.rep.ChgPlCnt_byKey(-1)
    def onBtnRight(self, event):  # wxGlade: FmSpdCnt.<event_handler>
        self.fmMain.rep.ChgPlCnt_byKey(1)
    def onBtnUp(self, event):  # wxGlade: FmSpdCnt.<event_handler>
        self.fmHide()
        iRow = self.fmMain.zlRep.GetFirstSelected() - 1
        if iRow >= 0:
            self.fmMain.lire.SelectRow(iRow)
    def onBtnDown(self, event):  # wxGlade: FmSpdCnt.<event_handler>
        self.fmHide()
        iRow = self.fmMain.zlRep.GetFirstSelected() + 1
        if iRow < self.fmMain.zlRep.GetItemCount():
            self.fmMain.lire.SelectRow(iRow)

class FmSet_Speed(fmBase.FmSpdCntBase):
    def __init__(self, fmMain, *args, **kwds):
        Forms_.FmSpdCnt.__init__(self, *args, **kwds)
        self.fmMain = fmMain  #type: FmMain
        # setting of play-speed
        self.btnDel.SetLabel(LID('set to slowest //spd'))
        # setting of play-speed
        self.btnEnd.SetLabel(LID('set to Def //spd'))
        # setting of play-speed
        self.btnUp.SetLabel(LID('go Prev snte //spd'))
        # setting of play-speed
        self.btnDown.SetLabel(LID('go Next snte //spd'))
        # setting of play-speed
        self.btnLeft.SetLabel(LID('slower //spd'))
        # setting of play-speed
        self.btnRight.SetLabel(LID('faster //spd'))

        self.zHtml.SetPage('TEST HTML')
        self.Fit()
        # self.Bind(wx.EVT_ACTIVATE_APP, self.on_activate)  # 不會觸發 !
        self.Bind(wx.EVT_ACTIVATE, self.on_activate)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown_spd)

    def on_activate(self, event):
        # AddLogInf('GetActive={}', event.GetActive())
        if event.GetActive():
            # self.fmMain.Show()
            # self.Raise()  # 將對話框置于頂層
            pass
        else:   # 當 form unfocus 時就關閉 form
            self.fmHide()
        event.Skip()

    def onKeyDown_spd(self, event):
        nCode, modifiers, sChar = self.fmMain.onKey_get_(event)
        if modifiers == wx.WXK_NONE:
            if nCode == wx.WXK_ESCAPE:
                self.fmHide()
            elif nCode in [wx.WXK_LEFT, wx.WXK_RIGHT]:
                self.fmMain.rep.ChgSpeed_byKey(-1  if nCode == wx.WXK_LEFT else  1)
            elif nCode == wx.WXK_DELETE:
                self.onBtnDel(event)
            elif nCode == wx.WXK_END:
                self.onBtnEnd(event)
            elif nCode == wx.WXK_UP:
                self.onBtnUp(event)
            elif nCode == wx.WXK_DOWN:
                self.onBtnDown(event)
        elif event.AltDown():    # elif modifiers == wx.WXK_ALT:
            if nCode in [wx.WXK_LEFT, wx.WXK_RIGHT]:
                self.fmMain.rep.ChgSpeed_byKey(-1  if nCode == wx.WXK_LEFT else  1)
            pass
        # elif nCode == ord('I') and modifiers == wx.MOD_ALT:
        #     self.onBtn1(event)

        # event.Skip()  # <--- propagate / 使能繼續傳遞此 event !!

    def onBtnDel(self, event):  # wxGlade: FmSpdCnt.<event_handler>
        self.fmMain.rep.ChgSpeed_byKey(-99)
    def onBtnEnd(self, event):  # wxGlade: FmSpdCnt.<event_handler>
        self.fmMain.rep.CurSnte_Play.speed = None
        self.fmMain.rep.ChgSpeed_byKey(0)
    def onBtnUp(self, event):  # wxGlade: FmSpdCnt.<event_handler>
        self.fmHide()
        iRow = self.fmMain.zlRep.GetFirstSelected() - 1
        if iRow >= 0:
            self.fmMain.lire.SelectRow(iRow)
    def onBtnDown(self, event):  # wxGlade: FmSpdCnt.<event_handler>
        self.fmHide()
        iRow = self.fmMain.zlRep.GetFirstSelected() + 1
        if iRow < self.fmMain.zlRep.GetItemCount():
            self.fmMain.lire.SelectRow(iRow)


class MyNoteBar(Forms_.MyToolBar):
    def __init__(self, fmMain : FmMain):
        self.fmMain = fmMain
        super().__init__(self.fmMain.panel_Notebar, -1)
        self.AddPlainBtn(wx.Colour(0, 0, 0), wx.Colour('green') , 'B', self.on_tool_click_1)
        self.AddPlainBtn(wx.Colour(0, 0, 0), wx.Colour('red')   , 'Tx', self.on_tool_click_1)
        self.AddPlainBtn(wx.Colour('yellow'), wx.Colour(0, 0, 0), 'Tx', self.on_tool_click_2)
        self.AddPlainBtn(wx.Colour(0, 0, 0), wx.Colour('red')   , 'B', self.on_tool_click_1)
        self.AddPlainBtn(wx.Colour('yellow'), wx.Colour(0, 0, 0), 'B', self.on_tool_click_2)
        self.Realize()
        # self.sizer_NoteToolbar.Insert(0, self.NoteBar, 0, wx.EXPAND, 0)
        self.fmMain.sizer_Notebar.Add(self, 0, wx.EXPAND, 0)
        self.fmMain.sizer_Notebar.Layout()
        # self.x.Layout()

    def AddPlainBtn(self, bg_color, text_color, text, event_handler):
        bmp = self.create_bitmap(bg_color, text_color, text)
        obj = self.AddTool(wx.ID_ANY, '', bmp, shortHelp=LID("highlight color of selected text"))
        self.Bind(wx.EVT_TOOL, event_handler, obj)

    # 產生 icon : 純色背景, 圖形為文字 text
    def create_bitmap(self, bg_color, text_color, text):
        bmp_width  = 24
        bmp_height = 24
        font_size  = 16 if len(text) > 1 else 20
        font_weight = wx.FONTWEIGHT_NORMAL if len(text) > 1 else wx.FONTWEIGHT_BOLD

        bmp = wx.Bitmap(bmp_width, bmp_height)
        with SelectAndFree(wx.MemoryDC(), bmp, wx.NullBitmap) as dc:
            font = wx.Font(font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, font_weight)
            dc.SetBackground(wx.Brush(bg_color))
            dc.Clear()
            dc.SetTextForeground(text_color)
            dc.SetFont(font)

            text_width, text_height = dc.GetTextExtent(text)
            text_x = (bmp_width - text_width) // 2
            text_y = (bmp_height - text_height) // 2
            dc.DrawText(text, text_x, text_y)
        return bmp

    def on_tool_click_1(self, event):
        tool_id = event.GetId()
    def on_tool_click_2(self, event):
        tool_id = event.GetId()


class MyApp(wx.App):
    def OnInit(self):
        # self.frame = forms__.MyFrame(None, wx.ID_ANY, "") # 若不繼承, 直接使用 forms__.MyFrame
        self.frame = FmMain(None, wx.ID_ANY, "")           # 若透過繼承的 MyFrame
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# if __name__ == '__main__':
TCustomLog.SetLogFile('./pjMusicRepeater.log')
TCustomLog.SetLogLevel(fileLv = logging.DEBUG, consoleLv = logging.INFO)
AddLogInf('='*90)
gApp = MyApp(0)
gApp.MainLoop()
