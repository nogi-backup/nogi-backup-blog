from typing import List

from sqlalchemy import BIGINT, BOOLEAN, INT, Column, String, Table
from sqlalchemy.sql.expression import and_, select

from nogi.db import BaseModel


class NogiMembers(BaseModel):

    def __init__(self, engine, metadata, role='reader'):
        table = Table(
            'nogi_members',
            metadata,
            Column('id', INT, primary_key=True, autoincrement=True),
            Column('roma_name', String(64)),
            Column('kana_name', String(64)),
            Column('kanji_name', String(64)),
            Column('is_graduated', BOOLEAN),
            Column('created_at', BIGINT),
            Column('updated_at', BIGINT),
            extend_existing=True)
        super().__init__(engine, metadata, table, role)

    def get_member_profile(self, member_roma: str) -> dict:
        stmt = select([
            self.table.c.id,
            self.table.c.roma_name,
            self.table.c.kana_name,
            self.table.c.kanji_name,
            self.table.c.is_graduated]) \
            .where(
            and_(self.table.c.roma_name == member_roma)
        )
        row = self.execute(stmt).fetchone()
        return dict(id=row.id, roma_name=row.roma_name, kana_name=row.kana_name,  kanji_name=row.kanji_name, is_graduated=row.is_graduated)

    def get_current_members(self) -> List[dict]:
        results = []
        stmt = select([
            self.table.c.id,
            self.table.c.roma_name,
            self.table.c.kana_name,
            self.table.c.kanji_name,
            self.table.c.is_graduated]) \
            .where(
                and_(self.table.c.is_graduated == 0)
        )
        cursor = self.execute(stmt)
        row = cursor.fetchone()
        while row:
            results.append(
                dict(id=row.id, roma_name=row.roma_name, kana_name=row.kana_name,  kanji_name=row.kanji_name)
            )
            row = cursor.fetchone()
        return results
