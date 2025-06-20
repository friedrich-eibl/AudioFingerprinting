from fingerprinting import *
import librosa as lr
from pathlib import Path
from pydub import AudioSegment

import time
import random
import csv

def generate_random_list(seed: int, length: int):
    random.seed(seed)
    return [random.random() for _ in range(length)]

def get_audio_duration(path: str):
    y, sr = lr.load(path, sr=None)
    return len(y) / sr

def write_line_to_file(file_path, elements):
    #if not os.path.isfile(file_path)

    row = ', '.join(str(e) for e in elements)
    with open(file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(elements)


def execute_test(db_file, test_folder, exp):
    pathlist = list(Path(test_folder).glob('**/*.mp3')) + list(Path(test_folder).glob('**/*.wav'))
    print(len(pathlist))
    # return
    successful_matches = 0
    no_match_count = 0
    wrong_matches = 0
    threshold_too_high = 0
    relative_starts = generate_random_list(seed=exp["seed"], length=30)
    add_noise = exp["add_noise"]
    overall_runtime = 0
    failed_test_count = 0

    start_long = time.perf_counter()
    for idx, path in enumerate(pathlist):
        try:
            # because path is object not string
            start = time.perf_counter()
            peak_min_distance = exp["fingerprinting"]["peak_min_dist"]
            peak_min_amplitude_threshold = exp["fingerprinting"]["peak_min_amp"]

            path_in_str = str(path)
            print(path_in_str)
            
            clip_length = exp["clip_len"]
            relative_start = relative_starts[idx%len(relative_starts)]
            start_time = relative_start * (get_audio_duration(path_in_str)-clip_length)
            
            spectrogram, sampling_rate = generate_spectogram(path_in_str, start_time, clip_length)
            peaks = find_peaks(spectrogram, sampling_rate,peak_min_distance, peak_min_amplitude_threshold)        
            
            while len(peaks) < 10 and start_time < (get_audio_duration(path_in_str)-clip_length):
                start_time += 0.5
                print("incremented start_time by 0.5")
                spectrogram, sampling_rate = generate_spectogram(path_in_str, start_time, clip_length)
                peaks = find_peaks(spectrogram, sampling_rate,peak_min_distance, peak_min_amplitude_threshold)


            test_hashes = generate_fingerprints(peaks, 'test')
            match_name, score, confidence = match_sample_db(test_hashes, db_file)
        except Exception as e:
            failed_test_count += 1
            continue

        if score > 250:
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
            if match_name in str(path):
                threshold_too_high += 1

        end = time.perf_counter()
        overall_runtime += end - start
        print(f"Elapsed time: {end - start:.6f} seconds\n")
        
        
        write_line_to_file(exp["name"], [match_name, str(path), score, confidence]) # for testing

    end_long = time.perf_counter()

    print("Overall: ", overall_runtime)
    print ("overall estimate: ", end_long - start_long)

    print("\n\nNo Matches:", no_match_count)
    print("Wrong matches:", wrong_matches)
    print("Successful Matches:", successful_matches)

    results = {
        "matching_time": overall_runtime,
        "matching_time_single": '-', #overall_runtime / len(list(Path(test_folder).glob('**/*.mp3')) + list(Path(test_folder).glob('**/*.wav'))),
        "wrong_matches": wrong_matches,
        "correct_matches": successful_matches,
        "no_matches": no_match_count,
        "threshold_too_high": threshold_too_high,
        "failed_to_test": failed_test_count,
    }

    return results


if __name__ == '__main__':
    results = execute_test('limittest_database.db', 'eurasian_blackcap')
