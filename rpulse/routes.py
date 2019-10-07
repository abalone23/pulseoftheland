from rpulse import app
from flask import render_template, url_for, flash, redirect, request
import numpy as np
import pandas as pd
import psycopg2 as pg
import pickle
from collections import defaultdict, OrderedDict, Counter

POSTGRES_USER = app.config["POSTGRES_USER"]
POSTGRES_HOST = app.config["POSTGRES_HOST"]
POSTGRES_PORT = app.config["POSTGRES_PORT"]
POSTGRES_RMT_DB = app.config["POSTGRES_RMT_DB"]

SECRET_KEY = app.config["SECRET_KEY"]

con = pg.connect(f'dbname={POSTGRES_RMT_DB} user={POSTGRES_USER} host={POSTGRES_HOST}')

@app.route("/")
def index():
    cur = con.cursor()
    query = """SELECT c.city_name, c.city_url, s.state_abbr, s.state_name, round(c.ascore::Numeric, 0) AS ascore
            FROM cities AS c
            INNER JOIN states AS s ON s.state_id = c.state_id
            ORDER BY c.ascore DESC
            LIMIT 5"""
    cur.execute(query)
    topcities = cur.fetchall()
    con.commit()

    cur = con.cursor()
    query = """SELECT s.state_name, s.state_abbr, round(s.pop_2018, -3), string_agg(t.topic, ', ') AS topics,
            round(s.sentiment_compound::Numeric, 2) AS sentiment_compound,
            round(s.median_hh_income / 1000, 0) AS median_hh_income, s.sentiment_rating, round(s.ascore::Numeric, 0) AS ascore
            FROM topics AS t
            INNER JOIN topics_geo AS tg ON tg.topic_id = t.topic_id
            INNER JOIN states AS s ON s.state_id = tg.geo_id
            WHERE tg.geo_type = 'state'
            GROUP BY s.state_name, s.pop_2018, s.state_abbr,
            s.sentiment_compound, s.median_hh_income, s.sentiment_rating, s.ascore
            ORDER BY s.state_name"""
    cur.execute(query)
    results = cur.fetchall()
    con.commit()

    states_dict = {}
    for state_name, state_abbr, pop_2018, topics, sentiment_compound, median_hh_income, sentiment_rating, ascore in results:
        topics = topics.split(', ')

        clean_topics = [f'<a href="/topics/{topic.lower()}.html">{topic}</a>' for topic in topics if topic != 'Topic']

        if len(clean_topics):
            clean_topics = ', '.join(clean_topics)
        else:
            clean_topics = '-'

        states_dict[state_abbr] = [state_name, state_abbr, pop_2018, clean_topics, sentiment_compound, median_hh_income, sentiment_rating, ascore]

    return render_template('index.html',
                            title='Pulse of the Land',
                            states=states_dict, topcities=topcities)

@app.route("/loc/<state_abbr>.html")
def state(state_abbr):
    cur = con.cursor()
    query = """SELECT state_name, round(pop_2018, -3), round(sub_cnt, -3), state_sub,
             round(sentiment_compound::Numeric, 2) AS sentiment_compound,
             round(median_hh_income, -3), sentiment_rating, round(ascore::Numeric, 0) AS ascore
             FROM states WHERE state_abbr = %s"""
    data = (state_abbr,)
    cur.execute(query, data)
    row = cur.fetchone()

    if row is not None:
        state_info = {}
        state_info['state_name'] = row[0]
        state_info['pop_2018'] = f'{row[1]:,}'
        state_info['sub_cnt'] = f'{row[2]:,}'
        state_info['state_sub'] = row[3]
        state_info['sentiment_compound'] = row[4]
        state_info['median_hh_income'] = f'{row[5]:,}'
        state_info['sentiment_rating'] = row[6]
        state_info['ascore'] = row[7]

        con.commit()

        cur = con.cursor()
        # WHERE s.state_abbr = %s and tg.geo_type = 'city' AND t.topic != 'Topic'
        query = """SELECT round(c.pop_2018, -3), c.city_name, c.city_url, string_agg(t.topic, ', ') AS topics,
                    round(c.sentiment_compound::Numeric, 2) AS sentiment_compound,
                    round(c.median_hh_income, -3), c.sentiment_rating, round(c.ascore::Numeric, 0) AS ascore
                    FROM topics AS t
                    INNER JOIN topics_geo AS tg ON tg.topic_id = t.topic_id
                    INNER JOIN cities AS c ON c.city_id = tg.geo_id
                    INNER JOIN states AS s ON s.state_id = c.state_id
                    WHERE s.state_abbr = %s and tg.geo_type = 'city'
                    GROUP BY c.city_name, c.city_url, c.pop_2018, c.sentiment_compound,
                             c.median_hh_income, c.sentiment_rating, c.ascore
                    order by c.city_name"""

        data = (state_abbr,)
        cur.execute(query, data)
        results = cur.fetchall()

        cities_dict = {}
        for pop_2018, city_name, city_url, topics, sentiment_compound, median_hh_income, sentiment_rating, ascore in results:
            topics = topics.split(', ')

            clean_topics = [f'<a href="/topics/{topic.replace(" ", "_").lower()}.html">{topic}</a>' for topic in topics if topic != 'Topic']

            if len(clean_topics):
                clean_topics = ', '.join(clean_topics)
            else:
                clean_topics = 'Undefined Topics'
        
            cities_dict[city_url] = [pop_2018, city_name, city_url, clean_topics, sentiment_compound, median_hh_income, sentiment_rating, ascore]
        
        return render_template('state.html', title=state_info['state_name'], state_info=state_info, cities=cities_dict, state_abbr=state_abbr)
    else:
        return '404'

@app.route("/loc/<state_abbr>/<city>.html")
def city(state_abbr, city):
    # city = city.replace('_', ' ')

    cur = con.cursor()
    query = """SELECT s.state_name, c.city_name, round(c.pop_2018, -3), round(c.sub_cnt, -3), c.city_sub,
             round(c.sentiment_compound::Numeric, 2) AS sentiment_compound,
             round(c.median_hh_income, -3), c.sentiment_rating, round(c.ascore::Numeric, 0) AS ascore,
             c.city_url
             FROM states as s
             INNER JOIN cities AS c ON c.state_id = c.state_id
             WHERE state_abbr = %s AND c.city_url = %s"""
    data = (state_abbr, city)
    cur.execute(query, data)
    row = cur.fetchone()

    city_info = {}
    city_info['state_name'] = row[0]
    city_info['city_name'] = row[1]
    city_info['pop_2018'] = f'{row[2]:,}'
    city_info['sub_cnt'] = f'{row[3]:,}'
    city_info['city_sub'] = row[4]
    city_info['sentiment_compound'] = row[5]
    city_info['median_hh_income'] = f'{row[6]:,}'
    city_info['sentiment_rating'] = row[7]
    city_info['ascore'] = row[8]
    city_info['city_url'] = row[9]
    con.commit()

    cur = con.cursor()
    query = "SELECT t.topic, t.topic_id, k.keyword, k.num_geo \
            FROM keywords as k \
            JOIN topics_keywords as tk ON tk.keyword_id = k.keyword_id \
            JOIN topics AS t ON t.topic_id = tk.topic_id \
            JOIN topics_geo as tg ON tg.topic_id = tk.topic_id \
            JOIN cities as c ON c.city_id = tg.geo_id \
            JOIN states as s ON s.state_id = c.state_id \
            WHERE s.state_abbr = %s AND c.city_url = %s and tg.geo_type = 'city' \
            order by tk.topic_id"
    con.commit()

    data = (state_abbr, city)
    cur.execute(query, data)
    topics = cur.fetchall()

    topic_dict = {}
    topic_dict = defaultdict(list)

    for topic, topic_id, keyword, num_geo in topics:
        if num_geo > 1:
            keyword_url = keyword.replace(' ', '_')
            keyword = f'<a href="/keywords/{keyword_url}.html">{keyword}</a>'

        if topic == 'Topic':
            topic = f'Topic {topic_id}'
        else:
            topic_url = topic.replace(' ', '_').lower()
            topic = f'<a href="/topics/{topic_url}.html">{topic}</a>'

        topic_dict[topic].append(keyword)

    for t, kws in topic_dict.items():
            # print(kw)
        topic_dict[t] = ', '.join(kws)

    topic_dict = OrderedDict(sorted(topic_dict.items()))
    # topic_dict = sorted(topic_dict.keys())
    # print(topic_dict)
    return render_template('cities.html', title=city_info['city_name']+', '+city_info['state_name'], topics=topics, state_abbr=state_abbr, city_info=city_info, topic_dict=topic_dict)

@app.route("/about.html")
def about():
    return render_template('about.html', title='About')

@app.route("/terms.html")
def terms():
    return render_template('terms.html', title='Terms')

@app.route("/privacy.html")
def privacy():
    return render_template('privacy.html', title='Privacy')

@app.route("/keywords/<keyword>.html")
def keywords(keyword):
    keyword_spaces = keyword.replace('_', ' ')
    cur = con.cursor()
    query = """SELECT c.city_name, c.city_url, s.state_abbr, t.topic, s.state_name,
            round(c.pop_2018, -3), round(c.median_hh_income, -3), c.sentiment_rating, round(c.ascore::Numeric, 0) AS ascore
            FROM keywords AS k
            INNER JOIN topics_keywords AS tk ON tk.keyword_id = k.keyword_id
            INNER JOIN topics AS t on t.topic_id = tk.topic_id
            INNER JOIN topics_geo AS tg ON tg.topic_id = tk.topic_id AND tg.geo_type = 'city'
            INNER JOIN cities AS c ON c.city_id = tg.geo_id
            INNER JOIN states AS s ON s.state_id = c.state_id
            WHERE k.keyword = %s
            GROUP BY c.city_name, city_url, s.state_abbr, t.topic, s.state_name, k.keyword_id,
                     c.pop_2018, c.median_hh_income, c.sentiment_rating, c.ascore
            ORDER BY c.city_name, k.keyword_id"""
    data = (keyword_spaces,)
    cur.execute(query, data)
    keywords = cur.fetchall()

    return render_template('keywords.html', title=keyword, kw_info=keywords, keyword=keyword, keyword_spaces=keyword_spaces)

@app.route("/topics/<topic>.html")
def topics(topic):
    topic_spaces = topic.title().replace('_', ' ')
    # print(topic_spaces)
    cur = con.cursor()
    query = """SELECT DISTINCT c.city_name, c.city_url, s.state_abbr, t.topic, s.state_name, 
                round(c.pop_2018, -3), round(c.median_hh_income, -3), c.sentiment_rating, round(c.ascore::Numeric, 0) AS ascore
                FROM topics AS t
                INNER JOIN topics_geo AS tg ON tg.topic_id = t.topic_id AND tg.geo_type = 'city'
                INNER JOIN cities AS c ON c.city_id = tg.geo_id
                INNER JOIN states AS s ON s.state_id = c.state_id
                WHERE t.topic = %s
                ORDER BY t.topic, c.city_name"""
    data = (topic_spaces,)
    cur.execute(query, data)
    topics = cur.fetchall()

    return render_template('topics.html', title=topic, topic_info=topics, topic=topic, topic_spaces=topic_spaces)