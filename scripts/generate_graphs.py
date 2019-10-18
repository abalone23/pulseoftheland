import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import psycopg2 as pg
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas.io.sql as pd_sql

connection_args = {
    'host': os.getenv('POSTGRES_HOST'),
    'user': os.getenv('POSTGRES_USER'),
    'dbname': os.getenv('POSTGRES_RP_DB'),
    'port': os.getenv('POSTGRES_PORT')
}

connection = pg.connect(**connection_args)

query = """SELECT sa.ascore, s.state_abbr, s.state_name, sa.model_id
         FROM states_archive AS sa
         INNER JOIN states AS s ON s.state_id = sa.state_id
         ORDER BY model_id"""
df_ascores = pd_sql.read_sql(query, connection)

states_list = df_ascores['state_abbr'].unique().tolist()

df_avgscores = df_ascores.groupby('model_id')['ascore'].mean().reset_index(drop=True)

for state_abbr in states_list:
    state_name = df_ascores['state_name'][(df_ascores['state_abbr'] == state_abbr) & (df_ascores['model_id'] == 1)].values[0]    
    fig, ax = plt.subplots(figsize = (16, 9))
    df_ascores['ascore'][df_ascores['state_abbr'] == state_abbr].reset_index(drop=True).plot(ax=ax, fontsize=20, linewidth=5.0, label='Daily ' + state_name + ' Score')
    df_avgscores.plot(ax=ax, fontsize=20, linewidth=3.0, linestyle='dashed', color='gray', label='Daily Avg. State Score')
    plt.xticks([]);
    ax.set_ylabel('Score', fontsize=30)
    ax.set_title(state_name + ' Daily Scores (60 Days)', fontsize=40)
    plt.tight_layout()
    leg = plt.legend(fontsize=20);
    plt.savefig(f'rpulse/static/graphs/state_{state_abbr.lower()}.png', transparent=True, bbox_inches='tight')
    plt.close(fig)

query = """SELECT c.city_id, ca.ascore, c.city_name, ca.model_id, s.state_abbr, c.city_url
         FROM cities_archive AS ca
         INNER JOIN cities AS c ON c.city_id = ca.city_id
         INNER JOIN states AS s ON s.state_id = c.state_id
         ORDER BY ca.model_id"""
df_ascores_c = pd_sql.read_sql(query, connection)

cities_list = df_ascores_c['city_id'].unique().tolist()

df_avgscores_c = df_ascores_c.groupby('model_id')['ascore'].mean().reset_index(drop=True)

for city_id in cities_list:
    state_abbr = df_ascores_c['state_abbr'][(df_ascores_c['city_id'] == city_id) & (df_ascores_c['model_id'] == 1)].values[0]    
    city_name = df_ascores_c['city_name'][(df_ascores_c['city_id'] == city_id) & (df_ascores_c['model_id'] == 1)].values[0]    
    city_url = df_ascores_c['city_url'][(df_ascores_c['city_id'] == city_id) & (df_ascores_c['model_id'] == 1)].values[0]    

    fig, ax = plt.subplots(figsize = (16, 9))
    df_ascores_c['ascore'][df_ascores_c['city_id'] == city_id].reset_index(drop=True) \
                                                              .plot(ax=ax, fontsize=20, linewidth=5.0, label='Daily ' + city_name + ' Score')
    df_avgscores_c.plot(ax=ax, fontsize=20, linewidth=3.0, linestyle='dashed', color='gray', label='Daily Avg. City Score')
    plt.xticks([]);
    ax.set_ylabel('Score', fontsize=30)
    ax.set_title(city_name + ', ' + state_abbr + ' Daily Scores (60 Days)', fontsize=40)
    plt.tight_layout()
    leg = plt.legend(fontsize=20);
    plt.savefig(f'rpulse/static/graphs/city_{state_abbr.lower()}_{city_url}.png', transparent=True, bbox_inches='tight')
    plt.close(fig)