import wx, time

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title='Menu Demo', size=(300, 200))

        panel = wx.Panel(self)
        button = wx.Button(panel, label='Open File Menu')
        button.Bind(wx.EVT_BUTTON, self.on_open_menu)

        self.create_menu()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(button, 0, wx.CENTER | wx.ALL, 20)
        panel.SetSizer(sizer)

        wx.CallLater(500, self.on_open_menu, None)

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_OPEN, 'Open', 'Open a file')
        file_menu.Append(wx.ID_SAVE, 'Save', 'Save a file')
        file_menu.Append(wx.ID_EXIT, 'Exit', 'Exit the application')
        menu_bar.Append(file_menu, 'Filex')

        help_menu = wx.Menu()
        help_menu.Append(wx.ID_HELP_CONTENTS, 'Help', 'Open Help')
        menu_bar.Append(help_menu, 'Help')

        self.SetMenuBar(menu_bar)

    def on_open_menu(self, event):
        # wnd = wx.GetTopLevelWindows()[0]
        # wnd = self.GetEventHandler()
        # wnd = self
        wnd = self.GetTopLevelParent()
        sendEvent = wx.KeyEvent(wx.EVT_KEY_DOWN.typeId)
        sendEvent.SetAltDown(True)
        sendEvent.SetKeyCode(ord('F'))

        # wx.PostEvent(wnd, sendEvent)
        self.GetEventHandler().ProcessEvent(sendEvent)


if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
