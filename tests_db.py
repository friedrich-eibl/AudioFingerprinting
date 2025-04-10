from fingerprinting import *
from pathlib import Path

db_file = 'fingerprints_committee.db'
test_folder = 'eurasian_blackcap'
pathlist = list(Path(test_folder).glob('**/*.mp3')) + list(Path(test_folder).glob('**/*.wav'))

successful_matches = 0
no_match_count = 0
wrong_matches = 0

for path in pathlist:
    # because path is object not string
    path_in_str = str(path)
    print(path_in_str)
    spectrogram, sampling_rate = generate_spectogram(path_in_str)
    peaks = find_peaks(spectrogram, sampling_rate)
    test_hashes = generate_fingerprints(peaks, 'test')
    match_name, score = match_sample_db(test_hashes, db_file)

    if score > 30:
        print(f"Match result: Song='{match_name}', Score={score}")
        if match_name in str(path):
            successful_matches += 1
            print('\n')
        else:
            print("\033[91mWrong Match!\033[0m\n")
            wrong_matches += 1
    else:
        no_match_count += 1
        print("\033[93mNo Match!\033[0m\n")

print("\n\nNo Matches:", no_match_count)
print("Wrong matches:", wrong_matches)
print("Successful Matches:", successful_matches)