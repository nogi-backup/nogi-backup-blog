"""Updater.py
Objective: Check DB Record is updated.
"""
import os
import time
import traceback

from MySQLdb._exceptions import IntegrityError
import requests

from nogi import REQUEST_HEADERS, endpoints
from nogi.db.nogi_blog_summary import NogiBlogSummary
from nogi.utils import notification
from nogi.utils.parsers import (BlogParser, generate_post_key,
                                parse_official_archive_urls)


class Updater:

    CRAWL_FROM = 'blog.nogizaka46.com'

    def __init__(self, member: dict, latest_post_ts: int, blog_db: NogiBlogSummary, do_scan_all: bool = False):
        self.member = member
        self.progress_db = blog_db
        self.latest_post_ts = latest_post_ts
        self.new_blogs = []

        home_page = endpoints.get_nogi_official_archives_html(member['roma_name'])
        self.urls = parse_official_archive_urls(home_page)
        self._scan_all = do_scan_all if do_scan_all else not bool(self.latest_post_ts)
        self.slack_url = os.environ.get('SLACK_HOOK')
        self.channel_name = os.environ.get('CHANNEL_NAME')

    def _push_notification(self, new_post: dict):
        requests.post(
            url=self.slack_url,
            headers={'Content-Type': "application/json", 'cache-control': "no-cache"},
            json=notification.render_slack_message(
                title=new_post['title'],
                member=self.member,
                blog_created_at=new_post['blog_created_at'],
                url=new_post['url'],
                channel_name=self.channel_name
            ))

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
        for abstract in page.get_page_blog_abstract():
            if abstract and abstract['created_at'] > self.latest_post_ts:
                posts.append(self.db_transform(obj=abstract, member_id=self.member['id'], crawl_from=self.CRAWL_FROM))
            else:
                break
        return posts

    def run(self):
        new_posts = []
        for url in self.urls:
            new_post = self.extract_page(BlogParser(requests.get(url, headers=REQUEST_HEADERS).text))
            if new_post:
                new_posts.extend(new_post)
            elif self._scan_all:
                continue
            else:
                break
        if not new_posts:
            print('{} No New Post.'.format(self.member['roma_name']))
            return

        print(new_posts)
        for post in new_posts:
            post['created_at'] = int(time.time())
            if self.slack_url:
                self._push_notification(post)
            try:
                self.progress_db.raw_insert(post)
            except IntegrityError:
                pass
            except Exception:
                print(traceback.format_exc())
        return dict(member=self.member['roma_name'], new_posts=len(new_posts))
