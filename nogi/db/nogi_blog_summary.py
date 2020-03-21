from typing import Generator

from sqlalchemy import BIGINT, BOOLEAN, INT, JSON, Column, String, Table
from sqlalchemy.sql.expression import and_, desc, select

from nogi.db import BaseModel


class NogiBlogSummary(BaseModel):

    def __init__(self, engine, metadata, role='reader'):
        table = Table(
            'nogi_blog_summary',
            metadata,
            Column('id', INT, primary_key=True, autoincrement=True),
            Column('member_id', INT),
            Column('blog_key', String(64), unique=True),
            Column('url', String(255)),
            Column('title', String(255)),
            Column('blog_created_at', BIGINT),
            Column('crawl_from', String(64)),
            Column('is_in_gcs', BOOLEAN, default=False),
            Column('image_gcs_paths', JSON),
            Column('post_gcs_path', String(255)),
            Column('created_at', BIGINT),
            Column('updated_at', BIGINT),
            extend_existing=True)
        super().__init__(engine, metadata, table, role)

    def get_member_blog_keys(self, member_id: int) -> Generator[str, None, None]:
        stmt = select([self.table.c.blog_key]) \
            .where(and_(self.table.c.member_id == member_id)) \
            .order_by(self.table.c.created_at)
        cursor = self.execute(stmt)
        row = cursor.fetchone()
        while row:
            yield row.blog_key
            row = cursor.fetchone()

    def get_last_post_meta(self, member_id: int) -> dict:
        stmt = select([self.table.c.blog_key, self.table.c.blog_created_at]) \
            .where(and_(self.table.c.member_id == member_id)) \
            .order_by(desc(self.table.c.blog_created_at)).limit(1)
        row = self.execute(stmt).fetchone()
        return dict(blog_key=row.blog_key, blog_created_at=row.blog_created_at) if row else dict()

    def get_missing_blog_url(self, member_id: int) -> Generator[str, None, None]:
        stmt = select([self.table.c.url]) \
            .where(and_(self.table.c.member_id == member_id, self.table.c.is_in_gcs == 0)) \
            .order_by(desc(self.table.c.created_at))
        cursor = self.execute(stmt)
        row = cursor.fetchone()
        while row:
            yield row.url
            row = cursor.fetchone()

    def update_crawled_result(self, crawler_result: dict):
        self.raw_update(
            where=and_(self.table.c.blog_key == crawler_result['blog_key']),
            row=dict(
                is_in_gcs=True,
                title=crawler_result['title'],
                image_gcs_paths=crawler_result['image_gcs_paths'],
                post_gcs_path=crawler_result['post_gcs_path']))
