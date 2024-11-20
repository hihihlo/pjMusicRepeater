import wx
import wx.html2

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="WebView Example", size=(400, 300))
        panel = wx.Panel(self)
        self.webview = wx.html2.WebView.New(panel)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyHook)  # 不論 focus 何在, 皆可捕捉到 !
        self.iLetter = 0
        self.letters = ['A', 'B', 'C', 'D', 'E']

        self.webview.SetPage(self.generate_html_content(), '')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.webview, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        self.Center()
        self.timer.Start(100)
        self.Show()

    # 在 wx.html.HtmlWindow 中顯示3個字母, 中間那個有文字邊框
    def generate_html_contentA(self):
        return """
            <html>
            <head>
                <style>
                    .container {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100%;
                    }
                    .bordered {
                        border: 3px solid red;
                        padding: 5px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <span>A</span>
                    <span class="bordered">B</span>
                    <span>C</span>
                </div>
            </body>
            </html>
        """

    # 出現3列, 而不是一列中3組字串 !!
    def generate_html_contentB(self):
        return """
測試
<div style="border-width: 3px; border-style:solid ; width: 150px; height: 30px; 
border-color: rgb(255, 172, 85); padding: 5px; text-align: center;">

    邊框

</div>
樣式
        """

    def generate_html_contentC(self):
        return """
                <table align="center">
                    <tr>
                        <td>A</td>
                        <td style="border: 1px solid black; padding: 5px;">B</td>
                        <td>C</td>
                    </tr>
                </table>
        """

    def generate_html_content(self):
        return """
            <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
                    <div style="margin: 0 auto;">
                        <div style="display: inline-block; padding: 5px;">A</div>
                        <div style="display: inline-block; border: 1px solid black; padding: 5px;">B</div>
                        <div style="display: inline-block; padding: 5px;">C</div>
                    </div>
                </div>
        """

    def on_timer(self, event):
        html_content = """
            <html>
            <body>
                <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
                    <div style="margin: 0 auto;">
        """

        for i, letter in enumerate(self.letters):
            if i == self.iLetter:
                html_content += f'<div style="display: inline-block; border: 1px solid black; padding: 5px;">{letter}</div>'
            else:
                html_content += f'<div style="display: inline-block; padding: 5px;">{letter}</div>'

        html_content += """
                    </div>
                </div>
            </body>
            </html>
        """

        self.webview.SetPage(html_content, "")

        # self.iLetter = (self.iLetter + 1) % len(self.letters)
        self.iLetter = self.iLetter + 1  if self.iLetter + 1 < len(self.letters)  else 0

    def onKeyHook(self, event):
        nCode = event.GetKeyCode()
        modifiers = event.GetModifiers()
        if modifiers == wx.WXK_NONE and nCode == wx.WXK_ESCAPE:
            exit(0)
        event.Skip()  # <--- propagate / 使能繼續傳遞此 event !!

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()
