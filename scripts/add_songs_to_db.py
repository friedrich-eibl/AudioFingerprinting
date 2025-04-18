from fingerprinting import *
from pathlib import Path


def add_songs_from_folder_to_db():
    song_names = [f.name for f in song_folder.iterdir() if f.is_file()]
    conn = sqlite3.connect(db_path)

    for song_name in song_names:
        path = song_folder / song_name
        song_id = add_song_to_db(conn, song_name, path)
        if song_id:
            spectrogram, sampling_rate = generate_spectogram(path)
            peaks = find_peaks(spectrogram, sampling_rate)
            song_hashes = generate_fingerprints(peaks,song_name)
            add_fingerprints_to_db(conn, song_id, song_hashes)

    conn.close()


if __name__ == '__main__':
    song_folder = Path(__file__).parent.parent / 'committee_audio'
    db_path = Path(__file__).parent.parent / 'fingerprint_improved_database.db'

    add_songs_from_folder_to_db()