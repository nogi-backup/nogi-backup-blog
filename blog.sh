#!/bin/bash

export GOOGLE_APPLICATION_CREDENTIALS=/Users/cooomma/.projects/.secrets/nogi-backup-fe683e9f479b.json
export DB_USERNAME=nogi_backup_cronjob
export DB_PASSWORD=2b45747bad47895cbce017e01f7450e3
export DB_HOST=core-db-1.crklhimepheu.ap-northeast-1.rds.amazonaws.com
export DB_PORT=3306
export DB_NAME=nogi_backup

# python3 blog.py check-blog-update
# python3 blog.py crawl_blogs
