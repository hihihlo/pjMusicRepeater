import mpv
import time

player = mpv.MPV()  # player = mpv.MPV(ytdl = False, video = False)
# print(f'device={player.audio_device}')
#player.audio_device = 'wasapi/{5fe5ad9b-9dfd-41b3-8269-c8780d0ba6a5}'
#path = r'long.mp3'
path = r'N0_1.wav'
# path = r'c:\DriveD\MyPro\DataProc\Parser_Script\Python\+media\+voice\pjMusicPlayer\ref_project\N0_1.wav'
#path = r'c/DriveD/MyPro/DataProc/Parser_Script/Python/+media/+voice/pjMusicPlayer/ref_project/N0_1.wav'

player.play(path)
player.speed = 0.5
print(f"dur={player.duration}")
# player.playlist_append(path)
# player.playlist_pos = 0

#print(player.playlist_filenames)
#print(player.audio_device_list, '\n')
player.wait_until_playing()
print(f"dur={player.duration}")
print(f"time_pos={player.time_pos}, playback-time={player.playback_time}")
    #print(f"idle={player.get_property('idle-active')}")
time.sleep(0.3)
print(f"time_pos={player.time_pos}, playback-time={player.playback_time}")
#print(f"time_pos={player.time_pos}"
#print(f"playback-time={player.playback_time}")

# player.wait_for_property('idle-active')
#while player.poll() is None:
#    time.sleep(0.1)

if not player.idle_active:
    player.wait_for_playback(timeout=2)
print('mvp end')
print(f"time_pos={player.time_pos}, playback-time={player.playback_time}")
