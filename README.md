# Pulse of the Land
## Introduction
[Pulse of the Land](https://www.pulseoftheland.com) rates geographic areas ([states](https://github.com/abalone23/pulseoftheland/blob/master/reference/state_subs.csv) and [cities](https://github.com/abalone23/pulseoftheland/blob/master/reference/city_subs.csv)) around the United States based on sentiment analysis and topic modeling using posts from location-based subreddits on [Reddit](https://www.reddit.com) as well as demographic characteristics such as income and population from the census.

## Data
### Reddit
[Reddit](https://www.reddit.com) is a discussion website organized by subjects including geographic location. Information for the sentiment analysis and topic modeling is obtained from city and state location-based subreddits across the United States via the [Pushshift.io API wrapper](https://github.com/dmarx/psaw). Only locations with populations over 50,000 and over 1,000 subreddit subscribers are included.

* [51 states](https://github.com/abalone23/pulseoftheland/blob/master/reference/state_subs.csv) (including District of Columbia)
* [235 cities](https://github.com/abalone23/pulseoftheland/blob/master/reference/city_subs.csv)

### Census
The demographic data comes from:
* [Census](https://www.census.gov/data/tables/time-series/demo/popest/2010s-total-cities-and-towns.html) (population)
* [American Community Survey](https://factfinder.census.gov/faces/nav/jsf/pages/download_center.xhtml) (median income)

### Mapping
Coordinates are retrieved using [Google Maps API](https://developers.google.com/maps/documentation) via the [googlemaps](https://github.com/googlemaps/google-maps-services-python) Python client library.

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

## Web App
The web app is published using Flask.

## Workflow
The above process using the previous three month's data is scheduled to run on a daily basis via Apache Airflow:
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

## Miscellaneous
This is the final project for the SF15 Metis data science cohort. Thanks to Adam, Jonathan, Kelly and all my cohort mates over the summer.