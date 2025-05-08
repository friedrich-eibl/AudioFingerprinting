import csv
import os
from pathlib import Path

import yaml

from scripts.add_songs_to_db import add_songs_from_folder_to_db
from setup import setup_db
from tests_db import execute_test

benchmark = 'robustness_tests'

with open('test_config.yaml', 'r') as file:
    config = yaml.safe_load(file)

experiments = config['experiments']
fieldnames = ['test_name', 'matching_time', 'matching_time_single', 'wrong_matches', 'correct_matches', 'no_matches']

with open('results.csv', mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for exp in experiments:
        db_file = exp['name'] + '.db'
        setup_db(db_file)

        add_songs_from_folder_to_db(Path(__file__).parent / db_file, Path(__file__).parent / 'committee_audio')
        results = execute_test(db_file, benchmark, exp)
        results['test_name'] = exp['name']

        writer.writerow(results)

        os.remove(db_file)