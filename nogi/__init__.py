import logging
import os

from nogi.db import create_engine_and_metadata

engine, metadata = create_engine_and_metadata()

os.makedirs('./tmp', exist_ok=True)


REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
