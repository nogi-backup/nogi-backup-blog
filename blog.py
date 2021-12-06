
import asyncio
import os
from random import randint, shuffle
import time

import click
from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine

from nogi.db.nogi_blogs import NogiBlog
from nogi.db.nogi_members import NogiMembers
from nogi.storages.s3 import S3
from nogi.utils.post_extractor import PostExecutor

QUEUE_LENGTH = 5


@click.command()
def crawl():
    os.makedirs('./tmp', exist_ok=True)
    _connection = 'postgresql+pg8000://{username}:{password}@{host}/{name}'.format(
        username=os.environ.get('DB_USERNAME', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'admin'),
        host=os.environ.get('DB_HOST', '127.0.0.1'),
        name=os.environ.get('DB_NAME', 'postgres')
    )

    # Connect DB
    engine: Engine = create_engine(_connection, encoding='utf8')
    metadata = MetaData(bind=engine)
    blog_db_instance = NogiBlog(engine, metadata, 'nogizaka', role='writer')
    member_db_instance = NogiMembers(engine, metadata, 'nogizaka', role='writer')

    # Create S3
    s3 = S3(bucket_name=os.environ['S3_BUCKET'])

    # List active Members
    active_members = [member['roma_name'] for member in member_db_instance.get_current_members()]
    shuffle(active_members)

    # Create Job Queue
    tasks = []
    loop = asyncio.get_event_loop()

    while active_members:
        # Create a Job for each member
        _member = active_members.pop()
        tasks.append(asyncio.ensure_future(PostExecutor(_member, blog_db_instance, s3).crawl()))

        # Fire.
        if len(tasks) >= QUEUE_LENGTH:
            loop.run_until_complete(asyncio.gather(*tasks))
            tasks = []

            # Take a break. Be aware the rate limit.
            sleep_second = randint(1, 15)
            print('Sleep for %s second. Left %d Members todo' % sleep_second, len(active_members))
            time.sleep(sleep_second)

    if tasks:
        loop.run_until_complete(asyncio.gather(*tasks))


if __name__ == "__main__":
    crawl()
