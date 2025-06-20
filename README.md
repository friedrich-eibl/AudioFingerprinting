
# Audio-Fingerprinting Bird Songs

This project is meant to explore the possible application of acoustic fingerprinting for detecting playback traps used in poaching of song birds. The algorithm was based on the [Shazam algorithm](https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf) for music recognition.

## Setup
In order to run the scripts in this repository, you can create a virtual environment and install the dependencies from [requirements.txt](https://github.com/friedrich-eibl/AudioFingerprinting/blob/master/requirements.txt) using the following commands:

```
python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

```


## Experimental
Under [experiments/](https://github.com/friedrich-eibl/AudioFingerprinting/tree/master/experiments) you can find different scripts that are purely for the testing and evaluation of the fingerprinting algorithm. 

The [test_data.csv](https://github.com/friedrich-eibl/AudioFingerprinting/blob/master/experiments/test_data.csv) file contains a compiled list of bird songs from the xeno-canto online archive that can be used for testing purposes.

The [_config.yaml](https://github.com/friedrich-eibl/AudioFingerprinting/blob/master/experiments/_config.yaml) file can be used to specify the parameters for any number of experiments for both indexing songs and recognition.

If you want to run full experiments including creating a database, fingerprinting, comparing other songs and outputting a csv containing the match for each song as well as a confidence score, use: `python run_tests.py`


If you only want to test creating the database and populating it, run:
```
python setup.py
python add_songs_to_db.py
```
If you only want to test the detection of certain audio files using an existing database, run: `python tests_db.py`



## Application

For testing the web application of a live detector add songs using [scripts/add_songs_to_db.py](https://github.com/friedrich-eibl/AudioFingerprinting/blob/master/scripts/add_songs_to_db.py) and run:

`python app.py`
