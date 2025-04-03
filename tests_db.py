# from fingerprinting import *
# known_songs = {
#         "Purcell": "songs/1685 Purcell , Trumpet Tune and Air.mp3",
#         "Bach": "songs/1721 Bach , Minuet and Badinerie (from Orchestral Suite No. 2 inB Minor).mp3",
#         # Add more 'Song Name': 'path/to/file.mp3' entries
#     }
# known_songs = {
#         "NC1": "northern_cardinal_clips/XC899256 - Northern Cardinal - Cardinalis cardinalis.wav",
#         "NC2": "northern_cardinal_clips/XC899257 - Northern Cardinal - Cardinalis cardinalis.wav",
#         "NC3": "northern_cardinal_clips/XC920144 - Northern Cardinal - Cardinalis cardinalis.mp3",
#         "NC4": "northern_cardinal_clips/XC920145 - Northern Cardinal - Cardinalis cardinalis.mp3",
#         "NC5": "northern_cardinal_clips/XC930723 - Northern Cardinal - Cardinalis cardinalis.wav",
#     }
# conn = sqlite3.connect('fingerprint_database.db') # Connect once
# for song_name, path in known_songs.items():
#     song_id = add_song_to_db(conn, song_name, path)
#     if song_id:
#         spectrogram, sampling_rate = generate_spectogram(path)
#         peaks = find_peaks(spectrogram, sampling_rate)
#         song_hashes = generate_fingerprints(peaks,song_name) # Pass actual integer song_id
#         add_fingerprints_to_db(conn, song_id, song_hashes)
# conn.close() # Disconnect when done adding



from fingerprinting import *
from pathlib import Path

db_file = 'fingerprint_database.db'

pathlist = Path('northern_cardinal_clips').glob('**/*.wav')
for path in pathlist:
    # because path is object not string
    path_in_str = str(path)
    print(path_in_str)
    spectrogram, sampling_rate = generate_spectogram(path_in_str)
    peaks = find_peaks(spectrogram, sampling_rate)
    test_hashes = generate_fingerprints(peaks, 'test')
    match_name, score = match_sample_db(test_hashes, db_file)

    if score > 30:
        print(f"Match result: Song='{match_name}', Score={score}\n")
    else:
        print('No Match!\n')







# print ("\nfull song")
# spectrogram, sampling_rate = generate_spectogram('songs/1685 Purcell , Trumpet Tune and Air.mp3')
# peaks = find_peaks(spectrogram, sampling_rate)
# song_hashes = generate_fingerprints(peaks,'purcell')
# print(f"Generated {len(song_hashes)} hashes")
#
# print ("\nfull song 1")
# spectrogram, sampling_rate = generate_spectogram('songs/1721 Bach , Minuet and Badinerie (from Orchestral Suite No. 2 inB Minor).mp3')
# peaks = find_peaks(spectrogram, sampling_rate)
# bach_hashes = generate_fingerprints(peaks,'bach')
# print(f"Generated {len(bach_hashes)} hashes")
#
# print("\nTest 0")
# spectrogram, sampling_rate = generate_spectogram('test_frags/Purcell_4.mp3')
# peaks = find_peaks(spectrogram, sampling_rate)
# test_hashes = generate_fingerprints(peaks, 'test')
# print(f"Generated {len(test_hashes)} hashes")
# match_id, score = match_sample(test_hashes, song_hashes)
# print(f"Match result for Test 0: Song='{match_id}', Score={score}")