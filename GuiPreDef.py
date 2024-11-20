# this file is for wxGlade GUI use, 因為寫在此檔比寫在 GUI 小框中易讀
import wx, io, re
from wx.lib.agw import ultimatelistctrl as ULC
from cusLogger import *
import wx.richtext as wxRich

agwStyle = wx.LC_REPORT | wx.LC_SINGLE_SEL | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT \
   | ULC.ULC_VRULES | ULC.ULC_HRULES | ULC.ULC_NO_HIGHLIGHT

class MyRichText(wxRich.RichTextCtrl):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._SetBasicStyles()
        #----- _SetBasicStyles 設定後的 GetRichBuf_toXml 舉例 (由 log 看到) :
        # b'<?xml version="1.0" encoding="UTF-8"?>
        # \n<richtext version="1.0.0.0" xmlns="http://www.wxwidgets.org">
        # \n  <paragraphlayout textcolor="#00FA00" bgcolor="#090909" fontpointsize="16" fontweight="400" fontface="par"
        # alignment="1" parspacingafter="0" parspacingbefore="0" parstyle="par">
        # \n    <paragraph>
        # \n      <text>th</text>      // <---------------------- group(2) bgn
        # \n      <text textcolor="#FF0000" fontweight="700">is &#36889;&#26159;</text>
        # \n      <text>&#19968;&#20491;</text>
        # \n    </paragraph>
        # \n    <paragraph>
        # \n      <text>&#28204;&#35430; okABC</text>  // <------ group(2) end
        # \n    </paragraph>
        # \n  </paragraphlayout>
        # \n</richtext>\n'
        self.reRich = re.compile('(.*<paragraph>)(.*)(</paragraph>.*)', re.S)
        self.ReplTag = '<_XO_XO_>'  # tag for replace
        # self.tt()

    def _SetBasicStyles(self):
        self.SetBackgroundColour(wx.Colour(0,0,0))
        stl_paragraph = wxRich.RichTextAttr()
        stl_paragraph.SetFontSize(16)
        stl_paragraph.SetBackgroundColour(wx.Colour(9,9,9))
        stl_paragraph.SetTextColour(wx.Colour(0,250,0))
        stl_paragraph.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        stl_paragraph.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        stl_paragraph.SetParagraphSpacingBefore(0)
        stl_paragraph.SetParagraphSpacingAfter(0)
        stl_paragraph.SetParagraphStyleName('par')
        stl_paragraph.SetFontFaceName('par')
        # style_paragraph: rt.RichTextParagraphStyleDefinition = rt.RichTextParagraphStyleDefinition('paragraph')
        # style_paragraph.SetStyle(stl_paragraph)
        # style_paragraph.SetNextStyle('paragraph')
        # self._stylesheet.AddParagraphStyle(style_paragraph)
        # self.ApplyStyle(style_paragraph)
        # self.SetDefaultStyle(stl_paragraph)
        self.SetBasicStyle(stl_paragraph)

    def tt(self):
        self.AppendText('this 這是一個\n測試 okABC')
        # # self.SetSelection(2, 6)
        self.SetInternalSelectionRange(wx.richtext.RichTextRange(2, 6))  #僅選擇, caret 位置不變
        sSel = self.GetStringSelection()
        self.DeleteSelection()
        self.BeginTextColour((255, 0, 0))
        self.WriteText(sSel)
        self.EndTextColour()

        self.SetInternalSelectionRange(wx.richtext.RichTextRange(2, 6))  #僅選擇, caret 位置不變
        self.ApplyBoldToSelection()
        self.SetInternalSelectionRange(wx.richtext.RichTextRange(-2, -2))  #none select
        self.SetInsertionPoint(0)  # go home
        # self.SetInsertionPointEnd()
        # self.SetInternalSelectionRange(wx.richtext.RichTextRange(0, 0))  #僅選擇, caret 位置不變
        # self.ApplyTextEffectToSelection(flag)  #https://docs.wxpython.org/wx.TextAttrEffects.enumeration.html#wx-textattreffects

        xml = self.GetRichBuf_toXml()
        # print(f'GetXML ty={type(xml)}, {xml}')  #type(xml) = bytes
        self.Clear()
        self.SetRichBuf_frXml(xml)

    # uInfUnit :  (type : UInfUnit)
    #   if None : GetRichBuf_toXml、SetRichBuf_frXml 將存取完整的/原始的 xml bytes
    #   if 非空 : GetRichBuf_toXml 只取必要部份(self.reRich), SetRichBuf_frXml 時再套入表頭/表尾
    #   有 uInfUnit 參數時, 是想避免每次都儲存相同的一大串表頭/表尾 xml
    # ref :
    #   wxPython: Extracting XML from the RichTextCtrl - Mouse Vs Python
    #   https://www.blog.pythonlibrary.org/2015/07/10/wxpython-extracting-xml-from-the-richtextctrl/

    def GetRichBuf_toXml(self, uInfUnit = None) -> bytes:
        handler = wx.richtext.RichTextXMLHandler()
        # handler.SetFlags(wx.richtext.RICHTEXT_HANDLER_INCLUDE_STYLESHEET)
        buffer = self.GetBuffer()
        with io.BytesIO() as stream:
            handler.SaveFile(buffer, stream)
            xml = stream.getvalue()   # bytes
        if uInfUnit:
            rlt = self.reRich.search(xml.decode('utf-8'))
            if rlt:
                uInfUnit.sRichOuter = f'{rlt.group(1)}{self.ReplTag}{rlt.group(3)}'
                inside = rlt.group(2).strip()
                xml = None   if inside == '<text></text>' else   inside.encode('utf-8')
                AddLogDug('gup2={}, xml={}', inside, xml)
        return xml

    def SetRichBuf_frXml(self, xml: bytes,  uInfUnit = None):
        self.Clear()  # need !!!
        if xml is None or isinstance(xml, str):
            return  #////
        if uInfUnit and uInfUnit.sRichOuter:
            xml = re.sub(self.ReplTag, xml.decode('utf-8'), uInfUnit.sRichOuter, count=1).encode('utf-8')
        handler = wx.richtext.RichTextXMLHandler()
        buffer = self.GetBuffer()
        with io.BytesIO(xml) as stream:
            handler.LoadFile(buffer, stream)

