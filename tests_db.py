from fingerprinting import *
from pathlib import Path

db_file = 'fingerprint_database.db'
pathlist = list(Path('northern_cardinal_clips').glob('**/*.wav'))

successful_matches = 0

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
        if match_name in str(path):
            successful_matches += 1
    else:
        print('No Match!\n')

print("\n\nFailed Matches:", len(pathlist) - successful_matches)
print("Successful Matches:", successful_matches)