import wx

class MyDialog(wx.Dialog):
    def __init__(self, parent):
        #wx.Dialog.__init__(self, parent, title="My Dialog", style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
        wx.Dialog.__init__(self, parent, title="My Dialog", style=wx.DEFAULT_DIALOG_STYLE)

        # 一些控件
        panel = wx.Panel(self)
        self.text_ctrl = wx.TextCtrl(panel, wx.ID_ANY, "")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text_ctrl, 0, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)

        self.Bind(wx.EVT_ACTIVATE_APP, self.on_activate)

    def on_activate(self, event):
        if event.GetActive():
            self.Raise()  # 將對話框置于頂層

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(400, 300))
        self.panel = wx.Panel(self)
        self.button = wx.Button(self.panel, label="Show Modal Dialog")
        self.Bind(wx.EVT_BUTTON, self.on_show_modal, self.button)

    def on_show_modal(self, event):
        dialog = MyDialog(self)
        dialog.ShowModal()
        dialog.Destroy()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame(None, "Modal Dialog Demo")
    frame.Show(True)
    app.MainLoop()
