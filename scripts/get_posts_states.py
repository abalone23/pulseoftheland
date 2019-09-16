import sys
import numpy as np
import pandas as pd
import re
import json
from datetime import datetime, timedelta
import pickle
import datetime as dt
from psaw import PushshiftAPI
api = PushshiftAPI()

with open('../data/df_states.pkl', 'rb') as fp:
    df_states = pickle.load(fp)

start = '2018-08'
num_days = 430
state_subs = df_states['state_sub'].tolist()

#testing
# city_subs = city_subs[:5]
# city_subs = ['Alameda']

def get_posts(subreddit, start, num_days):
    start_epoch = int(datetime.strptime(start, '%Y-%m').timestamp())
    start_epoch_date = datetime.strptime(start, '%Y-%m')
    end_epoch_date = start_epoch_date + timedelta(days=num_days)
    end_epoch = int(end_epoch_date.timestamp())

    state_fip = str(df_states['state_fip'][df_states['state_sub'] == subreddit].values[0])

    post_list = list(api.search_submissions(after=start_epoch, before=end_epoch,
                                subreddit=state_sub,
                                stickied=False,
                                sort='asc',
                                filter=['id', 'permalink', 'title', 'selftext', 'permalink', 'num_comments', 
                                        'is_video', 'is_original_content', 'contest_mode', 'url',
                                        'media_only', 'locked'
                                       ]))

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

        # Save json file for previous month, only for files with over 10 documents:
        if post_date_d != prev_post_date_d and prev_post_date_d != '' and len(posts) > 10:
            filename = (
                        f'../data/reddit/states/{subreddit.lower()}_'
                        f'{str(prev_post_date_y)}_{str(prev_post_date_m).zfill(2)}_{str(prev_post_date_d).zfill(2)}.json'
                       )
            with open(filename, 'w') as fp:
                json.dump(posts, fp, indent=2)
            posts = [] # reset posts list for new day
        
        if len(selftext) > 50:
            print(f'sub: {subreddit} id: {post_id} post_date: {post_date} title: {title}')

            posts.append({
                'geo_type': 'state',
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

for state_sub in state_subs:
    get_posts(state_sub, start, num_days)