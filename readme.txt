Procedure:
1. generate_city_subs_raw.ipynb.ipynb
    * use PSAW api to retrieve city subs
    * generate:
        * data/df_city_subs_raw.pkl

2. generate_city_subs_clean.py
    * use:
        * data/df_city_subs_raw.pkl
    * delete invalid cities, add missing cities
    * generate:
        * data/df_city_subs.pkl

3. generate_state_subs_raw.ipynb
    * use PSAW api to retrieve state subs
    * generate:
        * data/df_city_subs_raw.pkl

4. generate_state_subs_clean.py
    * use:
        * data/df_state_subs_raw.pkl
    * update invalid state subs
    * generate:
        * data/df_state_subs.pkl

5. generate_population.ipynb
    * use:
        * data/sources/data/sources/cities_pop.csv
        * data/sources/nst-est2018-alldata.csv
    * generate:
        * data/df_states_income.pkl
        * data/df_cities_income.pkl

6. generate_incomes.ipynb
    * use:
        * data/sources/ACS_17_5YR_GCT1901.US13PR_with_ann.csv [median household income]
    * generate:
        * data/df_states_income.pkl
        * data/df_cities_income.pkl

7. generate_latlongs.ipynb
    * use:
        * data/df_state_subs.pkl
        * data/df_city_subs.pkl
    * get location coordinates
    * generate:
        * data/geocode_result_states.pkl [list]
        * data/df_geo_cities.pkl [dataframe]

8. combine_dfs_cities.ipynb
    * use:
        * data/df_city_subs.pkl
        * data/df_cities_pop.pkl
        * data/df_cities_income.pkl
        * data/df_geo_cities.pkl
    * join dataframes
    * generate:
        * data/df_cities.pkl

9. combine_dfs_states.ipynb
    * use:
        * data/df_state_subs.pkl
        * data/df_states_pop.pkl
        * data/df_states_income.pkl
        * data/geocode_result_states.pkl
    * join dataframes
    * generate:
        * data/df_states.pkl

10. get_post_states.py
    * use PSAW api to retrieve reddit data
    * json files for each sub and each month saved to data/cities

11. get_post_cities.py
    * use PSAW api to retrieve reddit data
    * json files for each sub and each month saved to data/cities

12. load_mongo.ipynb
    * load city json files into MongoDB collection

13. create_pg_tables.sql
    * create Postgres states and cities tables
        * psql -d rpdb < create_pg_tables.sql
        * Note: CREATE DATABASE rpdb; should be run previously

14. prep_pg_tables.ipynb
    * INSERT states and cities data into Postgres

15. model_cities.ipynb
    * NLP topic modeling etc

16. export:
    * run:
        psql -d rpdb < ./sql/export_tables.sql

    copy local to stage:
    scp *.csv ec2metisprod:projects/rp/data

    import:
    * regenerate tables

    * run:
        psql -d rpdb < ./sql/import_tables.sql

17. local wget to scrape website
    cd ~/python/projects/metis/project_5/cached_site
    * wget -q -e robots=off -m  http://ip_address:5000

18. aws cli copy to s3
    cd /path/to/stage_site/cached_site/ip_address:5000
    * aws s3 cp . s3://www.pulseoftheland.com --recursive --quiet