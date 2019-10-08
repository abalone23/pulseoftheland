import sys
import argparse
import numpy as np
import pandas as pd
import re
import json
from datetime import datetime, timedelta
from time import sleep
import pickle
from psaw import PushshiftAPI
api = PushshiftAPI()

text = 'Get the latest NUMDAYS days of Reddit city data.'
parser = argparse.ArgumentParser(description = text)
parser.add_argument("--numdays", "-n", help="set # days to retrieve: 1 or 90")
parser.add_argument("--quiet", "-q", help="suppress output", action="store_true")

args = parser.parse_args()

if args.quiet is not True:
    if args.numdays:
        if args.numdays == '1':
            num_days = '5d'
        elif args.numdays == '90':
            num_days = '90d'
        else:
            print ('Error: Please select 1 or 90 days')
            sys.exit(2)
        print(f'# Days: {args.numdays}')

with open('data/df_cities.pkl', 'rb') as fp:
    df_cities = pickle.load(fp)

city_subs = df_cities['city_sub'].tolist()

def get_posts(subreddit):
    state_fip = str(df_cities['state_fip'][df_cities['city_sub'] == subreddit].values[0])

    post_list = list(api.search_submissions(after=num_days,
                                before='4d',
                                subreddit=city_sub,
                                stickied=False,
                                sort='asc',
                                filter=['id', 'permalink', 'title', 'selftext', 'permalink', 'num_comments', 
                                        'is_video', 'is_original_content', 'contest_mode', 'url',
                                        'media_only', 'locked'
                                       ]))
    sleep(0.5)
    posts = []
    prev_post_id = 0
    prev_post_date_y = ''
    prev_post_date_m = ''
    prev_post_date_d = ''
    
    for post in post_list:
        contest_mode = post[0]
        created_utc = post[1]
        post_id = post[2]
        is_original_content = post[3]
        is_video = post[4]
        locked = post[5]
        media_only = post[6]
        num_comments = post[7]
        permalink = post[8]
        selftext = post[9]
        title = post[10]
        url = post[11]

        post_date = datetime.fromtimestamp(created_utc).strftime('%Y-%m-%d')

        post_date_str = datetime.strptime(post_date, "%Y-%m-%d") 
        post_date_d = post_date_str.day        
        post_date_m = post_date_str.month
        post_date_y = post_date_str.year

        # Save json file for previous month, only for files with over 5 documents:
        if post_date_d != prev_post_date_d and prev_post_date_d != '' and len(posts) > 5:
            filename = (
                        f'data/reddit/cities/{subreddit.lower()}_'
                        f'{str(prev_post_date_y)}_{str(prev_post_date_m).zfill(2)}_{str(prev_post_date_d).zfill(2)}.json'
                       )
            with open(filename, 'w') as fp:
                json.dump(posts, fp, indent=2)
            posts = [] # reset posts list for new day
        
        if len(selftext) > 50:
            # print(f'sub: {subreddit} id: {post_id} post_date: {post_date} title: {title}')

            posts.append({
                'geo_type': 'city',
                'state_fip': state_fip,
                'subreddit': subreddit,
                'post_id': post_id,
                'post_date': post_date,
                'subreddit': subreddit,
                'title': title,
                'is_original_content': is_original_content,
                'is_video': is_video,
                'locked': locked,
                'media_only': media_only,
                'num_comments': num_comments,
                'permalink': permalink,
                'contest_mode': contest_mode,
                'selftext': selftext
            })
        
        prev_post_date_d = post_date_d        
        prev_post_date_m = post_date_m
        prev_post_date_y = post_date_y

for city_sub in city_subs:
    get_posts(city_sub)