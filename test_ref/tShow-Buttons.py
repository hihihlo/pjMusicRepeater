import wx 
import wx.lib.buttons as buttons

class GenericButtonFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Generic Button Example',size=(500, 350))
        panel = wx.Panel(self, -1)
        sizer = wx.FlexGridSizer(5, 2, 20, 20)
        b = wx.Button(panel, -1, "A wx.Button")
        b.SetDefault()
        sizer.Add(b)
        b = wx.Button(panel, -1, "non-default wx.Button")
        sizer.Add(b)
        sizer.Add((10,10))
        b = buttons.GenButton(panel, -1, 'Genric Button')
        sizer.Add(b)
        b = buttons.GenButton(panel, -1, 'disabled Generic')
        b.Enable(False)
        sizer.Add(b)
        
        b = buttons.GenButton(panel, -1, 'bigger')
        b.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD, False))
        b.SetBezelWidth(5)
        b.SetBackgroundColour("Navy")
        b.SetForegroundColour("white")
        b.SetToolTipString("This is a BIG button...")
        sizer.Add(b)
        
        bmp = wx.Bitmap("key_Del.png", wx.BITMAP_TYPE_ANY)
        b = buttons.GenBitmapButton(panel, -1, bmp)
        sizer.Add(b)
        b = buttons.GenBitmapToggleButton(panel, -1, bmp)
        sizer.Add(b)
        b = buttons.GenBitmapTextButton(panel, -1, bmp, "Bitmapped Text",size=(175, 75))   # <--- ok
            # b = buttons.GenBitmapTextButton(panel, bitmap=wx.NullBitmap, label="Bitmapped Text", size=(175, 75))   # <--- wxDIB::Create(): invalid bitmap
            # b.SetBitmapLabel(bmp)
        # b.SetUseFocusIndicator(False)
        sizer.Add(b)
        b = buttons.GenToggleButton(panel, -1, "Toggle Button")
        sizer.Add(b)
        panel.SetSizer(sizer)

if __name__ == '__main__':
    # app = wx.PySimpleApp()
    app = wx.App(False)
    frame = GenericButtonFrame()
    frame.Show()
    app.MainLoop()
 