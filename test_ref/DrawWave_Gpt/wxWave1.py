import wx
import numpy as np
from pydub import AudioSegment

class WaveformPanel(wx.Panel):
    def __init__(self, parent, audio_file):
        super(WaveformPanel, self).__init__(parent)

        self.audio = AudioSegment.from_file(audio_file)
        self.samples = np.array(self.audio.get_array_of_samples())
        self.time = np.arange(0, len(self.samples)) / self.audio.frame_rate

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()

        # 繪製波形圖
        dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))

        # 调整振幅范围以便更好地显示波形
        amplitude_range = 32768
        scaled_samples = (self.samples / amplitude_range) * (self.GetSize().y / 2)

        points = []
        for i, value in enumerate(scaled_samples):
            x = int(self.time[i] * 100)
            y = int(self.GetSize().y / 2 - value)
            points.append((x, y))

        dc.DrawLines(points)

    def on_left_down(self, event):
        x, _ = event.GetPosition()
        time_clicked = x / 100.0
        print(f"Current playback time: {time_clicked:.2f} seconds")

class WaveformFrame(wx.Frame):
    def __init__(self, audio_file):
        super(WaveformFrame, self).__init__(None, title="Waveform Viewer", size=(800, 400))
        panel = WaveformPanel(self, audio_file)
        self.Show(True)

if __name__ == "__main__":
    app = wx.App(False)
    audio_file_path = 'foo.mp3'  # 替換 'foo.mp3' 為你的音頻文件名稱
    frame = WaveformFrame(audio_file_path)
    app.MainLoop()
