from pydub import AudioSegment
import matplotlib.pyplot as plt
import numpy as np

def plot_waveform(audio_file_path):
    # Load audio file
    audio = AudioSegment.from_file(audio_file_path)

    # Extract audio data as numpy array
    samples = np.array(audio.get_array_of_samples())

    # Calculate time axis
    duration = len(samples) / audio.frame_rate
    time_axis = np.linspace(0., duration, len(samples))

    # Plot waveform with two points per x-axis position
    plt.figure(figsize=(10, 4))
    #plt.scatter(time_axis[::len(samples)//2], samples[::len(samples)//2], color='r', marker='o', s=1)  # Adjust 's' for marker size
    plt.scatter(time_axis, samples, color='r', marker='o', s=1)  # Adjust 's' for marker size

    plt.title('Waveform of {}'.format(audio_file_path))
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.show()

# Replace 'foo.mp3' with the path to your audio file
audio_file_path = 'foo.mp3'
plot_waveform(audio_file_path)
