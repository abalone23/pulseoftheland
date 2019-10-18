#!/bin/bash

# get latest permits from abc site and load into json files; insert permits to PostgreSQL
source /home/asilver/.profile

cd /home/asilver/projects/pulseoftheland

# generate json files in data/reports:
/home/asilver/venvs/rp/bin/python ./scripts/get_posts_states.py --numdays 1
/home/asilver/venvs/rp/bin/python ./scripts/get_posts_cities.py --numdays 1

# load data from json files into Mongo and archive processed files
/home/asilver/venvs/rp/bin/python ./scripts/load_mongo.py --numdays 1

# generate topic modeling/sentiment/ascores and insert results into PostgreSQL
/home/asilver/venvs/rp/bin/python ./scripts/model_clean.py
