from pathlib import Path

import matplotlib.pyplot as plt
import librosa as lr

from fingerprinting import generate_spectogram, find_peaks


def show_spectogram_for_song(file_path, show_peaks: bool):
    spectrogram, sampling_rate = generate_spectogram(file_path)

    plt.figure()
    lr.display.specshow(spectrogram, sr=sampling_rate, x_axis='time', y_axis='log')

    if show_peaks:
        peak_times, peak_freqs = zip(*find_peaks(spectrogram, sampling_rate))
        plt.scatter(peak_times, peak_freqs, c='r', s=10, marker='x') # Plot peaks

    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram mixed with other sounds')
    plt.show()


if __name__ == '__main__':
    song_path = 'db_mgm_cut_clip.mp3'
    song_path = 'recognition_test_db_with_noise.mp3'
        # (str(Path(__file__).parent.parent
        #         / 'committee_audio/+++ AMPELOPOULI9         Mönchsgrasmücke  BlackCap       meist verwendet.mp3'))
    show_spectogram_for_song(song_path, True)