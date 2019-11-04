#!/bin/bash

source ~/.profile

cd projects/pulseoftheland

echo "Generating json files in data/reports"
~/venvs/rp/bin/python ./scripts/get_posts_states.py --numdays 1
~/venvs/rp/bin/python ./scripts/get_posts_cities.py --numdays 1

echo "loading data from json files into Mongo and archive processed files"
~/venvs/rp/bin/python ./scripts/load_mongo.py --numdays 1

echo "Generating topic modeling/sentiment/ascores and insert results into PostgreSQL"
~/venvs/rp/bin/python ./scripts/model_clean.py

echo "Generating maps"
~/venvs/rp/bin/python ./scripts/generate_maps.py

echo "Copy files via wget"
cd cached_site
wget -q -e robots=off -m --user $RP_BASIC_USER --password $RP_BASIC_PASS http://$RP_IP_ADDR:$RP_PORT

cd $RP_IP_ADDR:$RP_PORT

# make sure index.html exists before copying files
if [ -e index.html ]
then
    echo "index.html exists, continue with aws commands"

    # delete dynamic S3 files
    aws s3 rm s3://www.pulseoftheland.com --quiet --recursive --exclude "*" --include "loc/*.html" \
    --include "topics/*.html" --include "keywords/*.html" --include "maps/*.png" \
    --include "graphs/*.png" --include /index.html

    # copy to S3
    aws s3 cp . s3://www.pulseoftheland.com --recursive --quiet

    # invalidate cached index.html
    aws cloudfront create-invalidation --distribution-id $RP_CF_DIST --paths /index.html
else
    echo "Failed to cd"
    exit 1
fi