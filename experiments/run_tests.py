import csv
import os
from pathlib import Path

import yaml

from scripts.add_songs_to_db import add_songs_from_folder_to_db
from setup import setup_db
from tests_db import execute_test

benchmark = 'test_data'

with open('_config.yaml', 'r') as file:
    config = yaml.safe_load(file)

experiments = config['experiments']
fieldnames = ['test_name', 'db_hashes', 'matching_time', 'matching_time_single', 'wrong_matches', 'correct_matches', 'no_matches', 'threshold_too_high', 'failed_to_test']

with open('bigtest_wod_2.csv', mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for exp in experiments:
        db_file = exp['name'] + '.db'
        setup_db(db_file)
        
        data_dirs = [
            "commonblackbirdtypesongqClen80len300",
            "eurasiannuthatchtypesongqDlen30len300",
            "commonquailtypesongqDlen30len300",
            "eurasianskylarktypesongqDlen40len300",
            "marshwrentypesongqDlen30len300",
            "eurasianblackcaptypesongqClen80len300",
            "songthrushtypesongqClen90len300"
        ]
         
        for data_dir in data_dirs:
            db_hash_count = add_songs_from_folder_to_db(Path(__file__).parent / db_file, Path(__file__).parent / f'test_data/{data_dir}/a', exp)
        
        results = execute_test(db_file, benchmark, exp)
        results['test_name'] = exp['name']
        results['db_hashes'] = db_hash_count

        writer.writerow(results)

        os.remove(db_file)
