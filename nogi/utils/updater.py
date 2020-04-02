"""Updater.py
Objective: Check DB Record is updated.
"""
import os
import time

from MySQLdb._exceptions import IntegrityError
import requests

from nogi import REQUEST_HEADERS, endpoints
from nogi.db.nogi_blog_summary import NogiBlogSummary
from nogi.utils import notification
from nogi.utils.parsers import (BlogParser, generate_post_key,
                                parse_official_archive_urls)


class Updater:

    CRAWL_FROM = 'blog.nogizaka46.com'

    def __init__(self, member: dict, blog_db: NogiBlogSummary, do_scan_all: bool = False):
        self.member = member
        self.progress_db = blog_db
        self.latest_blog_keys = self.progress_db.get_last_blog_posts(member_id=member['id'], limit=10)
        self.new_blogs = []

        home_page = endpoints.get_nogi_official_archives_html(member['roma_name'])
        self.urls = parse_official_archive_urls(home_page)
        self._scan_all = do_scan_all
        self.slack_url = os.environ.get('SLACK_WEBHOOK')
        self.slack_channel_name = os.environ.get('SLACK_CHANNEL_NAME')
        self.telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.telegram_channel_name = os.environ.get('TELEGRAM_CHANNEL_NAME')

    @staticmethod
    def db_transform(obj: dict, **kwargs) -> dict:
        return dict(
            member_id=kwargs.get('member_id'),
            blog_key=generate_post_key(obj['url']),
            title=obj['title'],
            url=obj['url'],
            blog_created_at=obj['created_at'],
            crawl_from=kwargs.get('crawl_from'))

    def extract_page(self, page: BlogParser):
        posts = []
        latest_blog_keys = {x['blog_key'] for x in self.latest_blog_keys}
        last_blog_created_at = self.latest_blog_keys[0]['blog_created_at']

        for abstract in page.get_page_blog_abstract():
            if abstract and abstract['created_at'] > last_blog_created_at and abstract['key'] not in latest_blog_keys:
                posts.append(self.db_transform(obj=abstract, member_id=self.member['id'], crawl_from=self.CRAWL_FROM))
        return posts

    def run(self):
        new_posts = []
        for url in self.urls:
            new_posts.extend(self.extract_page(BlogParser(requests.get(url, headers=REQUEST_HEADERS).text)))

        if not new_posts:
            print('{} No New Post.'.format(self.member['roma_name']))
            return

        print(self.latest_blog_keys, new_posts)
        for post in new_posts:
            post['created_at'] = int(time.time())
            try:
                self.progress_db.raw_insert(post)
            except IntegrityError:
                print(post)
            if self.slack_url and self.slack_channel_name:
                notification.send_slack_notification(
                    url=self.slack_url, channel_name=self.slack_channel_name, member=self.member, post=post
                )
            if self.telegram_bot_token and self.telegram_channel_name:
                notification.send_telegram_notification(
                    token=self.telegram_bot_token, channel_name=self.telegram_channel_name, member=self.member, post=post
                )
        return dict(member=self.member['roma_name'], new_posts=len(new_posts))
