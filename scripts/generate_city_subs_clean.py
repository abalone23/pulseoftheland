import numpy as np
import pandas as pd
import re
from datetime import datetime
import pickle
import datetime as dt

with open('../data/df_city_subs_raw.pkl', 'rb') as fp:
    df_city_subs_raw = pickle.load(fp)

def clean_cities(subs):
    cities2remove = ['newyork', 'Hamilton', 'Sparkster', 'georgetown', 'TransGoneWild', 'ElizabethTurner',
                 'Temple', 'tylerthecreator', 'lynnchu', 'LargeSnorlax', 'HollywoodUndead', 'SouthgateMemes',
                 'sandy', 'wyoming', 'enigmacatalyst', 'melbourne', 'reading', 'ontario', 'Washington',
                 'columbia', 'manchester', 'bristol', 'goodyearwelt', 'Rogers', 'ArcadiaQuest', 'Dublin',
                 'PittsburghPorn', 'sacramentor4r', 'Homesteading', 'sunrise', 'aurora', 'EstrangedAdultChild',
                 'ElizabethOlsen', 'oklahomacity', 'stlouisblues', 'alexandria', 'waterloo', 'MissionarySoles',
                 'Provocateur_Addict', 'Kirkland', 'manhattan', 'cambridge']

    df_city_subs = subs[~subs['city_sub'].isin(cities2remove)]

    # since these duplicate cities exist, drop those cities without the sub:
    # 3954040: Newark, OH, Lafayette, LA, Bloomington, IL & MN, Columbus, GA, Albany, GA, Albany, OR,
    # Bellevue, NE, Charleston, WV, Greenville, NC, Kansas City, Missouri, Lakewood, FL/CA/CO/WA,
    # Portland, ME, Springfield, IL/OR, Lawrence, MA, Lancaster, CA, Jacksonville, NC, Medford, MA,
    # Troy, MI, Wilmington, DE, Rochester, MN, St. Peters, MO, Auburn, WA, Pasadena, TX
    cities2removebyid = ['3954040', '2240735', '1706613', '2706616', '1319000', '3719000', '1301052',
                         '4101000', '3103950', '5414600', '427820', '3728080', '2938000', '1238250',
                         '639892', '843000', '5338038', '2360545', '2970000', '3974118', '4169600',
                         '2534550', '640130', '3734200', '2539835', '1772000', '2680700', '1077580',
                         '2754880', '2965126', '5303180', '4856000', '4865600']
    df_city_subs = df_city_subs[~df_city_subs['state_city_id'].isin(cities2removebyid)]

    # do NOT zero fill state_city_id or it won't JOIN correctly later on
    cities2add = [
                    ('nyc', '3651000', 'New York City', 'New_York City, New York', 189000),
                    ('SaltLakeCity', '4967000', 'Salt Lake City', 'Salt Lake City, Utah', 44400),
                    ('washingtondc', '1150000', 'Washington DC', 'Washington, District of Columbia', 84200),
                    ('nashville', '4752006', 'Nashville', 'Nashville, Tennessee', 48300),
                    ('indianapolis', '1836003', 'Indianapolis', 'Indianapolis, Indiana', 35500),
                    ('okc', '4055000', 'Oklahoma City', 'Oklahoma City, Oklahoma', 12300),
                    ('Louisville', '2148006', 'Louisville', 'Louisville, Kentucky', 23600),
                    ('ColoradoSprings', '816000', 'Colorado Springs', 'Colorado Springs, Colorado', 21700),
                    ('StLouis', '2965000', 'St. Louis', 'St. Louis, Missouri', 44700),
                    ('saintpaul', '2758000', 'St. Paul', 'St. Paul, Minnesota', 3600),
                    ('lexington', '2146027', 'Lexington', 'Lexington, Kentucky', 11700),
                    ('anchorage', '203000', 'Anchorage', 'Anchorage, Alaska', 6500),
                    ('bullcity', '3719000', 'Durham', 'Durham, North Carolina', 9800),
                    ('Sacramento', '664000', 'Sacramento', 'Sacramento, California', 32600),
                    ('AuroraCO', '804000', 'Aurora', 'Aurora, Colorado', 2600),
                    ('ColumbusGA', '1319000', 'Columbus', 'Columbus, Georgia', 1400),
                    ('rochestermn', '2754880', 'Rochester', 'Rochester, Minnesota', 2300),
                    ('springfieldMO', '2970000', 'Springfield', 'Springfield, Missouri', 7200),
                    ('StCharlesMO', '2964082', 'St. Charles', 'St. Charles, Missouri', 2000),
                    ('ProvoUtah', '4962470', 'Provo', 'Provo, Utah', 1300),
                    ('CambridgeMA', '2511000', 'Cambridge', 'Cambridge, Massachusetts', 4100)
                ]
    dfcities2add = pd.DataFrame(cities2add, columns = ['city_sub' , 'state_city_id', 'city_short' , 'city_state', 'sub_cnt']) 
    df_city_subs_final = pd.concat([df_city_subs, dfcities2add], sort=False).reset_index(drop=True)

    return df_city_subs_final

df_city_subs = clean_cities(df_city_subs_raw)

df_city_subs[['state_fip', 'city_fip']] = df_city_subs['state_city_id'].str.extract(r'(\d{1,2})(\d{5})$', expand=True)
df_city_subs = df_city_subs.astype({'state_fip': int})

pickle.dump(df_city_subs, open('../data/df_city_subs.pkl', 'wb'))