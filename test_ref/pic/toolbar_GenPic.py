import wx
from contextlib import contextmanager


@contextmanager
def SelectAndFree(dc, objSel, objFree):
    try:
        dc.SelectObject(objSel)
        yield dc
    finally:
        dc.SelectObject(objFree)

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(400, 300))

        self.toolbar = self.CreateToolBar()
        # self.color = wx.Colour(0, 0, 0)  # 默认颜色为黑色

        self.add_tool(wx.Colour(0, 0, 0),  wx.Colour('green'), 'B', self.on_tool_click_1)
        self.add_tool(wx.Colour(0, 0, 0),  wx.Colour('red'),   'Tx', self.on_tool_click_1)
        self.add_tool(wx.Colour('yellow'), wx.Colour(0, 0, 0), 'Tx', self.on_tool_click_2)
        self.add_tool(wx.Colour(0, 0, 0),  wx.Colour('red'),   'B', self.on_tool_click_1)
        self.add_tool(wx.Colour('yellow'), wx.Colour(0, 0, 0), 'B', self.on_tool_click_2)

        self.toolbar.Realize()
        self.Show()

    def add_tool(self, bg_color, text_color, text, event_handler):
        bmp = self.create_bitmap(bg_color, text_color, text)
        obj = self.toolbar.AddTool(wx.ID_ANY, '', bmp, shortHelp="Custom Tool")
        self.Bind(wx.EVT_TOOL, event_handler, obj)

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
        print(f"Tool A with ID {tool_id} clicked.")
    def on_tool_click_2(self, event):
        tool_id = event.GetId()
        print(f"Tool B with ID {tool_id} clicked.")


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(None, 'Custom Toolbar Example')
    app.MainLoop()
