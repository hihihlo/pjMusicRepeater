import wx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from pydub import AudioSegment
import threading
import time

class AudioPlayer(wx.Frame):
    def __init__(self, parent, title):
        super(AudioPlayer, self).__init__(parent, title=title, size=(800, 600))
        
        self.panel = wx.Panel(self)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.panel, -1, self.figure)
        self.play_button = wx.Button(self.panel, label="Play")
        self.timer = wx.Timer(self)
        
        self.Bind(wx.EVT_BUTTON, self.on_play_button, self.play_button)
        self.Bind(wx.EVT_TIMER, self.update_timer, self.timer)
        
        self.audio_file = "foo.mp3"
        self.audio = AudioSegment.from_mp3(self.audio_file)
        self.sample_width = self.audio.sample_width
        self.frame_rate = self.audio.frame_rate
        self.num_channels = self.audio.channels
        self.duration = len(self.audio) / 1000.0
        self.audio_data = np.array(self.audio.get_array_of_samples())
        # self.times = np.arange(0, self.duration, 1/self.frame_rate)
        # 將self.times的維度調整為與self.audio_data相同
        self.times = np.linspace(0, self.duration, len(self.audio_data))
        
        self.ax.plot(self.times, self.audio_data, linewidth=0.5)
        self.ax.set_title("Audio Waveform")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")
        self.ax.set_xlim(0, self.duration)
        
        self.vline = self.ax.axvline(x=0, color='r', linestyle='--')
        
        self.playback_position = 0
        self.is_playing = False
        
        self.timer.Start(100)  # Timer interval in milliseconds
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, flag=wx.EXPAND)
        sizer.Add(self.play_button, 0, flag=wx.CENTER|wx.TOP|wx.BOTTOM, border=10)
        
        self.panel.SetSizer(sizer)
        self.Centre()
        self.Show(True)
    
    def on_play_button(self, event):
        if not self.is_playing:
            self.play_button.SetLabel("Pause")
            self.play_audio()
        else:
            self.play_button.SetLabel("Play")
            self.pause_audio()
    
    def play_audio(self):
        self.is_playing = True
        self.playback_thread = threading.Thread(target=self.playback_thread_function)
        self.playback_thread.start()
    
    def playback_thread_function(self):
        for i in range(self.playback_position, len(self.times)):
            if not self.is_playing:
                break
            self.playback_position = i
            wx.CallAfter(self.update_vline_position)
            time.sleep(1/self.frame_rate)
        self.is_playing = False
        wx.CallAfter(self.reset_playback_position)
    
    def pause_audio(self):
        self.is_playing = False
    
    def update_vline_position(self):
        self.vline.set_xdata(self.times[self.playback_position])
        self.canvas.draw()
    
    def reset_playback_position(self):
        self.playback_position = 0
        self.vline.set_xdata(self.times[self.playback_position])
        self.canvas.draw()
    
    def update_timer(self, event):
        if self.is_playing and self.playback_position < len(self.times):
            current_time = self.playback_position / self.frame_rate
            self.SetTitle(f"Audio Player - {current_time:.2f} seconds")

if __name__ == '__main__':
    app = wx.App(False)
    frame = AudioPlayer(None, "Audio Player")
    app.MainLoop()
