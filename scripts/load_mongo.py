import re
import json
import os
import argparse
from datetime import date, datetime, timedelta
from pymongo import MongoClient

client = MongoClient()
db = client.r

text = 'Load Reddit json data into Mongo.'
parser = argparse.ArgumentParser(description = text)
parser.add_argument("--numdays", "-n", help="set # days to retrieve: 1 or all")
parser.add_argument("--quiet", "-q", help="suppress output", action="store_true")

args = parser.parse_args()

if args.quiet is not True:
    if args.numdays:
        if args.numdays == '1':
            num_days = '1'
        elif args.numdays == 'all':
            num_days = 'all'
        else:
            print ('Error: Please select 1 or all')
            sys.exit(2)
        print(f'# Days: {args.numdays}')

# print(f'count: {db.posts.estimated_document_count()}')


if num_days == 'all':
    db.posts.drop()
    path_to_city_json = 'data/reddit/cities'
    json_city_files = [pos_json for pos_json in os.listdir(path_to_city_json) if pos_json.endswith('.json')]

    path_to_state_json = 'data/reddit/states'
    json_state_files = [pos_json for pos_json in os.listdir(path_to_state_json) if pos_json.endswith('json')]
else:
    # Get json files from 5 days ago in data directory and insert into mongo
    fivedaysago = (datetime.now() - timedelta(5)).strftime('%Y_%m_%d')

    path_to_city_json = 'data/reddit/cities'
    json_city_files = [pos_json for pos_json in os.listdir(path_to_city_json) if pos_json.endswith(f'{fivedaysago}.json')]

    path_to_state_json = 'data/reddit/states'
    json_state_files = [pos_json for pos_json in os.listdir(path_to_state_json) if pos_json.endswith(f'{fivedaysago}.json')]

def to_dt(dict):
    dict['post_date'] = datetime.strptime(dict['post_date'], '%Y-%m-%d')
    return dict

def convert(list_of_dicts):
    return [to_dt(row) for row in list_of_dicts]

# Insert into MongoDB:
for json_file in json_city_files:
    with open(f'data/reddit/cities/{json_file}', 'r') as f:
        posts_cities_list = json.load(f)
        try:
            posts_cities_list = convert(posts_cities_list)
        except TypeError:
            raise
        result = db.posts.insert_many(posts_cities_list)

for json_file in json_state_files:
    with open(f'data/reddit/states/{json_file}', 'r') as f:
        posts_states_list = json.load(f)
        try:
            posts_states_list = convert(posts_states_list)
        except TypeError:
            raise
        result = db.posts.insert_many(posts_states_list)