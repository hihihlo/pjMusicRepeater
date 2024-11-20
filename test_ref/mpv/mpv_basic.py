import mpv
import time

#path = r'N0_1.wav'
path = r'long.mp3'
player = mpv.MPV()  # player = mpv.MPV(log_handler=print)
#player.set_loglevel('trace')
#player.play('https://youtu.be/DOmdB7D-pUU')
player.play(path)
#player.wait_for_property('playback-time', timeout=2)
#print(player.get_property('error_string'))
#player.wait_until_playing()
#print(player.time_pos)

time.sleep(1.0)
player.stop()
player.wait_for_playback(timeout=2)
print('mvp end')
