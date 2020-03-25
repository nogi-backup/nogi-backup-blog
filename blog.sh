#!/bin/bash

echo $GCP_SERVICE_KEY | base64 --decode >/app/key.json
export GOOGLE_APPLICATION_CREDENTIALS=/app/key.json
python3 blog.py crawl --bucket nogi-blog
