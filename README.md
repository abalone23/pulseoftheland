# Pulse of the Land
## Introduction
[Pulse of the Land](https://www.pulseoftheland.com) tracks geographic areas ([states](https://github.com/abalone23/pulseoftheland/blob/master/reference/state_subs.csv) and [cities](https://github.com/abalone23/pulseoftheland/blob/master/reference/city_subs.csv)) throughout the United States based on sentiment analysis and topic modeling using posts from location-based subreddits on [Reddit](https://www.reddit.com) as well as demographic characteristics such as income and population from the census.

![screenprint](https://github.com/abalone23/pulseoftheland/blob/master/images/potl-sp.png "screenprint")

## Tools
### Python
Everything in this project is scripted using [Python](https://www.python.org/).
* GeoPandas
* Jupyter Notebooks
### APIs
* PRAW API
* PSAW API
* Google Maps API
### Architecture
* AWS
    * EC2
    * S3
    * Route 53

## Data
### Reddit
Data for the sentiment analysis and topic modeling is obtained from city and state location-based [Reddit](https://www.reddit.com) forums aka **subreddits** throughout the United States via the Pushshift.io API wrapper ([PSAW](https://github.com/dmarx/psaw)). Only locations with populations over 50,000 and over 1,000 subreddit subscribers are included. Metadata for initial subreddit subscriber count and selection is accessed via the Python Reddit API wrapper ([PRAW](https://praw.readthedocs.io/en/latest/))

* [51 states](https://github.com/abalone23/pulseoftheland/blob/master/reference/state_subs.csv) including District of Columbia
    * [notebook](https://github.com/abalone23/pulseoftheland/blob/master/notebooks/generate_state_subs_raw.ipynb) (raw)
    * [script](https://github.com/abalone23/pulseoftheland/blob/master/scripts/generate_state_subs_clean.py) (clean)
* [235 cities](https://github.com/abalone23/pulseoftheland/blob/master/reference/city_subs.csv)
    * [notebook](https://github.com/abalone23/pulseoftheland/blob/master/notebooks/generate_city_subs_raw.ipynb) (raw)
    * [script](https://github.com/abalone23/pulseoftheland/blob/master/scripts/generate_city_subs_clean.py) (clean)

### Census
The demographic data comes from:
* [Census](https://www.census.gov/data/tables/time-series/demo/popest/2010s-total-cities-and-towns.html) - population ([notebook](https://github.com/abalone23/pulseoftheland/blob/master/notebooks/generate_population.ipynb))
* [American Community Survey](https://factfinder.census.gov/faces/nav/jsf/pages/download_center.xhtml) - median income ([notebook](https://github.com/abalone23/pulseoftheland/blob/master/notebooks/generate_incomes.ipynb))

### Mapping
Coordinates are retrieved using [Google Maps API](https://developers.google.com/maps/documentation) via the [googlemaps](https://github.com/googlemaps/google-maps-services-python) Python client library. ([notebook](https://github.com/abalone23/pulseoftheland/blob/master/notebooks/generate_latlongs.ipynb))

Maps are generated using the [GeoPandas](GeoPandas) library. ([notebook](https://github.com/abalone23/pulseoftheland/blob/master/scripts/generate_maps.py))
## Analysis
### Sentiment Analysis
Sentiment analysis is performed using CountVectorizer with VADER.

### Topic Modeling
Topic modeling is performed using TextBlob.

### Rating System
The rating system uses a propietary score based on the following charactersitics:
* Sentiment
* Income
* Population

## Databases
### MongoDB
The json files are loaded into [MongoDB](https://www.mongodb.com/).
### PostgreSQL
The aggregated data including sentiment, topic modeling and scores are stored in [PostgreSQL](https://www.postgresql.org/).
#### Tables
A total of ten tables are used in the PostgreSQL schema. ([notebook](https://github.com/abalone23/pulseoftheland/blob/master/sql/create_pg_tables.sql))
* states
* cities
* topics
* keywords
* topics_keywords
* topics_geo
* models
* states_archive
* cities_archive
* topics_archive


## Web App
[pulseoftheland.com](https://www.pulseoftheland.com) is published using the web application framework [Flask](https://palletsprojects.com/p/flask/). It is then scraped internally using wget and the static files are uploaded to a public AWS S3 bucket 

## Workflow
The above process using the previous three month's data is scheduled to run on a daily basis:
1. Retrieve latest reddit data
2. Load into MongoDB
3. Run sentiment analysis
4. Run topic modeling
5. Generate maps

## Architecture
The web app runs on AWS.

### S3
* Private S3 bucket stores the Reddit json files
* Public S3 bucket hosts static HTML files

### EC2
* Python
    * scikit-learn
    * textblob
* MongoDB
* PostgreSQL