import os, sys, pathlib
import wx
import TAudio
# import pjMusicRepeater   # pjMusicRepeater import infSetting already !!!
#   === NOTE ===
#   1. 遞迴交互呼叫;  2. import 後會再執行一次, 含重複實例化 MyApp !!!!!!
#   即使在 infApp()、infUnit() 內 import, 也會重複實例化
from cusLogger import *
from utilMisc import *
import ruamel.yaml
import srt  # pip install -U srt
import chardet
import typing
from typing import List
from typing import Optional
from matplotlib import collections as pltCollections
from functools import cached_property

#======================================================================================================================
class TTest:
    def __init__(self):
        self.InfUnit_cnt = 0

gut = TTest()  # gut = global unit test

#======================================================================================================================
class USnte:  # USentence
    # enum Snte Type
    esntyMain = IncInt.reset()
    esntySub  = IncInt.val
    esntyCopy = IncInt.val
    esntyCnt_ = IncInt.val

    # 以下僅保留做為參考, 做為 交互 import / 建立時機 衝突時的備選解法之一
    # @classmethod
    # @property
    # def infApp(cls):
    #     if cls.__infApp is None:
    #         # cls.__infApp = pjMusicRepeater.gApp.frame.rep.infFile.uInfApp  #type: UInfApp  # gApp 尚未建立 !!!
    #         cls.__infApp = wx.GetTopLevelWindows()[0].rep.infFile.uInfApp  #type: UInfApp
    #     return cls.__infApp
    # @classmethod
    # @property
    # def infUnit(cls):
    #     if cls.__infUnit is None:
    #         # AddLogInf('prop_UNIT WindowListCnt={}', len(wx.GetTopLevelWindows()))
    #         # cls.__infUnit = pjMusicRepeater.gApp.frame.rep.infFile.uInfUnit  #type: UInfUnit  # gApp 尚未建立 !!!
    #         cls.__infUnit = wx.GetTopLevelWindows()[0].rep.infFile.uInfUnit  #type: UInfUnit
    #     return cls.__infUnit  #type: UInfUnit

    # __slots__ = 'bgn', 'end', 'cont', 'lSub'   # __slots__ 不適用於 yaml.register_class
    def __init__(self, bgn, end):
        self.bgn = bgn      #type: typing.Union[None, float]  #實際不能None, 僅為避免 IDE 誤判
        self.end = end      #type: typing.Union[None, float]  #實際不能None, 僅為避免 IDE 誤判
        self.cont = ''      #原文/歌詞
        self.bNote = None   #bin Note (也因為較好搜尋, "note" 太普遍了)
        self.__plcnt = None  #play cnt
        self.__speed = None
        self.lSub = []      #type: List[USnte]
        # 不需 write to yaml 的資訊 皆集中於 pEx object 內
        self.pEx = USnteEx(None, None, None, None)   #type: USnteEx
        # AddLogDug('USnte() ctor, .pEx={}', self.pEx)
        # <<注意>> : 隨後 LoadSrtFile > from_yaml > 將會使 pEx = None !! 即 pEx 在初始化階段可能為 None !!
    def __repr__(self):
        if self.pEx is None:  # when init_ing...
            return f' USnte(bgn={self.bgn:.2f}, end={self.end:.2f}, pEx=None)'
        else:
            return f' USnte(bgn={self.bgn:.2f}, end={self.end:.2f}, top={self.i_top}, sub={self.i_sub}, row={self.iRow}, cnt={self.__plcnt})'
    def __eq__(self, other):  # for operator== or index()
        return self.bgn == other.bgn and self.end == other.end
    def SetSnteEx(self, itop, isub, iRow, uPar):
        sBef = str(self)
        sArtDel = ''
        if self.pEx and self.pEx.SelRangeArtist:
            self.pEx.SelRangeArtist.remove()
            sArtDel = 'Art-'
        self.pEx = USnteEx(itop, isub, iRow, uPar)
        if self.isCopySnte:  self.pEx.snty = USnte.esntyCopy
        elif self.isSub:  self.pEx.snty = USnte.esntySub
        elif self.isPar:  self.pEx.snty = USnte.esntyMain
        AddLogDug('{} => {}  {art}, snty={snty}', sBef, str(self), art=sArtDel, snty=self.snty)
        if self.snty is None:
            AddLogERR('snty is None !!!?')

    @property
    def iRow(self):
        return self.pEx.iRow
    @property
    def i_top(self):
        return self.pEx.i_top
    @property
    def i_sub(self):
        return self.pEx.i_sub
    # i_sub == None 為 par/top, 否則為 sub
    @property
    def isPar(self):
        return self.i_sub is None
    @property
    def isSub(self):   # CopySnte also isSub
        return self.i_sub is not None
    @property
    def isCopySnte(self) -> bool:
        # 注意 : "None and bExpRlt" 結果為 None !!!  故不可 "return self.pEx.uPar and ..." 但可 "if self.pEx.uPar and ..."
        return self.pEx.uPar is not None and (self.i_sub == (len(self.pEx.uPar.lSub) - 1))
    @property
    def snty(self):
        return self.pEx.snty
    @property
    def isNone(self):
        return self.end is None or self.end == 0
    @property
    def plcnt_raw(self):
        return self.__plcnt
    @property
    def plcnt(self):
        # if self.__plcnt is None:
        #     AddLogDug('snty={}, UnitDefCnt={}', self.snty, gInfFile.uInfUnit.lDefSntePlcnt[self.snty])

        # if plcnt/speed is None, 則使用低一層優先權之值 : USnte.x > UInfUnit.x > UInfApp.x
        if self.__plcnt is not None:
            return self.__plcnt
        elif gInfFile.uInfUnit.lDefSntePlcnt[self.snty] is not None:
            return gInfFile.uInfUnit.lDefSntePlcnt[self.snty]
        else:
            return gInfFile.uInfApp.lDefSntePlcnt[self.snty]
    @plcnt.setter
    def plcnt(self, newVal):
        self.__plcnt = newVal
    @property
    def speed_raw(self):
        return self.__speed
    @property
    def speed(self):
        # if plcnt/speed is None, 則使用低一層優先權之值 : USnte.x > UInfUnit.x > UInfApp.x
        if self.__speed is not None:
            return self.__speed
        elif gInfFile.uInfUnit.lDefSnteSpeed[self.snty] is not None:
            return gInfFile.uInfUnit.lDefSnteSpeed[self.snty]
        else:
            return gInfFile.uInfApp.lDefSnteSpeed[self.snty]
    @speed.setter
    def speed(self, newVal):
        self.__speed = newVal


# 不需 write to yaml 的資訊 皆集中於此之內
class USnteEx:
    def __init__(self, itop, isub, iRow, uPar):
        # USnte.SetSnteEx 時重設(重新產生) 各 member
        self.i_top, self.i_sub, self.__iRow = itop, isub, iRow
        self.uPar = uPar   #type: USnte
        # 若為 main/top 則為 None (為 sub 才有值)
        self.SelRangeArtist = None   #type: typing.Union[pltCollections.PolyCollection, None]
        self.snty = None  # SnteType, set in USnte.SetSnteEx

    @property
    def iRow(self):
        return self.__iRow
    @property
    def GetInd(self):
        return UInd(self.i_top, self.i_sub)

class UInd:  # Index of USnte/USnteEx
    __slots__ = 'itop', 'isub'
    def __init__(self, itop, isub):
        self.itop, self.isub = itop, isub
    def __repr__(self):
        return f'UInd(top={self.itop}, sub={self.isub})'
    # __hash__ and __eq__ : for user defined dict key
    # def __hash__(self):
    #     return hash((self.i_top, self.i_sub))
    # def __eq__(self, other):
    #     return (self.i_top, self.i_sub) == (other.i_top, other.i_sub)


#======================================================================================================================
# - app setting info, global
# - ( this class should be inside InfFile )
class UInfApp:
    def __init__(self):
        self.lang = None  # ex: 'zh_TW'、'en_US'

        self.lDefSntePlcnt = [None] * USnte.esntyCnt_
        self.lDefSntePlcnt[USnte.esntyMain] = 2
        self.lDefSntePlcnt[USnte.esntySub] = 2
        self.lDefSntePlcnt[USnte.esntyCopy] = 1

        self.lDefSnteSpeed = [None] * USnte.esntyCnt_
        self.lDefSnteSpeed[USnte.esntyMain] = 1.0
        self.lDefSnteSpeed[USnte.esntySub] = 0.5
        self.lDefSnteSpeed[USnte.esntyCopy] = 0.65


# - track/unit info, 每個音檔 對應一個的 yaml info
# - ( this class should be inside InfFile )
class UInfUnit:
    # 不需 write to yaml 的資訊 皆集中於此之內
    # class UInfUnit_Ex:
    #     def __init__(self):
    #         pass

    def __init__(self):
        # prefix ut = Unit
        # self.utSpeed = 1.0  # play speed of whole track/mp3
        self.lDefSntePlcnt = [None] * USnte.esntyCnt_
        self.lDefSnteSpeed = [None] * USnte.esntyCnt_
        self.sRichOuter = None
        # self.pEx = UInfUnit.UInfUnit_Ex(audio)
        self.lSnte = []     #type: List[USnte]


class InfFile:
    NoYamlTag = ruamel.yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
    def __init__(self):
        AddLogInf('InfFile.__init__')
        self.fullFna_App = pathlib.Path(r'.\MusicRepeater.yaml')
        self.fullFna_Unit = None    #type: Optional[pathlib.Path]
        self.audio = None      #type: Optional[TAudio]    # init later in Init()
        self.uInfApp  = None   #type: Optional[UInfApp]
        self.uInfUnit = None   #type: Optional[UInfUnit]

        self.yamlApp = ruamel.yaml.YAML()  # ruamel-yaml obj
        self.yamlApp.indent(mapping=2, sequence=4, offset=2)
        self.yamlApp.register_class(UInfApp)

        self.yamlUnit = ruamel.yaml.YAML()  # ruamel-yaml obj
        self.yamlUnit.indent(mapping=2, sequence=4, offset=2)
        self.yamlUnit.representer.add_representer(USnte,   InfFile.toYaml_USnte)
        self.yamlUnit.constructor.add_constructor(InfFile.NoYamlTag, InfFile.frYaml_USnte)
        self.yamlUnit.register_class(UInfUnit)

        self.LoadApp()

    def Init(self, audio : TAudio):
        self.audio = audio

    @staticmethod
    def toYaml_USnte(representer, node):
        data = {key: value   for key, value in node.__dict__.items() if key != 'pEx'}  #不寫入 UInfUnit.pEx
        # AddLogDug('dict: {}', node.__dict__)
        return representer.represent_mapping(InfFile.NoYamlTag, data)

    @staticmethod
    def frYaml_USnte(loader, node):
        snte = USnte.__new__(USnte)
        yield snte
        data = ruamel.yaml.CommentedMap()
        loader.construct_mapping(node, maptyp=data, deep=True)
        # data['pEx'] = USnteEx(...)  # auto new .pEx in snte.__init__
        snte.__init__(data['bgn'], data['end'])
        # AddLogDug('## data= {}', data)
        # 此處設定的 snte.xx, 即為 read yaml 後建構出的 USnte obj 內容
        for k, v in data.items():
            setattr(snte, k, v)
        # AddLogDug('## snte= {}', snte)
        return data  # <---seem don't need !?

    def LoadVox(self, fullFna):
        if not self.audio.LoadVox_(fullFna):   # log already
            return  #////
        lFna = os.path.splitext(self.audio.audio_fullFna)
        self.fullFna_Unit = pathlib.Path(lFna[0] + ".MusRep")  # ex "vox01.MusRep"

        # 每個 .mp3 對應一個同名設定檔, 儲存 複讀段/筆記/...
        if self.fullFna_Unit.exists():   # 載入存在的對應設定檔
            self.uInfUnit = self.yamlUnit.load(self.fullFna_Unit)   #type: UInfUnit
            # AddLogInf('cont1= {}', self.uInfUnit.lSnte[1].cont)
            AddLogDug('{} loaded', self.fullFna_Unit)
        else:    # 由 .srt 建立新的對應設定檔
            AddLogInf('{} NOT exist, ', self.fullFna_Unit)
            self.uInfUnit = UInfUnit()
            self.uInfUnit.lSnte = self.LoadSrtFile()
            with open(self.fullFna_Unit, 'w', encoding='utf-8') as f:
                self.yamlUnit.dump(self.uInfUnit, f)

    def LoadSrtFile(self) -> list:
        # TODO: if self.fullFna_Unit:  this oper will overwrite bgn/end/cont/bNote, are you sure ?
        lFna = os.path.splitext(self.audio.audio_fullFna)
        fnaSrt = lFna[0] + ".srt"
        lInf = []
        if not os.path.isfile(fnaSrt):
            AddLogInf('and <{}> NOT exist', fnaSrt)
            wx.MessageBox(f'load {self.audio.audio_fullFna} OK,\n'
                          f'but .MusRep or .srt NOT exist !'
                          f"(many features are unavailable)",
                          'Music Repeater', wx.OK | wx.ICON_WARNING)
            # 暫時整個音檔為一句, 暫未自動分句
            snte = USnte( 0, self.audio.duration )
            lInf.append(snte)
            return lInf  #////

        AddLogInf('but <{}> exist : auto generate .MusRep from .srt', fnaSrt)
        with open(fnaSrt, 'rb') as fiRaw:
            rltEnc = chardet.detect(fiRaw.read(1000))
        with open(fnaSrt, encoding=rltEnc['encoding']) as fi:
            for subtitle in srt.parse(fi):  # type: srt.Subtitle
                snte = USnte( subtitle.start.total_seconds(), subtitle.end.total_seconds() )
                snte.cont = subtitle.content
                sub = USnte(snte.bgn, snte.end)
                snte.lSub.append(sub)   # generate/add CopyMainSnte
                lInf.append(snte)
                # print(f'rep:{rep.cont}, subtitle:{subtitle.content}, ss:{ss}')
        return lInf  #////

    def SaveUnit(self):
        AddLogDug('')
        with open(self.fullFna_Unit, 'w', encoding='utf-8') as f:
            self.yamlUnit.dump(self.uInfUnit, f)

    def LoadApp(self):
        # global setting
        if self.fullFna_App.exists():
            self.uInfApp  = self.yamlApp.load(self.fullFna_App)   #type: # Optional[UInfApp]
            AddLogDug('{} loaded', self.fullFna_App)
        else:    # 由 .srt 建立新的對應設定檔
            AddLogInf('{} NOT exist, auto create it', self.fullFna_App)
            self.uInfApp = UInfApp()
            # self.uInfApp.lSnte = self.LoadSrtFile()
            with open(self.fullFna_App, 'w', encoding='utf-8') as f:
                self.yamlApp.dump(self.uInfApp, f)

    def SaveApp(self):
        AddLogDug('')
        with open(self.fullFna_App, 'w', encoding='utf-8') as f:
            self.yamlApp.dump(self.uInfApp, f)

gInfFile = InfFile()
