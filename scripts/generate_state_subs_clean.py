import os
import numpy as np
import pandas as pd
import re
from datetime import datetime
import pickle
import datetime as dt
import sys
import praw

PRAW_CLIENT_ID = os.getenv('PRAW_CLIENT_ID')
PRAW_CLIENT_SECRET = os.getenv('PRAW_CLIENT_SECRET')
PRAW_USER_AGENT = os.getenv('PRAW_USER_AGENT')

with open('../data/df_state_subs_raw.pkl', 'rb') as fp:
    df_state_subs_raw = pickle.load(fp)

def clean_states(subs):
    reddit = praw.Reddit(client_id=PRAW_CLIENT_ID,
                        client_secret=PRAW_CLIENT_SECRET,
                        user_agent=PRAW_USER_AGENT)

    states2add = {9: 'Connecticut', 42: 'Pennsylvania'}

    states2add_list = []
    for state_fip, state_sub in states2add.items():
        sub_cnt = reddit.subreddit(state_sub).subscribers

        df_state_subs_raw.loc[df_state_subs_raw['state_fip'] == state_fip, 'state_sub'] = state_sub
        df_state_subs_raw.loc[df_state_subs_raw['state_fip'] == state_fip, 'sub_cnt'] = sub_cnt

    return df_state_subs_raw

df_state_subs = clean_states(df_state_subs_raw)

pickle.dump(df_state_subs, open('../data/df_state_subs.pkl', 'wb'))