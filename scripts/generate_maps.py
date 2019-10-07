import pickle
import os
import re
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

plt.rc('figure', max_open_warning = 0)

# project_path = os.path.join(os.path.expanduser('~'),'projects/rp')

with open('data/df_states.pkl', 'rb') as fp:
    df_states = pickle.load(fp)
with open('data/df_states_metrics.pkl', 'rb') as fp:
    df_states_metrics = pickle.load(fp)
df_states_all = pd.merge(df_states, df_states_metrics, on='state_sub')

with open('data/df_cities.pkl', 'rb') as fp:
    df_cities = pickle.load(fp)
with open('data/df_cities_metrics.pkl', 'rb') as fp:
    df_cities_metrics = pickle.load(fp)
df_cities_all = pd.merge(df_cities, df_cities_metrics, on='city_sub')

usa = gpd.read_file('data/maps/states_21basic/states.shp')
usa_continental = gpd.read_file('data/maps/states_21basic/states.shp')
crs = {'init': 'epsg:4326'}

geometry_cities = [Point(xy) for xy in zip( df_cities_all['city_lng'], df_cities_all['city_lat'])]
geo_df_cities = gpd.GeoDataFrame(df_cities_all, crs=crs, geometry=geometry_cities)

df_states_all = df_states_all.rename(columns={"state_abbr": "STATE_ABBR"})
df_states_continental = df_states_all[(df_states_all['STATE_ABBR'] != 'AK') & (df_states_all['STATE_ABBR'] != 'HI')]
usa = usa.merge(df_states_all, on='STATE_ABBR')
usa_continental = usa_continental.merge(df_states_continental, on='STATE_ABBR')

geo_df_cities_continental = geo_df_cities[(geo_df_cities['state_fip'] != 2) & (geo_df_cities['state_fip'] != 15)]

fig, ax = plt.subplots(figsize = (30, 30))

# create US map
usa_continental.plot(ax=ax, cmap='RdYlGn', edgecolor='#000000', linewidth=1, column='ascore', scheme='quantiles')

geo_df_cities_continental[(geo_df_cities_continental['sentiment_rating'] == 'pos') & 
              (geo_df_cities_continental['pop_2018'] >= 1000000)
             ].plot(ax=ax, markersize=500, color='green', marker='o', alpha=.7);

geo_df_cities_continental[
              (geo_df_cities_continental['sentiment_rating'] == 'pos') & 
              (geo_df_cities_continental['pop_2018'] < 1000000)
             ].plot(ax=ax, markersize=100, color='green', marker='o', alpha=.7);

geo_df_cities_continental[(geo_df_cities_continental['sentiment_rating'] == 'neg') & 
              (geo_df_cities_continental['pop_2018'] >= 1000000)
             ].plot(ax=ax, markersize=500, color='red', marker='o', alpha=.7);

geo_df_cities_continental[(geo_df_cities_continental['sentiment_rating'] == 'neg') & 
              (geo_df_cities_continental['pop_2018'] < 1000000)
                 ].plot(ax=ax, markersize=100, color='red', marker='o', alpha=.7);

geo_df_cities_continental[(geo_df_cities_continental['sentiment_rating'] == 'neu') &
              (geo_df_cities_continental['pop_2018'] >= 1000000)
             ].plot(ax=ax, markersize=500, color='yellow', marker='o', alpha=.7);

geo_df_cities_continental[(geo_df_cities_continental['sentiment_rating'] == 'neu') &
              (geo_df_cities_continental['pop_2018'] < 1000000)
                 ].plot(ax=ax, markersize=100, color='yellow', marker='o', alpha=.7);

for x, y, label in zip(geo_df_cities_continental.geometry.x, geo_df_cities_continental.geometry.y, geo_df_cities_continental['city_short']):
    if len(geo_df_cities_continental[(geo_df_cities_continental['pop_2018'] > 1000000) & (geo_df_cities_continental['city_short'] == label)]) == 1:
        ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords='offset points', size=20, weight='bold')
plt.axis('off');
plt.savefig('static/maps/united_states.png', transparent=True, bbox_inches='tight')


# create state maps
for state_fip in df_states_all['state_fip']:
    state_abbr = df_states_all['STATE_ABBR'][df_states_all['state_fip'] == state_fip].values[0]
    
    fig, ax = plt.subplots(figsize = (10, 10))
    usa[usa['state_fip'] == state_fip].plot(ax=ax, edgecolor='y', linewidth=2, color="#C5E1A5")
    
    geo_df_cities[(geo_df_cities['state_fip'] == state_fip) & 
                  (geo_df_cities['sentiment_rating'] == 'pos') & 
                  (geo_df_cities['pop_2018'] >= 1000000)
                 ].plot(ax=ax, markersize=500, color='#06450a', marker='o', alpha=.7);

    geo_df_cities[(geo_df_cities['state_fip'] == state_fip) & 
                  (geo_df_cities['sentiment_rating'] == 'pos') & 
                  (geo_df_cities['pop_2018'] < 1000000)
                 ].plot(ax=ax, markersize=100, color='#06450a', marker='o', alpha=.7);

    geo_df_cities[(geo_df_cities['state_fip'] == state_fip) & 
                  (geo_df_cities['sentiment_rating'] == 'neg') & 
                  (geo_df_cities['pop_2018'] >= 1000000)
                 ].plot(ax=ax, markersize=500, color='red', marker='o', alpha=.7);

    geo_df_cities[(geo_df_cities['state_fip'] == state_fip) & 
                  (geo_df_cities['sentiment_rating'] == 'neg') & 
                  (geo_df_cities['pop_2018'] < 1000000)
                 ].plot(ax=ax, markersize=100, color='red', marker='o', alpha=.7);

    geo_df_cities[(geo_df_cities['state_fip'] == state_fip) & 
                  (geo_df_cities['sentiment_rating'] == 'neu') &
                  (geo_df_cities['pop_2018'] >= 1000000)
                 ].plot(ax=ax, markersize=500, color='yellow', marker='o', alpha=.7);

    geo_df_cities[(geo_df_cities['state_fip'] == state_fip) & 
                  (geo_df_cities['sentiment_rating'] == 'neu') &
                  (geo_df_cities['pop_2018'] < 1000000)
                 ].plot(ax=ax, markersize=100, color='yellow', marker='o', alpha=.7);

    plt.axis('off');
    plt.savefig(f'static/maps/state_{state_abbr.lower()}.png', transparent=True, bbox_inches='tight')

# create city maps
for state_fip in df_states_all['state_fip']:
    state_abbr = df_states_all['STATE_ABBR'][df_states_all['state_fip'] == state_fip].values[0]

    for city_short in geo_df_cities['city_short'][geo_df_cities['state_fip'] == state_fip]:
        city_short_clean = re.sub(r"[\s']", '_', city_short).lower()
        fig, ax = plt.subplots(figsize = (10, 10))
        usa[usa['state_fip'] == state_fip].plot(ax=ax, edgecolor='y', linewidth=2, color="#C5E1A5")

        geo_df_cities[(geo_df_cities['state_fip'] == state_fip) & (geo_df_cities['city_short'] == city_short) &
                      (geo_df_cities['sentiment_rating'] == 'pos') & 
                      (geo_df_cities['pop_2018'] >= 1000000)
                     ].plot(ax=ax, markersize=500, color='#06450a', marker='o', alpha=.7);

        geo_df_cities[(geo_df_cities['state_fip'] == state_fip) & (geo_df_cities['city_short'] == city_short) &
                      (geo_df_cities['sentiment_rating'] == 'pos') & 
                      (geo_df_cities['pop_2018'] < 1000000)
                     ].plot(ax=ax, markersize=100, color='#06450a', marker='o', alpha=.7);

        geo_df_cities[(geo_df_cities['state_fip'] == state_fip) & (geo_df_cities['city_short'] == city_short) &
                      (geo_df_cities['sentiment_rating'] == 'neg') & 
                      (geo_df_cities['pop_2018'] >= 1000000)
                     ].plot(ax=ax, markersize=500, color='red', marker='o', alpha=.7);

        geo_df_cities[(geo_df_cities['state_fip'] == state_fip) & (geo_df_cities['city_short'] == city_short) &
                      (geo_df_cities['sentiment_rating'] == 'neg') & 
                      (geo_df_cities['pop_2018'] < 1000000)
                     ].plot(ax=ax, markersize=100, color='red', marker='o', alpha=.7);

        geo_df_cities[(geo_df_cities['state_fip'] == state_fip) & (geo_df_cities['city_short'] == city_short) &
                      (geo_df_cities['sentiment_rating'] == 'neu') &
                      (geo_df_cities['pop_2018'] >= 1000000)
                     ].plot(ax=ax, markersize=500, color='yellow', marker='o', alpha=.7);

        geo_df_cities[(geo_df_cities['state_fip'] == state_fip) & (geo_df_cities['city_short'] == city_short) &
                      (geo_df_cities['sentiment_rating'] == 'neu') &
                      (geo_df_cities['pop_2018'] < 1000000)
                     ].plot(ax=ax, markersize=100, color='yellow', marker='o', alpha=.7);
        
        for x, y, label in zip(geo_df_cities.geometry.x, geo_df_cities.geometry.y, geo_df_cities['city_short']):
            if label == city_short:
                ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords='offset points', size=16)
        
        plt.axis('off');
        plt.savefig(f'static/maps/city_{state_abbr.lower()}_{city_short_clean}.png', transparent=True, bbox_inches='tight')