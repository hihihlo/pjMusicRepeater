# import os, sys
# from cusLogger import *
import time

import numpy as np
# from typing import List
# import typing
# import pathlib
from cusLogger import *
from pydub import AudioSegment
import mpv

import ctypes
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume   # pip install pycaw


#======================================================================================================================
# Wrap around AudioSegment / SysVolume
class TAudio:
    class TSysVolume:
        def __init__(self):
            self.oAudDevices = AudioUtilities.GetSpeakers()
            self.oAudInterface = self.oAudDevices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.oVolume = ctypes.cast(self.oAudInterface, ctypes.POINTER(IAudioEndpointVolume))
            self.oVolume.SetMute(False, None)  #防止被手動設定為靜音(關閉音量)
        # val = 0..100
        def SetSysVolume(self, val):
            self.oVolume.SetMasterVolumeLevelScalar(val / 100, None)  # 0..1
        def GetSysVolume(self):
            return int(self.oVolume.GetMasterVolumeLevelScalar() * 100)

    # @classmethod
    # def GuiToMpv(cls, nGui) -> float:
    #     return nGui / 100
    # @classmethod
    # def MpvToGui(cls, nMpv) -> int:
    #     return int(nMpv * 100)
    @classmethod
    def MpvToGuiP(cls, nMpv) -> str:
        return 'def' if nMpv is None else f'{int(nMpv * 100)}%'

    def __init__(self):
        self.SysVolume = self.TSysVolume()
        self.audio_fullFna = None
        self.audio_data = None
        self.audioSeg = None
        self.audioMax = None
        self.audioMin = None
        self.sample_width = None
        self.frame_rate = None
        self.num_channels = None
        self.duration = None
        self.times = None

    @property
    def isInit(self):
        return self.audio_fullFna is not None

    def LoadVox_(self, voxFullFna):
        # self.audio_fullFna = "shortMutter.mp3"
        try:
            self.audioSeg = AudioSegment.from_mp3(voxFullFna)
        except Exception as e:
            sMsg = f'load audio file fail : {e}\nfile={voxFullFna}'
            AddLogERR('{}', sMsg)
            wx.MessageBox( sMsg, 'Music Repeater', wx.OK | wx.ICON_ERROR)
            self.audio_fullFna = None
            return False  #////
        self.audio_fullFna = voxFullFna
        self.sample_width = self.audioSeg.sample_width #2
        self.frame_rate = self.audioSeg.frame_rate
        self.num_channels = self.audioSeg.channels     #1
        self.duration = len(self.audioSeg) / 1000.0
        #print(f'duration={self.duration}, len audio_data={len(self.audio_data)}')  #duration=12.952 (secs), len audio_data=571183
        #print(f'frame_rate={self.frame_rate}, 1/F={1/self.frame_rate}') #frame_rate=44100, 1/F=2.26757369614
        #https://ithelp.ithome.com.tw/articles/10233646
        if True:
            self.audio_data = np.array(self.audioSeg.get_array_of_samples())
            self.times = np.linspace(0, self.duration, len(self.audio_data))                    #  start, stop, num(cnt)
            # self.times = np.linspace(0, self.duration, len(self.audioSeg.get_array_of_samples()))               #  start, stop, num(cnt)
            # self.times = np.arange(0, self.duration, 1/self.frame_rate)  # then cnt == 571184;   start, stop, step, dtype
        else:
            points_per_second = 1
            interval = int(self.frame_rate / points_per_second)
            self.audio_data = np.array(self.audioSeg.get_array_of_samples()[::interval])
            self.times = np.linspace(0, self.duration, len(self.audio_data))
        # print(f"audio data max={np.max(self.audio.audio_data)}, min={np.min(self.audio.audio_data)}")
        self.audioMax = int(np.max(self.audio_data))
        self.audioMin = int(np.min(self.audio_data))
        return True  #////

# Wrap mpv
class TPlayer:
    MinSpeed = 0.5  # (tip: 1.0 is normal)  # 暫無法改變, 只能當成 const, 小於此值會被 mpv 停止播放 !
    # def ResetAudioArg(self):
    #     self.player._set_property('min-speed', self.MinSpeed / 100)  # mpv property does not exist : min-speed, min_speed
    def __init__(self, audio : TAudio):
        self.audio = audio
        self.player_ = mpv.MPV(input_default_bindings=True)  # Type: mpv.MPV
        # player_ = mpv.MPV(ytdl = False, video = False)
        # self.player_.register_key_binding('CLOSE_WIN', 'quit')
        # self.player_.loop_file = 'inf'
        # self.player_.loop_playlist = 'inf'
        self.__Pre_time_pos = None

    # load & play a file (fna = file name)
    def playFile(self, fna):
        AddLogDug('PL.filename={}', fna)
        # tiBgn = time.time()
        self.player_.play(fna)
        self.player_.wait_until_playing(timeout=2)
        # self.player_.wait_for_playback()
        # to Play, 確保 idle 1->0 : 若等待時間 > tiWaitMin 則放棄, 不再等待 core-idle 變成 0
        # tiWaitMin = 1.0
        # while self.player_._get_property('core-idle') and (time.time() - tiBgn) <= tiWaitMin:
        #     time.sleep(0.001)
    def stop(self, **kwargs):
        AddLogDug('PL.stop')
        self.player_.stop(kwargs)
        # self.player_.wait_for_shutdown(timeout=3)  # will exception !!
        # self.player_.wait_until_paused(timeout=2)
    # idle_active == True 的原因 :
    #   - no file is loaded (與是否 pause 無關 !!)
    #   - 整個音檔播完後
    #   - stop() 後
    #   註 : 以上情況也會 timepos = None !
    @property
    def idle_active(self):
        return self.player_.idle_active
    @property
    def pause(self):
        return self.player_.pause
    @pause.setter
    def pause(self, newVal):
        bIdleActive = self.idle_active
        AddLogDug('PL.pause {} => {},  idle_active={}', self.player_.pause, newVal, bIdleActive)
        if self.player_.pause == newVal or bIdleActive:
            return  #////   pause 0->0 or 1->1
        tiBgn = time.time()   # .time / .sleep 皆以[秒]為單位
        self.player_.pause = newVal
        tiWaitMin = 0.050
        if newVal:  #---------- to Pause (pause 0->1)
            # self.player_.wait_until_paused()   # <-- 有時會發生錯誤, 原因不明, 故不採用
            while not self.player_._get_property('core-idle'):
                time.sleep(0.001)
            # 若 pause=1 後 0.020 秒就因系統忙碌而core臨時暫停(core-idle=1), 但實際並未暫停完成, 則使其至少暫停 tiWaitMin
            time.sleep(max(0.0, tiWaitMin - (time.time() - tiBgn)))
        else:       #---------- to Play (pause 1->0)
            # 保險機制 : 若等待時間 > tiWaitMin 則放棄, 不再等待 core-idle 變成 0
            while self.player_._get_property('core-idle') and (time.time() - tiBgn) <= tiWaitMin:
                time.sleep(0.001)

    # 注意 :
    #   因 playTimePos.TimePos 一直在變, 故可能函數開頭檢查<>None, 但函數中間變成 None !!!
    #   故須先設至其它變數 而非直接一直使用之
    @property
    def TimePos(self):
        return self.player_.time_pos

    def set_TimePos(self, posSec : float,  log):
        AddLogDug('PL.pos={}->{}, idle={idle},  by {log}', self.TimePos, f'{posSec:.2f}', idle=self.idle_active, log=log)
        if self.idle_active:
            # NOTE : 在啟動 play 前, 設定過 time_pos 會導致 play 後 time_pos 從此固定不動 !!! (pos=數值 or pos=None 都是)
            #        有時 player.play + player.wait_until_playing 也不行
            self.__Pre_time_pos = posSec
            AddLogDug('setTimePos_onIdle, bVoxFile={}', self.audio.audio_fullFna is not None)
            # self.player_.seek(0, reference='absolute')  # will error
            # self.__fmMain.audio_play()  # below can replace with this

            if self.audio.audio_fullFna is None:
                return  #////
            self.playFile(self.audio.audio_fullFna)
            self.playFrom_TimePos()
        else:
            self.player_.time_pos = posSec
    def playFrom_TimePos(self):
        AddLogDug('PL.idle={}, PrePos={}, pos={}', self.idle_active, self.__Pre_time_pos, self.TimePos)
        if self.idle_active:
            return  #////  caller 須負責 audio_play or playFile
        if self.__Pre_time_pos:
            # self.player_.wait_until_playing()
            self.player_.time_pos = self.__Pre_time_pos
            self.__Pre_time_pos = None
        self.pause = False

    @property
    def Speed(self):
        return self.player_.speed
    def SetSpeed(self, GoalVal):
        orgSpeed = self.player_.speed
        if GoalVal == orgSpeed:
            return  # skip, don't need change speed
        bPause = self.pause
        if not bPause:
            self.pause = True  # 重要! 否則導致 timepos 不準確, 甚至無限循環 play !!!
        self.player_.speed = max(self.MinSpeed, GoalVal)   # <---
        # time.sleep(0.050)
        AddLogDug('PL.Speed {} => {}, finalSpeed={}, orgPause={pau}', orgSpeed, GoalVal, self.player_.speed, pau=bPause)
        if not bPause:
            self.pause = False
            # self.player_.wait_until_playing()

    @property
    def volume(self):
        return self.player_.volume
    @volume.setter
    def volume(self, newVal):
        AddLogDug('PL.vol={}', newVal)
        self.player_.volume = newVal
        # self.player_._set_property('ao-volume', newVal)
        # self.player_._set_property('volume', 40)  # 100=normal


