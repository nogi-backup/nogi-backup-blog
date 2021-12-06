from datetime import datetime
from typing import List

from sqlalchemy import Column, MetaData, Sequence, Table
from sqlalchemy.engine import Engine
from sqlalchemy.sql.expression import and_, select
from sqlalchemy.sql.sqltypes import Date, DateTime, Integer, String

from nogi.db import BaseModel


class NogiMembers(BaseModel):

    def __init__(self, engine: Engine, metadata: MetaData, schema: str, role='reader'):
        table = Table(
            'members',
            metadata,
            Column('id', Integer, Sequence('id_seq'), primary_key=True),
            Column('roma_name', String(64)),
            Column('kana_name', String(64)),
            Column('kanji_name', String(64)),
            Column('birthday', Date),
            Column('term', Integer),
            Column('graduation', Date),
            Column('created_at', DateTime),
            Column('updated_at', DateTime),
            schema=schema,
            extend_existing=True)
        super().__init__(engine, metadata, table, role)

    def get_member_profile(self, member_roma: str) -> dict:
        stmt = select([
            self.table.c.id,
            self.table.c.roma_name,
            self.table.c.kana_name,
            self.table.c.kanji_name,
            self.table.c.term,
            self.table.c.birthday,
            self.table.c.graduation
        ]) \
            .where(
            and_(self.table.c.roma_name == member_roma)
        )
        row = self.execute(stmt).fetchone()
        return dict(id=row.id, roma_name=row.roma_name, kana_name=row.kana_name,  kanji_name=row.kanji_name, term=row.term, birthday=row.birthday, graduation=row.graduation)

    def get_current_members(self) -> List[dict]:
        results = []
        stmt = select([
            self.table.c.id,
            self.table.c.roma_name,
            self.table.c.kana_name,
            self.table.c.kanji_name
        ]) \
            .where(
                and_(self.table.c.graduation == None)
        )
        cursor = self.execute(stmt)
        row = cursor.fetchone()
        while row:
            results.append(
                dict(id=row.id, roma_name=row.roma_name, kana_name=row.kana_name,  kanji_name=row.kanji_name)
            )
            row = cursor.fetchone()
        return results

    def insert_new_member(self, kanji_name: str, kana_name: str, roma_name: str,  term: str, birthday: datetime = None, graduation: datetime = None) -> None:
        self.raw_insert(
            dict(kanji_name=kanji_name, kana_name=kana_name, roma_name=roma_name,
                 term=term, birthday=birthday, graduation=graduation)
        )
