import os
import psycopg2 as pg
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas.io.sql as pd_sql
import pickle
import re

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_RP_DB = os.getenv('POSTGRES_RP_DB')

connection_args = {
    'host': POSTGRES_HOST,
    'user': POSTGRES_USER,
    'dbname': POSTGRES_RP_DB,
    'port': POSTGRES_PORT
}

connection = pg.connect(**connection_args)

with open('data/df_states.pkl', "rb") as fp:
    df_states = pickle.load(fp)

states_list = df_states.values.tolist()

cursor = connection.cursor()

query_cities = "TRUNCATE cities RESTART IDENTITY CASCADE" # CASCADE needed due to foreign key
query_states = "TRUNCATE states RESTART IDENTITY CASCADE"
cursor.execute(query_cities)
cursor.execute(query_states)

for state_name, state_abbr, state_fip, state_sub, sub_cnt, pop_2018, median_hh_income, state_lat, state_lng in states_list:
    query =  """INSERT INTO states (state_name, state_abbr, state_fip, state_sub, sub_cnt, pop_2018,
                                    median_hh_income, state_lat, state_lng, sentiment_compound)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0)"""
    data = (state_name, state_abbr, state_fip, state_sub, sub_cnt, pop_2018, \
            median_hh_income, state_lat, state_lng)

    cursor.execute(query, data)
    
connection.commit()
cursor.close()

with open('data/df_cities.pkl', "rb") as fp:
    df_cities = pickle.load(fp)

cities_list = df_cities.values.tolist()

cursor = connection.cursor()

for state_city_id, city_short, city_state, city_sub, sub_cnt, state_fip, city_fip, pop_2010, \
    pop_2018, geographic_area, city, median_hh_income, city_lat, city_lng in cities_list:
    
    query = f'SELECT state_id FROM states WHERE state_fip = {state_fip}'
    cursor.execute(query)
    state_info = cursor.fetchall()
    state_id = state_info[0][0]
    city_url = re.sub('[\s\'"]', '_', city_short).lower()
    
    query =  """INSERT INTO cities (city_name, city_url, city_sub, sub_cnt, pop_2018, state_id, 
                                    median_hh_income, city_lat, city_lng, sentiment_compound)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0)"""
    data = (city_short, city_url, city_sub, sub_cnt, pop_2018, state_id, median_hh_income, city_lat, city_lng)
    cursor.execute(query, data)
    
connection.commit()
cursor.close()