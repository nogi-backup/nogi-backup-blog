from typing import Generator, List

from sqlalchemy import JSON, Column, Sequence, Table, select
from sqlalchemy.engine.base import Engine
from sqlalchemy.sql.expression import and_, desc, func
from sqlalchemy.sql.schema import MetaData
from sqlalchemy.sql.sqltypes import BigInteger, DateTime, Integer, String, Text

from nogi.db import BaseModel


class NogiBlog(BaseModel):

    def __init__(self, engine: Engine, metadata: MetaData, schema: str, role='reader'):
        table = Table(
            'blogs',
            metadata,
            Column('id', BigInteger, Sequence('id_seq'), primary_key=True),
            Column('blog_key', String(64), unique=True),
            Column('member_id', Integer),
            Column('url', String(255)),
            Column('title', String(255)),
            Column('blog_created_at', DateTime),
            Column('content', Text),
            Column('image_paths', JSON),
            Column('post_path', String(255)),
            Column('created_at', DateTime),
            Column('updated_at', DateTime),
            schema=schema,
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

    def get_last_blog_posts(self, member_id: int, limit: int = 1) -> List[str]:
        stmt = select([self.table.c.blog_key, self.table.c.blog_created_at]) \
            .where(and_(self.table.c.member_id == member_id)) \
            .order_by(desc(self.table.c.blog_created_at)) \
            .limit(limit)
        cursor = self.execute(stmt)
        row = cursor.fetchone()
        results = []
        while row:
            results.append(dict(blog_key=row.blog_key, blog_created_at=row.blog_created_at))
            row = cursor.fetchone()
        return results

    def get_members_latest_post_created_ts(self) -> dict:
        result = dict()
        stmt = select([
            self.table.c.member_id,
            func.max(self.table.c.blog_created_at).label('latest_post_ts')
        ]).group_by(self.table.c.member_id)
        for row in self.execute(stmt).fetchall():
            result[row.member_id] = row.latest_post_ts
        return result

    def get_missing_blog_url(self, member_id: int) -> Generator[str, None, None]:
        stmt = select([self.table.c.url]) \
            .where(and_(self.table.c.member_id == member_id, self.table.c.is_in_gcs == 0)) \
            .order_by(desc(self.table.c.created_at))
        cursor = self.execute(stmt)
        row = cursor.fetchone()
        while row:
            yield row.url
            row = cursor.fetchone()

    def insert_crawled_post(self, crawler_result: dict):
        self.raw_insert(
            dict(
                blog_key=crawler_result['blog_key'],
                member_id=crawler_result['member_id'],
                title=crawler_result['title'],
                blog_created_at=crawler_result['blog_created_at'],
                content=crawler_result['content'],
                url=crawler_result['url'],
                image_paths=crawler_result['image_paths'],
                post_path=crawler_result['post_path'],
            )
        )
