import wx
import wx.html2

class MyFrame(wx.Frame):
    def __init__(self):
        super(MyFrame, self).__init__(None, title="HTML Content Example", size=(600, 400))
        # self.html_window = wx.html.HtmlWindow(self)
        self.html_window = wx.html2.WebView.New(self)

        # 載入HTML內容
        self.html_window.SetPage(self.generate_html_content(), '')
        self.Center()
        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyHook)  # 不論 focus 何在, 皆可捕捉到 !

    def generate_html_content(self):
        # return """
        # <table border="1">
        #     <tr>
        #         <td>Row 1, Column 1</td>
        #         <td>Row 1, Column 2</td>
        #     </tr>
        #     <tr>
        #         <td>Row 2, Column 1</td>
        #         <td>Row 2, Column 2</td>
        #     </tr>
        # </table>
        # """
        ss = '<table border="1">'
        for row in range(3):
            ss += '<tr>'
            ss += f'<td>row {row} aa</td>'
            ss += f'<td>row {row} BB</td>'
            ss += '</tr>'
        ss += '</table>'
        return ss

    # def generate_html_content(self):
    #     html_content = """
    #     <html>
    #     <body>
    #         <h1>圖文混合示例</h1>
    #         <p>這是一個包含圖像和文字的簡單示例。</p>
    #         <img src="icon.png" alt="icon">
    #         <p>Hello, wxPython!</p>
    #         <img src="another_image.png" alt="another image">
    #         <p>這是另一個圖像。</p>
    #     </body>
    #     </html>
    #     """
    #     return html_content

    # def generate_html_content(self):
    #     return """
    #         <html>
    #         <head>
    #             <style>
    #                 .container {
    #                     display: flex;
    #                     justify-content: center;
    #                     align-items: center;
    #                     height: 100%;
    #                 }
    #                 .bordered {
    #                     border: 3px solid red;
    #                     padding: 5px;
    #                 }
    #             </style>
    #         </head>
    #         <body>
    #             <div class="container">
    #                 <span>A</span>
    #                 <span class="bordered">B</span>
    #                 <span>C</span>
    #             </div>
    #         </body>
    #         </html>
    #     """

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
