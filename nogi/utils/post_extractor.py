from io import BytesIO
import logging
import os
from typing import List
from urllib.parse import urlparse

import requests

from nogi.db.nogi_blogs import NogiBlog
from nogi.storages.s3 import S3
from nogi.utils import parsers
from nogi.utils.parsers import PostParser, generate_post_key

logger = logging.getLogger()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
}


class PostExecutor:

    def __init__(self, member: dict, blog_db: NogiBlog, s3: S3, concurrent: int = 4):
        self._waiting_limit = concurrent
        self.member = member
        self.post_prefix = os.path.join(member['roma_name'], 'post')
        self.image_prefix = os.path.join(member['roma_name'], 'img')

        # DB
        self.db = blog_db

        # S3
        self.s3 = s3

    # Stage 1: Check updates

    def _get_member_last_posts_on_blog(self, page_number: int = 1) -> List[str]:
        page = requests.get(
            url='https://blog.nogizaka46.com/{roma_name}/'.format_map(self.member),
            params=dict(p=page_number),
            headers=HEADERS
        )
        return parsers.parse_post_urls_in_blog_page(page.text)

    def check_latest_posts(self) -> List[str]:
        last_blog = self.db.get_last_blog_posts(member_id=self.member['id'])
        latest_blog_keys: str = last_blog['blog_key']
        todos = []

        page_number = 1
        while page_number:
            for url in self._get_member_last_posts_on_blog(page_number):
                if parsers.generate_post_key(url) == latest_blog_keys:
                    return todos
                todos.append(url)
            page_number += 1

    # Stage 2: Crawl

    @staticmethod
    def crawl_post(url: str) -> PostParser:
        return PostParser(requests.get(url, headers=HEADERS).text)

    def _backup_content(self, post_url: str) -> str:
        object_name = '/'.join(urlparse(post_url).path.split('/')[-3:])
        try:
            with requests.get(url=post_url, headers=HEADERS) as response:
                self.s3.upload_object(prefix=self.post_prefix, object_name=object_name, object_content=response.read())
            return object_name
        except:
            pass

    def _backup_images(self, image_urls: List[dict]) -> List[str]:
        downloaded_image_urls = []
        for url in image_urls:
            content = None
            object_name = '/'.join(urlparse(url['image_url']).path.split('/')[-5:])

            if url['high_resolution_url'] != url['image_url']:
                hd_image = self._get_hd_image(url['high_resolution_url'])
                if hd_image:
                    content = hd_image.read()
            else:
                image = requests.get(url=url['image_url'])
                if image.status_code == 200:
                    content = image.content

            self.s3.upload_object(prefix=self.image_prefix, object_name=object_name, object_content=content)
            downloaded_image_urls.append(url)
        return downloaded_image_urls

    # Utils

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
            blog_created_at=obj['created_at'],
        )

    @staticmethod
    def _get_hd_image(url: str) -> BytesIO:
        first_layer_response = requests.get(url, headers=HEADERS)
        logger.debug(first_layer_response.cookies)
        resp = requests.get(
            url=url.replace('http://dcimg.awalker.jp/v/', 'http://dcimg.awalker.jp/i/'),
            cookies=first_layer_response.cookies)
        logger.debug(resp.status_code)
        logger.debug(resp.headers)
        return BytesIO(resp.content) if resp.status_code == 200 else BytesIO(bytes=b'')

    async def crawl(self):
        print('Current Member: %s' % self.member['kanji_name'])

        # Check Latest Post
        todos = self.check_latest_posts()
        print('To be update posts: %d' % len(todos))

        # Crawl Latest Posts which are not in Database
        for post_url in todos:
            post_obj = self.crawl_post(post_url)
            # - Crawl the Content -> Database
            self._backup_content(post_obj.post_content)
            # - Crawl the Image -> S3
            self._backup_images(post_obj.post_content_images)
