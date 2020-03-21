from sqlalchemy import BIGINT, INT, TEXT, Column, String, Table

from nogi.db import BaseModel

# from sqlalchemy.sql.expression import and_, desc, select


class NogiBlogContent(BaseModel):

    def __init__(self, engine, metadata, role='reader'):
        table = Table(
            'nogi_blog_context',
            metadata,
            Column('id', INT, primary_key=True, autoincrement=True),
            Column('blog_key', String(64), unique=True),
            Column('member_id', INT),
            Column('title', String(255)),
            Column('blog_created_at', BIGINT),
            Column('content', TEXT),
            Column('url', String(255)),
            Column('created_at', BIGINT),
            Column('updated_at', BIGINT),
            extend_existing=True)
        super().__init__(engine, metadata, table, role)

    def upsert_crawled_post(self, crawler_result: dict):
        self.raw_upsert(
            dict(
                blog_key=crawler_result['blog_key'],
                member_id=crawler_result['member_id'],
                title=crawler_result['title'],
                blog_created_at=crawler_result['blog_created_at'],
                content=crawler_result['content'],
                url=crawler_result['url']))
