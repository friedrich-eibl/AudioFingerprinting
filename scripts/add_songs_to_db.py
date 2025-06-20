from fingerprinting import *
from pathlib import Path
from pydub.exceptions import CouldntDecodeError
from pydub import AudioSegment


def add_songs_from_folder_to_db(db_path, song_folder, exp) -> int:
    song_names = [f.name for f in song_folder.iterdir() if f.is_file()]
    conn = sqlite3.connect(db_path)
    corrupt_files_counter = 0

    for song_name in song_names:
        try:
            path = song_folder / song_name
            duration = len(AudioSegment.from_file(str(path))) / 1000

            song_id = add_song_to_db(conn, song_name, path, duration)
            if song_id:
                spectrogram, sampling_rate = generate_spectogram(path)

                peak_min_distance = exp["fingerprinting"]["peak_min_dist"]
                peak_min_amplitude_threshold = exp["fingerprinting"]["peak_min_amp"]
                
                peaks = find_peaks(spectrogram, sampling_rate, peak_min_distance, peak_min_amplitude_threshold)
                song_hashes = generate_fingerprints(peaks,song_name)
                add_fingerprints_to_db(conn, song_id, song_hashes)
        except CouldntDecodeError:
            corrupt_files_counter += 1
   
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fingerprints")
    fingerprints_count = cursor.fetchone()[0]
    conn.close()
    return fingerprints_count


if __name__ == '__main__':
    song_folder = Path(__file__).parent.parent.parent / 'xeno-canto/xeno-canto_downloads/red-wingedblackbirdqA'
    db_path = Path(__file__).parent.parent / 'limittest_database.db'

    add_songs_from_folder_to_db()
