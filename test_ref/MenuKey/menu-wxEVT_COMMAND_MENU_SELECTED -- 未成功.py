import wx

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
        # Simulate pressing Alt + F by checking the 'File' menu item
        file_menu_title = 'Filex'
        menu_bar = self.GetMenuBar()  #type: MenuBar
        menu_position = menu_bar.FindMenu(file_menu_title)
        print(f' ( wx.NOT_FOUND = {wx.NOT_FOUND} )')
        print(f'"File" menu_position={menu_position}')
        # if menu_position != wx.NOT_FOUND:
        file_menu = menu_bar.GetMenu(menu_position)
        print(f'get title=[{file_menu.GetTitle()}]')

        mitem = file_menu.FindItemByPosition(0)  # assuming it's the first item
        print(f'mitem.GetId()={mitem.GetId()}')
        mid = mitem.GetId()
        # mid = 5050
        # evt = wx.MenuEvent(wx.wxEVT_COMMAND_MENU_SELECTED, mid)
        # evt = wx.MenuEvent(wx.wxEVT_COMMAND_MENU_SELECTED, mid, file_menu)
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_MENU_SELECTED, mid)
        # evt = wx.CommandEvent(wx.EVT_MENU.typeId, mid)
        # wx.PostEvent(self.GetTopLevelParent(), evt)
        # wx.PostEvent(self, evt)
        # wx.PostEvent(menu_bar, evt)
        # self.GetEventHandler().ProcessEvent(evt)
        menu_bar.GetEventHandler().ProcessEvent(evt)


if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
