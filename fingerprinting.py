import librosa as lr
import numpy as np
import sqlite3
import time
from collections import defaultdict # Useful for counting
from scipy.ndimage import maximum_filter

from pathlib import Path


def generate_spectogram(path: str, start_time: float = 0.0, clip_duration: float = None):
    audio_signal, sampling_rate = lr.load(path, sr=22050, mono=True, offset=start_time, duration=clip_duration)

    transformed_signal = lr.stft(audio_signal)
    spectrogram = lr.amplitude_to_db(np.abs(transformed_signal), ref=np.max)

    return spectrogram, sampling_rate


def find_peaks(spectrogram, sampling_rate, peak_min_distance=15, peak_min_amplitude_threshold=-30):
    filtered_spectrogram = maximum_filter(spectrogram, size=(peak_min_distance, peak_min_distance))
    peaks_mask = (spectrogram == filtered_spectrogram)
    peaks_mask &= (spectrogram > (np.max(spectrogram) + peak_min_amplitude_threshold)) # Example threshold

    peak_indices = np.argwhere(peaks_mask)
    peak_times = lr.frames_to_time(peak_indices[:, 1], sr=sampling_rate, hop_length=512)
    peak_freqs = lr.fft_frequencies(sr=sampling_rate)[peak_indices[:, 0]]

    peaks = list(zip(peak_times, peak_freqs))
    print(f"Found {len(peaks)} peaks.")
    return peaks


def generate_fingerprints(peaks, song) -> dict:
    # Simplified conceptual hashing (needs refinement for efficiency and robustness)
    hashes = {} # Dictionary to store hashes: { hash_value: (song_id, time_offset) }

    # Parameters for pairing (adjust these)
    target_zone_time_delta_min = 0.1
    target_zone_time_delta_max = 1.0
    target_zone_freq_delta_max = 1000

    # This part would run for *each song* when building the database
    song_id = song # Replace with actual ID

    # Sort peaks by time for efficient pairing
    sorted_peaks = sorted(peaks, key=lambda x: x[0])

    for i in range(len(sorted_peaks)):
        anchor_time, anchor_freq = sorted_peaks[i]
        for j in range(i + 1, len(sorted_peaks)):
            target_time, target_freq = sorted_peaks[j]
            delta_t = target_time - anchor_time
            delta_f = abs(target_freq - anchor_freq)

            # Check if within time bounds of target zone
            if target_zone_time_delta_min <= delta_t <= target_zone_time_delta_max and delta_f <= target_zone_freq_delta_max:

                freq1_bin = int(anchor_freq)
                freq2_bin = int(target_freq)
                delta_t_bin = int(delta_t * 10) # Scale time delta, adjust precision

                hash_value = hash((freq1_bin, freq2_bin, delta_t_bin))

                if hash_value not in hashes:
                    hashes[hash_value] = []
                hashes[hash_value].append((song_id, anchor_time))
            elif delta_t > target_zone_time_delta_max:
                # Since peaks are sorted by time, no further peaks will be in the time zone
                break
    return hashes


def add_song_to_db(conn, song_name, file_path: str):
    if isinstance(file_path, Path):
        file_path = str(file_path)

    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO songs (song_name, file_path) VALUES (?, ?)", (song_name, file_path))
        conn.commit()
        song_id = cursor.lastrowid
        print(f"Added song '{song_name}' with ID {song_id}")
        return song_id
    except sqlite3.IntegrityError:
        print(f"Song '{song_name}' already exists. Fetching ID.")
        cursor.execute("SELECT song_id FROM songs WHERE song_name = ?", (song_name,))
        result = cursor.fetchone()
        return result[0] if result else None


def add_fingerprints_to_db(conn, song_id, fingerprint_dict):
    cursor = conn.cursor()
    fingerprint_data = []
    for hash_val, entries in fingerprint_dict.items():
        for entry in entries:
            offset = entry[1] if isinstance(entry, tuple) else entry
            hash_str = str(hash_val)
            fingerprint_data.append((hash_str, song_id, offset))

    cursor.executemany("INSERT INTO fingerprints (hash_value, song_id, offset) VALUES (?, ?, ?)", fingerprint_data)
    conn.commit()
    print(f"Added {len(fingerprint_data)} fingerprint entries for song ID {song_id}")


def match_sample_db(sample_fingerprints: dict, db_path: str):
    """Matches sample fingerprints against the SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    matches = defaultdict(lambda: defaultdict(int)) # { song_id: { offset_bin: count } }
    start_time = time.time()

    cursor.execute("SELECT song_id, song_name FROM songs")
    song_id_to_name = dict(cursor.fetchall())

    processed_hashes = 0
    total_matches_found = 0

    for sample_hash, sample_anchor_times in sample_fingerprints.items():
        hash_str = str(sample_hash)
        cursor.execute("SELECT song_id, offset FROM fingerprints WHERE hash_value = ?", (hash_str,))
        db_entries = cursor.fetchall() # List of (song_id, db_anchor_time)

        processed_hashes += 1
        if db_entries:
            total_matches_found += len(db_entries) * len(sample_anchor_times)
            for sample_anchor_tuple in sample_anchor_times:
                for db_song_id, db_anchor_time in db_entries:
                    delta_offset = db_anchor_time - sample_anchor_tuple[1]
                    offset_bin = round(delta_offset, 1)
                    matches[db_song_id][offset_bin] += 1

    conn.close()

    # Scoring
    best_match_song_id_num = None
    max_count = 0
    if not matches:
        print(f"No matches found after checking {processed_hashes} sample hashes.")
        match_duration = time.time() - start_time
        print(f"Matching took {match_duration:.2f} seconds.")
        return None, 0

    for song_id_num, offsets in matches.items():
        for offset, count in offsets.items():
            if count > max_count:
                max_count = count
                best_match_song_id_num = song_id_num

    match_duration = time.time() - start_time
    print(f"Matching took {match_duration:.2f} seconds. Found {total_matches_found} total hash alignments.")

    best_match_song_name = song_id_to_name.get(best_match_song_id_num, "Unknown ID")

    return best_match_song_name, max_count


def endpoint_detection_app(file_path):
    db_file = 'fingerprints_committee.db'
    spectrogram, sampling_rate = generate_spectogram(file_path)
    peaks = find_peaks(spectrogram, sampling_rate)
    test_hashes = generate_fingerprints(peaks, 'test')
    match_name, score = match_sample_db(test_hashes, db_file)

    return match_name, score
