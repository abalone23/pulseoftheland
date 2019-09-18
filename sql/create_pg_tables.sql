DROP TABLE IF EXISTS states_archive;
DROP TABLE IF EXISTS cities_archive;
DROP TABLE IF EXISTS cities;
DROP TABLE IF EXISTS states;
DROP TABLE IF EXISTS topics_keywords;
DROP TABLE IF EXISTS topics_geo;
DROP TABLE IF EXISTS keywords;
DROP TABLE IF EXISTS topics_archive;
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS topics;
DROP TYPE IF EXISTS sentiment;

CREATE TYPE sentiment AS ENUM ('neg', 'neu', 'pos');

CREATE TABLE states (
    state_id SERIAL PRIMARY KEY,
    state_name varchar(30) NOT NULL,
    state_abbr char(2) NOT NULL,
    state_fip integer NOT NULL,
    state_sub varchar(30) NOT NULL,
    sub_cnt integer NOT NULL,
    sentiment_compound float NOT NULL,
    sentiment_rating sentiment default 'neu',
    pop_2018 integer NOT NULL,
    median_hh_income integer NOT NULL,
    ascore float default 0.0 NOT NULL,
    state_lat float NOT NULL,
    state_lng float NOT NULL
);

CREATE TABLE cities (
    city_id SERIAL PRIMARY KEY,
    city_name varchar(30) NOT NULL,
    city_url varchar(30) NOT NULL,
    city_sub varchar(30) NOT NULL,
    sub_cnt integer NOT NULL,
    pop_2018 integer NOT NULL,
    median_hh_income integer NOT NULL,
    ascore float default 0.0 NOT NULL,
    sentiment_compound float NOT NULL,
    sentiment_rating sentiment default 'neu',
    city_lat float NOT NULL,
    city_lng float NOT NULL,
    state_id integer REFERENCES states (state_id)
);

CREATE TABLE topics (
    topic_id SERIAL PRIMARY KEY,
    topic varchar(30) NOT NULL,
    num_geo integer default 1 NOT NULL
);

CREATE TABLE keywords (
    keyword_id SERIAL PRIMARY KEY,
    keyword varchar(30) NOT NULL,
    num_geo integer default 1 NOT NULL
);

CREATE TABLE topics_keywords (
    id SERIAL PRIMARY KEY,
    topic_id integer REFERENCES topics (topic_id),
    keyword_id integer REFERENCES keywords (keyword_id)
);

CREATE TABLE models (
    model_id SERIAL PRIMARY KEY,
    extract_date timestamp NOT NULL
);

CREATE TABLE topics_geo (
    id SERIAL PRIMARY KEY,
    geo_type char(10) NOT NULL,
    geo_id integer NOT NULL,
    topic_id integer REFERENCES topics (topic_id),
    model_id integer REFERENCES models (model_id)
);

CREATE TABLE topics_archive (
    id SERIAL PRIMARY KEY,
    topic varchar(30) NOT NULL,
    geo_type char(10) NOT NULL,
    geo_id integer NOT NULL,    
    model_id integer REFERENCES models (model_id)
);

CREATE TABLE states_archive (
    id SERIAL PRIMARY KEY,
    sentiment_compound float NOT NULL,
    sentiment_rating sentiment NOT NULL,
    ascore float default 0.0 NOT NULL,
    state_id integer REFERENCES states (state_id),
    model_id integer REFERENCES models (model_id)
);

CREATE TABLE cities_archive (
    id SERIAL PRIMARY KEY,
    ascore float default 0.0 NOT NULL,
    sentiment_compound float NOT NULL,
    sentiment_rating sentiment NOT NULL,
    city_id integer REFERENCES cities (city_id),
    state_id integer REFERENCES states (state_id),
    model_id integer REFERENCES models (model_id)
);