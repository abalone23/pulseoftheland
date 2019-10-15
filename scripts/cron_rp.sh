#!/bin/bash
# 05 08 * * * /home/asilver/projects/rmt/scripts/cron_permits.sh >> /home/asilver/logs/rmt_permits.log 2>&1
# get latest permits from abc site and load into json files; insert permits to PostgreSQL
source /home/asilver/.profile

cd /home/asilver/projects/pulseoftheland

# generate json files in data/reports:
/home/asilver/venvs/rp/bin/python ./scripts/get_posts_states.py --numdays 1
/home/asilver/venvs/rp/bin/python ./scripts/get_posts_cities.py --numdays 1

# load data from json file sinto Mongo and archive processed files
/home/asilver/venvs/rp/bin/python ./scripts/load_mongo.py --numdays 1