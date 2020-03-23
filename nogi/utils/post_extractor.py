import asyncio
import logging
import os
import random
import time
from urllib.parse import urlparse

import aiohttp
from aiohttp import ClientSession, TCPConnector
import requests
from tqdm import tqdm

from nogi import REQUEST_HEADERS
from nogi.db.nogi_blog_content import NogiBlogContent
from nogi.db.nogi_blog_summary import NogiBlogSummary
from nogi.storages.gcs import GCS
from nogi.utils.parsers import PostParser, generate_post_key

logger = logging.getLogger()


class PostExecutor:

    def __init__(self, member: dict, summary_db: NogiBlogSummary, content_db: NogiBlogContent,  gcs_client: GCS, bucket: str, concurrent: int = 4):
        self._waiting_limit = concurrent
        self.member = member

        # DB
        self.summary_db = summary_db
        self.content_db = content_db

        # GCS Storage
        self.bucket = bucket
        self.storage = gcs_client
        self.storage_blog_post_prefix = os.path.join(member['roma_name'], 'post')
        self.storage_blog_image_prefix = os.path.join(member['roma_name'], 'img')

        # Tasks
        self.todos = [k for k in self.summary_db.get_missing_blog_url(member['id'])]

    @staticmethod
    def db_transform(post_url: str, obj: dict, **kwargs) -> dict:
        return dict(
            member_id=kwargs.get('member_id'),
            blog_key=generate_post_key(post_url),
            url=post_url,
            title=obj['title'],
            content=obj['content'],
            image_gcs_paths=kwargs.get('image_gcs_paths'),
            post_gcs_path=kwargs.get('post_gcs_path'),
            blog_created_at=int(obj['created_at'].timestamp()))

    async def backup_image(self, session: ClientSession, image_url: str):
        image_gcs_path = os.path.join(self.storage_blog_image_prefix,
                                      '/'.join(urlparse(image_url).path.split('/')[-5:]))
        try:
            async with session.get(url=image_url, headers=REQUEST_HEADERS) as response:
                self.storage.upload_stream(
                    bucket=self.bucket, blob_name=image_gcs_path,
                    content=await response.read(), content_type='image/jpeg')
            return image_gcs_path
        except aiohttp.client_exceptions.InvalidURL:
            print('Invalid URL: %s' % image_url)
        except aiohttp.client_exceptions.ClientConnectorError:
            print('Client Connector Error: %s' % image_url)

    async def backup_content(self, session: ClientSession, post_url: str) -> str:
        post_gcs_path = os.path.join(self.storage_blog_post_prefix, '/'.join(urlparse(post_url).path.split('/')[-3:]))
        try:
            async with session.get(url=post_url, headers=REQUEST_HEADERS) as response:
                self.storage.upload_stream(
                    bucket=self.bucket, blob_name=post_gcs_path,
                    content=await response.read(), content_type='text/html')
            return post_gcs_path
        except aiohttp.client_exceptions.InvalidURL:
            print('Invalid URL: %s' % post_url)
        except aiohttp.client_exceptions.ClientConnectorError:
            print('Client Connector Error: %s' % post_url)

    @staticmethod
    def crawl_post(url: str) -> None:
        return PostParser(requests.get(url, headers=REQUEST_HEADERS).text).to_dict()

    async def _run(self, url: str):
        try:
            async with aiohttp.ClientSession(connector=TCPConnector(verify_ssl=False)) as session:
                post_gcs_path = await self.backup_content(session, url)
                post = self.crawl_post(url)
                images_gcs_paths = [await self.backup_image(session, image_url) for image_url in post['image_urls']]
                result = self.db_transform(post_url=url, obj=post, member_id=self.member['id'],
                                           image_gcs_paths=images_gcs_paths, post_gcs_path=post_gcs_path)
                self.content_db.upsert_crawled_post(result)
                self.summary_db.update_crawled_result(result)
        except aiohttp.client_exceptions.InvalidURL:
            print('Invalid URL: %s' % url)
        except aiohttp.client_exceptions.ClientConnectorError:
            print('Client Connector Error: %s' % url)
        except Exception:
            import traceback
            print('Error URL: %s' % url)
            print(traceback.format_exc())

    def run(self):
        loop = asyncio.get_event_loop()
        if self.todos:
            tasks = []
            for url in tqdm(self.todos, desc='Current Member: {}'.format(self.member['kanji_name']), ncols=120):
                tasks.append(asyncio.ensure_future(self._run(url)))
                if len(tasks) > self._waiting_limit:
                    loop.run_until_complete(asyncio.gather(*tasks))
                    tasks = []
            if tasks:
                loop.run_until_complete(asyncio.gather(*tasks))

            slepp_second = random.randint(1, 15)
            print('Sleep for %s second' % slepp_second)
            time.sleep(slepp_second)
