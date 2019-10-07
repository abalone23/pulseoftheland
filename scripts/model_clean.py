import sys
import csv
import os
import pickle
import re
from datetime import date, datetime, timedelta

from pymongo import MongoClient
import psycopg2 as pg
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas.io.sql as pd_sql

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from sklearn.decomposition import NMF

from textblob import TextBlob
from textblob.taggers import NLTKTagger
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from ascore import create_ascore

nltk_tagger = NLTKTagger()

import warnings
warnings.filterwarnings('ignore')

# NMF topics
num_topics = 10
num_keywords = 8
num_days = 90

with open('data/df_states.pkl', 'rb') as fp:
    df_states = pickle.load(fp)

with open('data/df_cities.pkl', 'rb') as fp:
    df_cities = pickle.load(fp)

client = MongoClient()
db = client.r

# today = datetime.today()
# days_to_load = today - timedelta(days = days_ago)
start = datetime(2019, 6, 10)
end = start + timedelta(days=num_days)

day = timedelta(days=1)

mydate_start = start
mydate_end = end

def generate_models(posts, start, end):
    df_posts = pd.DataFrame(posts)
    # print(df_posts[['title', 'post_date']].sort_values('post_date'))

    # word count
    df_posts['count'] = df_posts['selftext'].str.count(' ') + 1

    # remove duplicates ie spam, daily/weekly notices etc. 
    df_posts = df_posts.drop_duplicates(subset='selftext')

    min_word_cnt = 10
    max_word_cnt = 1500

    # remove extra-short and extra-long posts
    df_posts = df_posts[(df_posts['count'] >= min_word_cnt) & (df_posts['count'] < max_word_cnt)]

    # remove spam posts contains at least 5 consecutive words
    df_posts = df_posts[~df_posts['selftext'].str.contains(r'\b(\w+)(\s+\1){4,}\b', r'\1', flags=re.IGNORECASE)]

    custom_stop_word_list = ['area', 'thanks', 'place', 'state', 'people', 'time', 'year',
                            'day, city', 'town', 'week', 'question', 'county', 'said',
                            'thank', 'reddit', 'ave', 'really', 'hey', 'way', 'lot',
                            'thing', 'don', 'hour', 'idea', 'option', 'wa', 'does', 'ha',
                            'use', 'like', 'number', 'didn', 'doesn', 'google',
                            'sub', 'blah', 'mod', 'lol', 'hello', 'month', 'issue',
                            'location', 'minute', 'today', 'example', 'sunday',
                            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
                            'information', 'info', 'subreddit', 'wiki', 'january', 'february',
                            'march', 'april', 'may', 'june', 'july', 'august', 'september',
                            'october', 'november', 'december', 'great', 'new', 'bos', 'thx',
                            'shit', 'penis', 'couldn', 'fuck', 'just', 'today', 'tomorrow',
                            'sort', 'item', 'anybody', 'list', 'post', 'page', 'dont', 'img',
                            'wouldn', 'would', 'redditors', 'somebody', 'img']

    custom_stop_words = ' '.join(custom_stop_word_list)
    blob = TextBlob(custom_stop_words)
    lemmatized_custom_stop_word_list = blob.words.lemmatize() # lemmatize all custom stop words
    stop_words = ENGLISH_STOP_WORDS.union(lemmatized_custom_stop_word_list)

    def preprocess_text(post):
        """This is run before the sentiment analysis"""
        
        # remove | words |
        regex_pat = re.compile(r'\|.+?\|', flags=re.IGNORECASE)
        post = re.sub(regex_pat, '', post)

        # remove { words }
        regex_pat = re.compile(r'{.+?}', flags=re.IGNORECASE)
        post = re.sub(regex_pat, '', post)

        # remove ( words )
        regex_pat = re.compile(r'\(.+?\)', flags=re.IGNORECASE)
        post = re.sub(regex_pat, '', post)

        # remove [ words ]
        regex_pat = re.compile(r'\[.+?\]', flags=re.IGNORECASE)
        post = re.sub(regex_pat, '', post)

        # remove links
        regex_pat = re.compile(r'https?:\/\/.*[\r\n]*', flags=re.IGNORECASE)
        post = re.sub(regex_pat, '', post)
        
        # remove emails
        regex_pat = re.compile(r'\S*@\S*\s?', flags=re.IGNORECASE)
        post = re.sub(regex_pat, '', post)
            
        # remove any digits or words that start with digits ie 19th
        regex_pat = re.compile(r'\b\D?\d.*?\b', flags=re.IGNORECASE)
        post = re.sub(regex_pat, ' ', post)

        # remove words that start # ie #x200b
        regex_pat = re.compile(r'#.*\b', flags=re.IGNORECASE)
        post = re.sub(regex_pat, ' ', post)

        post = post.replace('&amp', 'and').replace('&nbsp', ' ')
        post = post.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '”')
        
        # remove special stop words
        regex_pat = re.compile(r'update:|wibta|email|gmail|tldr|                              nbsp|\b.+_.+\b|\baaa.+\b|\bbbb.+\b', flags=re.IGNORECASE)
        post = re.sub(regex_pat, '', post)
        
        # collapse spaces
        regex_pat = re.compile(r'\s+', flags=re.IGNORECASE)
        post = re.sub(regex_pat, ' ', post)
        
        return post

    def get_topics(nmf_model, num_keywords):
        num_topics = nmf_model.components_.shape[0]
        topics_dict = {}
        for ix, topic in enumerate(nmf_model.components_):
            topics_dict[ix] = ", ".join([count_vectorizer.get_feature_names()[i] 
                                        for i in topic.argsort()[:-num_keywords - 1:-1]])
        return topics_dict

    # Preprocess the posts:
    df_posts['selftext_preprocessed'] = df_posts['selftext'].apply(preprocess_text)

    sid = SentimentIntensityAnalyzer()
    df_posts['sentiment_all'] = df_posts['selftext_preprocessed'].apply(lambda x: sid.polarity_scores(x))

    # extract compound score to new column
    df_posts['sentiment_compound'] = df_posts['sentiment_all'].apply(lambda x: x.get('compound'))

    # Extra step needed to calculate state sentiment since all cities within that state should be included as well
    df_cities_tmp = df_cities[['city_sub', 'state_fip']]
    df_cities_tmp = df_cities_tmp.rename(columns={'city_sub': 'subreddit'})

    df_states_tmp = df_states[['state_sub', 'state_fip']]
    df_states_tmp = df_states_tmp.rename(columns={'state_sub': 'subreddit'})

    df_posts_tmp = df_posts[['subreddit', 'geo_type', 'sentiment_compound']]
    df_posts_cities = pd.merge(df_posts_tmp, df_cities_tmp, on='subreddit')
    df_posts_states = pd.merge(df_posts_tmp, df_states_tmp, on='subreddit')

    frames = [df_posts_cities, df_posts_states]
    df_posts_sent_tmp = pd.concat(frames)

    # Create sentiment df for each subreddit
    df_sent = df_posts.groupby('subreddit') \
                    .agg({'sentiment_compound':'mean', 'geo_type':'first'}) \
                    .reset_index()
    sent_dict = df_sent.to_dict('records')

    # Create sentiment df for each subreddit
    df_sent_cities = df_posts_cities.groupby('subreddit') \
                                    .agg({'sentiment_compound':'mean'}) \
                                    .reset_index()
    sent_dict_cities = df_sent_cities.to_dict('records')

    # special case for states to inlucde states and cities with state
    df_sent_states = df_posts_sent_tmp.groupby('state_fip') \
                                    .agg({'sentiment_compound':'mean'}) \
                                    .reset_index()
    sent_dict_states = df_sent_states.to_dict('records')

    quant_states_25 = round(df_sent_states.quantile(.25).values[1], 2)
    quant_states_75 = round(df_sent_states.quantile(.75).values[1], 2)

    quant_cities_25 = round(df_sent_cities.quantile(.25).values[0], 2)
    quant_cities_75 = round(df_sent_cities.quantile(.75).values[0], 2)

    connection_args = {
        'host': os.getenv('POSTGRES_HOST'),
        'user': os.getenv('POSTGRES_USER'),
        'dbname': os.getenv('POSTGRES_RP_DB'),
        'port': os.getenv('POSTGRES_PORT')
    }

    connection = pg.connect(**connection_args)

    # insert sentiments scores into Postgres
    cursor = connection.cursor()

    for row in sent_dict_states:
        state_fip = row['state_fip']
        sentiment_compound = round(row['sentiment_compound'], 2)

        if sentiment_compound > quant_states_75:
            sentiment_rating = 'pos'
        elif sentiment_compound < quant_states_25:
            sentiment_rating = 'neg'
        else:
            sentiment_rating = 'neu' # neutral
        
        query =  "UPDATE states SET sentiment_compound = %s, sentiment_rating = %s WHERE state_fip = %s"
        
        data = (sentiment_compound, sentiment_rating, state_fip)       
        cursor.execute(query, data)
        
        connection.commit()

    cursor.close()

    # insert sentiments scores into Postgres
    cursor = connection.cursor()

    for row in sent_dict_cities:
        subreddit = row['subreddit']
        sentiment_compound = round(row['sentiment_compound'], 2)

        if sentiment_compound > quant_cities_75:
            sentiment_rating = 'pos'
        elif sentiment_compound < quant_cities_25:
            sentiment_rating = 'neg'
        else:
            sentiment_rating = 'neu' # neutral

        query =  "UPDATE cities SET sentiment_compound = %s, sentiment_rating = %s WHERE city_sub = %s"
        
        data = (sentiment_compound, sentiment_rating, subreddit)       
        cursor.execute(query, data)
        
        connection.commit()

    cursor.close()

    def compute_ascore(geo):
        cursor = connection.cursor()

        if geo == 'states':
            table = 'states'
            sub_field = 'state_sub'
        else:
            table = 'cities'
            sub_field = 'city_sub'
        
        query = f'SELECT {sub_field}, pop_2018, median_hh_income, sentiment_compound FROM {table}'
        df_metrics = pd_sql.read_sql(query, connection)
        
        df_metrics['ascore'] = create_ascore(
            df_metrics[['pop_2018']], 
            df_metrics[['median_hh_income']], 
            df_metrics[['sentiment_compound']]
        )
        
        df_metrics['ascore'] = df_metrics['ascore'].round(1)

        for row in df_metrics.itertuples():
            query =  f'UPDATE {table} SET ascore = %s WHERE {sub_field} = %s'
            data = (row.ascore, row[1])       
            cursor.execute(query, data)
            connection.commit()
        cursor.close()

    compute_ascore('states')
    compute_ascore('cities')

    query = f'SELECT state_sub, sentiment_compound, sentiment_rating, ascore FROM states'
    df_states_metrics = pd_sql.read_sql(query, connection)

    query = f'SELECT city_sub, sentiment_compound, sentiment_rating, ascore FROM cities'
    df_cities_metrics = pd_sql.read_sql(query, connection)

    pickle.dump(df_states_metrics, open('data/df_states_metrics.pkl', 'wb'))
    pickle.dump(df_cities_metrics, open('data/df_cities_metrics.pkl', 'wb'))

    def clean_text(post):
        """Run after sentiment analysis"""
        blob = TextBlob(post)
        
        # delete 1 and 2 letter words
        regex_pat = re.compile(r'\b\w{1,2}\b', flags=re.IGNORECASE)
        post = re.sub(regex_pat, ' ', post)

        # remove quotes
        regex_pat = re.compile(r'[\'"]', flags=re.IGNORECASE)
        post = re.sub(regex_pat, '', post)
        
        # set textblob again with cleaned words:
        blob = TextBlob(post, pos_tagger=nltk_tagger)
        
        # lemmatize, lowercase, and only include nouns and proper nouns
        words = [token.lemmatize()
                    .lower() for token, (_, pos) in zip(blob.words, blob.tags)
                    if pos in ['NN', 'NNS', 'NNP', 'NNPS']]
        
        return ' '.join(words)

    df_posts['selftext_final'] = df_posts['selftext_preprocessed'].apply(clean_text)

    cursor = connection.cursor()

    query_topics = "TRUNCATE topics RESTART IDENTITY CASCADE" # CASCADE needed due to foreign key
    query_kw = "TRUNCATE keywords RESTART IDENTITY CASCADE"
    query_geo = "TRUNCATE topics_geo RESTART IDENTITY CASCADE"
    query_tkw = "TRUNCATE topics_keywords RESTART IDENTITY CASCADE"
    cursor.execute(query_topics)
    cursor.execute(query_kw)
    cursor.execute(query_geo)
    cursor.execute(query_tkw)
    connection.commit()
    cursor.close()

    cursor = connection.cursor()

    query =  f"INSERT INTO models (extract_date) VALUES (to_timestamp('{start}', 'YYYY-MM-DD HH24:MI:SS')) RETURNING model_id"
    cursor.execute(query)
    model_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()

    cursor = connection.cursor()

    for location in sent_dict:
        sub = location['subreddit']
        posts_final = df_posts['selftext_final'][df_posts['subreddit'] == sub]
        
        if len(df_states[df_states['state_sub'] == sub]):
            state_name = df_states.loc[df_states['state_sub'] == sub, 'state_name'].values[0].lower()
            # it's necessary to lemmatize the word otherwise:
            # UserWarning: Your stop_words may be inconsistent with your preprocessing.
            blob = TextBlob(state_name)
            state_tokens = blob.words.lemmatize()
            
            # Tailor stop word for each location
            stop_words_tot = stop_words.union(state_tokens)
            geo_type = 'state'

            query =  "SELECT state_id FROM states WHERE state_sub = %s"
            data = (sub,) # tuple required for cursor.execute
            cursor.execute(query, data)
            state_id = cursor.fetchone()[0]
            geo_id = state_id
        else:
            city_short = df_cities.loc[df_cities['city_sub'] == sub, 'city_short'].values[0].lower()
            # it's necessary to lemmatize the word otherwise:
            # UserWarning: Your stop_words may be inconsistent with your preprocessing.
            blob = TextBlob(city_short)
            city_tokens = blob.words.lemmatize()
            stop_words_tot = stop_words.union(city_tokens)
            geo_type = 'city'
            query =  "SELECT city_id FROM cities WHERE city_sub = %s"
            data = (sub,) # comma will turn it into a list which is required in cursor.execute
            cursor.execute(query, data)
            city_id = cursor.fetchone()[0]
            geo_id = city_id
        
        connection.commit()

        count_vectorizer = CountVectorizer(ngram_range=(1, 2), stop_words=stop_words_tot)    
        doc_word = count_vectorizer.fit_transform(posts_final)
        nmf_model = NMF(num_topics)
        nmf_model.fit_transform(doc_word)

        topics_dict = get_topics(nmf_model, num_keywords)
        for k, v in topics_dict.items():
            keywords = v.split(', ') # convert keywords to list
            
            query =  "INSERT INTO topics (topic) VALUES ('Topic') RETURNING topic_id"
            cursor.execute(query)
            topic_id = cursor.fetchone()[0]
            connection.commit()
            
            for word in keywords:
                if len(word) <= 30: # do not include any word over 30 characters
                    # check whether keyword exists and if so, get the id to use
                    query = "SELECT keyword_id FROM keywords WHERE keyword = %s"
                    data = (word,)
                    cursor.execute(query, data)
                    row_kw = cursor.fetchone()
                    if row_kw is not None:
                        keyword_id = row_kw[0] # keyword exists
                    else:
                        query_kw =  "INSERT INTO keywords (keyword) VALUES (%s) RETURNING keyword_id"
                        data_kw = (word,)
                        cursor.execute(query_kw, data_kw)   
                        keyword_id = cursor.fetchone()[0]                

                    query_kw =  "INSERT INTO topics_keywords (topic_id, keyword_id) VALUES (%s, %s)"
                    data_kw = (topic_id, keyword_id)
                    cursor.execute(query_kw, data_kw)   

            # geo_type: city or state
            # geo_id: city_id or state_id
            query =  "INSERT INTO topics_geo (geo_type, geo_id, topic_id, model_id) VALUES (%s, %s, %s, %s)"
            data = (geo_type, geo_id, topic_id, model_id)
            cursor.execute(query, data)
                
            connection.commit()
    cursor.close()

    cursor = connection.cursor()
    query =  """
            UPDATE keywords AS kw
            SET num_geo = sq.count FROM (
            SELECT count(tk.keyword_id) AS count, tk.keyword_id 
            FROM topics_keywords as tk 
            INNER JOIN keywords as k on k.keyword_id = tk.keyword_id
            GROUP BY tk.keyword_id
            ) AS sq
            WHERE kw.keyword_id = sq.keyword_id
            """
    cursor.execute(query)
    connection.commit()
    cursor.close()

    # EDA exploration used to create topic dictionary
    # broad topics at top, narrow topics below which will override the broad ones
    topics_dict = [
                    {'Work': ['work', 'job', 'management', 'employer', 'office']},
                    {'Entertainment': ['museum', 'play', 'music', 'fun', 'game', 'theater', 'theatre', 
                                        'comedy', 'movie']},
                    {'Housing': ['housing', 'apartment', 'lease', 'mortgage', 'rent', 'tenant', 
                                    'rent', 'household', 'condo', 'hoa', 'lease', 'landlord',
                                    'mold', 'house']},
                    {'Vehicles': ['vehicle', 'suv', 'car', 'truck']},
                    {'Transportation': ['transportation', 'car', 'road', 'train', 'highway', 'parking', 
                                        'truck', 'plane', 'traffic', 'passenger', 'driver', 'driving']},
                    {'Religion': ['religion', 'church', 'christ', 'jesus', 'lord']},
                    {'Alcohol': ['alcohol', 'beer', 'wine', 'brewing']},
                    {'Public Transit': ['public', 'train', 'route', 'bus', 'passenger', 'subway', 
                                            'line', 'transfer', 'transit', 'muni', 'bart']},
                    {'Travel': ['travel', 'adventure', 'pack', 'camera']},
                    {'Government': ['government', 'council', 'ordinance', 'complaint']},
                    {'School': ['school', 'campus', 'class', 'student', 'transfer', 'college']},
                    {'Food': ['food', 'grocery', 'store', 'sandwich']},
                    {'Restaurants': ['food', 'restaurant', 'seafood', 'pizza', 'eat', 'taco', 'service', 'dim sum',
                                     'burger']},
                    {'College': ['college', 'university', 'engineering']},
                    {'Medicine': ['vaccine', 'doctor', 'operation', 'hospital']},
                    {'Crime': ['crime', 'property crime', 'theft', 'robbery', 'police', 'abuse', 'homicide',
                                'suspect', 'offender']},
                    {'Drugs': ['drug', 'drug problem', 'violation', 'order', 'substance']},
                    {'Homelessness': ['homeless', 'problem', 'shelter', 'policy', 'depression']},
                    {'Jobs': ['career', 'job', 'resume', 'company', 'service', 'interview']},
                    {'Beaches': ['beach', 'sea', 'pier', 'island']},
                    {'Pizza': ['pizza', 'pepperoni', 'topping', 'pizza hut']},
                    {'Gaming': ['game', 'magic', 'video game', 'twitch']},
                    {'Pets': ['pet', 'cat', 'dog', 'fish', 'shelter', 'animal', 'breed', 'park', 'owner',
                                'rabbit', 'kitten']},
                    {'Service Animals': ['animal', 'service animal', 'dog', 'blind']},
                    {'Business': ['industry', 'business', 'meetup', 'job']},
                    {'Night Life': ['night', 'bar', 'drink', 'downtown']},
                    {'Ridesharing': ['taxi', 'uber', 'lyft', 'jump', 'ride']},
                    {'Co-Living': ['apartment', 'share', 'room', 'roommate']},
                    {'Elections': ['election', 'volunteer', 'campaign', 'gerrymandering', 'candidate']},
                    {'Politics': ['politics', 'republican', 'democrat', 'trump', 'dems', 'gop']},
                    {'Cycling': ['cycling', 'bike', 'lane', 'bicycle', 'ride', 'biker', 'bikers',
                                    'bike lane', 'cyclist', 'rider']},
                    {'Sports': ['sport', 'basketball', 'baseball', 'football', 'soccer', 'ballpark', 
                                'tennis', 'season', 'team', 'game']},
                    {'Bars': ['alcohol', 'license', 'owner', 'pub', 'brew', 'beer', 'draft']},
                    {'Cafes': ['coffee', 'tea', 'bean']},
                    {'Health Care': ['health', 'health care', 'coverage']},
                    {'Salons': ['hair', 'haircut', 'color', 'nails', 'facial', 'barber']},
                    {'Reading': ['reading', 'book', 'library']},
                    {'Music': ['music', 'musician', 'venue']},
                    {'Desserts': ['dessert', 'ice cream', 'cake', 'pie', 'ice', 'cream']},
                    {'LGBTQ': ['LGBT', 'queer', 'gay', 'drag', 'pride', 'transgender']},
                    {'Air Transportation': ['air', 'jet', 'aircraft', 'plane']},
                    {'Parking': ['parking', 'garage']},
                    {'Tatoos': ['tatoos', 'artist']},
                    {'Housing Problems': ['water', 'damage', 'water damage', 'mold']},
                    {'Smoking': ['cigarette', 'cigarettes', 'vape', 'cbd', 'cannabis']},
                    {'Marijuana': ['cbd', 'marijuana', 'dispensary', 'weed', 'cannabis', 'cbd oil']},
                    {'Disney': ['disney', 'disneyland', 'disneyworld']},
                    {'Internet Service': ['router', 'speed', 'xfinity', 'verizon', 'modem', 'router modem']}
                ]

    threshold = .2
    min_kw_topic = threshold * num_keywords

    def assign_topics():
        """Loop through topics keywords and assign topics from topics_dict if minimum keyword 
        match threshold is met"""
        
        cursor = connection.cursor()

        query = """SELECT tk.topic_id, string_agg(k.keyword, '-:-') AS keyword_list_db 
                    FROM keywords AS k 
                    INNER JOIN topics_keywords AS tk ON tk.keyword_id = k.keyword_id 
                    INNER JOIN topics_geo AS tg ON tg.topic_id = tk.topic_id 
                    LEFT JOIN cities AS c ON c.city_id = tg.geo_id AND tg.geo_type = 'city'
                    LEFT JOIN states AS s ON s.state_id = tg.geo_id AND tg.geo_type = 'state'
                    GROUP BY tg.geo_id, tk.topic_id
                """
        
        cursor.execute(query)
        result = cursor.fetchall()
        connection.commit()
        
        for topic_id, keywords_db in result:
            keywords_list_db = keywords_db.split('-:-')

            # loop through defined topics
            for row in topics_dict:
                for topic, keywords_list in row.items():
                    keyword_matches = len(set(keywords_list_db) & set(keywords_list))

                    if keyword_matches >= min_kw_topic:
                        query =  "UPDATE topics SET topic = %s WHERE topic_id = %s"
                        data = (topic, topic_id)
                        cursor.execute(query, data)
                        connection.commit()

    assign_topics()

    cursor = connection.cursor()

    query = """INSERT INTO topics_archive (topic, geo_type, geo_id, model_id)
                (SELECT t.topic, tg.geo_type, tg.geo_id, tg.model_id 
                FROM topics as t
                INNER JOIN topics_geo AS tg ON tg.topic_id = t.topic_id
                WHERE t.topic != 'Topic'
                )
            """
    cursor.execute(query)
    connection.commit()

    query = """INSERT INTO states_archive (sentiment_compound, sentiment_rating, ascore, state_id, model_id)
                (SELECT DISTINCT s.sentiment_compound, s.sentiment_rating, s.ascore, s.state_id, tg.model_id
                FROM states AS s
                INNER JOIN topics_geo AS tg ON tg.geo_id = s.state_id AND tg.geo_type = 'state'
                )
            """
    cursor.execute(query)
    connection.commit()

    query = """INSERT INTO cities_archive (ascore, sentiment_compound, sentiment_rating, city_id, state_id, model_id)
                (SELECT DISTINCT c.ascore, c.sentiment_compound, c.sentiment_rating, c.city_id, c.state_id, tg.model_id
                FROM cities AS c
                INNER JOIN topics_geo AS tg ON tg.geo_id = c.state_id AND tg.geo_type = 'city'
                )
            """
    cursor.execute(query)
    connection.commit()

    cursor.close()

for i in range(1): # run once or twice for testing
# for i in range(num_days):
    # Extract posts from MongoDB to list, DataFrame:
    posts = list(db.posts.find({'post_date': {'$gte': start, '$lt': end}}))
    posts_cnt = len(posts)
    if posts_cnt > 0:
        print(f'Start date: {mydate_start} End date: {mydate_end}, processing {posts_cnt}')
        generate_models(posts, mydate_start, mydate_end)
    else:
        print(f'Start date: {mydate_start} End date: {mydate_end}, 0 records, skipping')
    mydate_start += day
    mydate_end += day