import wx, time
# import ctypes
# from .. import simulateKey  # ImportError: attempted relative import with no known parent package
# from ... pjMusicRepeater import simulateKey  # ImportError: attempted relative import with no known parent package
from simulateKey import *

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
        # Virtual-Key Codes (Winuser.h) - Win32 apps | Microsoft Learn
        #   https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
        # Which is the easiest way to simulate keyboard and mouse on Python? - Stack Overflow
        #   https://stackoverflow.com/questions/2791839/which-is-the-easiest-way-to-simulate-keyboard-and-mouse-on-python
        #   簡單的示範 send key and mouse
        # How to generate keyboard events? - Stack Overflow
        #   https://stackoverflow.com/questions/13564851/how-to-generate-keyboard-events
        #   "object-Object" 此人提供了簡單實用的 class, 含 key mapping define

        # KeySm.press(KeySm.F, [KeySm.alt])
        KeySm.press(ord('F'), [KeySm.alt])

if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
