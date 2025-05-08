from fingerprinting import *
from pathlib import Path

import time


def execute_test(db_file, test_folder, exp):
    pathlist = list(Path(test_folder).glob('**/*.mp3')) + list(Path(test_folder).glob('**/*.wav'))
    successful_matches = 0
    no_match_count = 0
    wrong_matches = 0

    overall_runtime = 0

    start_long = time.perf_counter()
    for path in pathlist:
        # because path is object not string
        start = time.perf_counter()

        path_in_str = str(path)
        print(path_in_str)
        spectrogram, sampling_rate = generate_spectogram(path_in_str)
        peaks = find_peaks(spectrogram, sampling_rate)
        test_hashes = generate_fingerprints(peaks, 'test')
        match_name, score = match_sample_db(test_hashes, db_file)

        if score > 150:
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

        end = time.perf_counter()
        overall_runtime += end - start
        print(f"Elapsed time: {end - start:.6f} seconds\n")

    end_long = time.perf_counter()

    print("Overall: ", overall_runtime)
    print ("overall estimate: ", end_long - start_long)

    print("\n\nNo Matches:", no_match_count)
    print("Wrong matches:", wrong_matches)
    print("Successful Matches:", successful_matches)

    results = {
        "matching_time": overall_runtime,
        "matching_time_single": overall_runtime / len(list(Path(test_folder).glob('**/*.mp3')) + list(Path(test_folder).glob('**/*.wav'))),
        "wrong_matches": wrong_matches,
        "correct_matches": successful_matches,
        "no_matches": no_match_count
    }

    return results


if __name__ == '__main__':
    results = execute_test('limittest_database.db', 'eurasian_blackcap')
