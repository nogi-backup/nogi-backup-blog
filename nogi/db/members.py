from typing import List

from sqlalchemy import (VARCHAR, BigInteger, Column, Constraint, Date, Integer,
                        MetaData, Table)
from sqlalchemy.engine import Engine
from sqlalchemy.sql.expression import and_, select


class Members:

    def __init__(self, engine: Engine, metadata: MetaData):
        self.engine = engine
        self.table = Table(
            'members',
            metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('roma_name', VARCHAR(64)),
            Column('kana_name', VARCHAR(64)),
            Column('kanji_name', VARCHAR(64)),
            Column('birthday', Date),
            Column('term', Integer),
            Column('graduation', Date),
            Column('created_at', BigInteger),
            Column('updated_at', BigInteger),
            Constraint('nogi_members_pkey'),
            schema='nogizaka',
        )

    def get_member_profile(self, member_roma: str) -> dict:
        stmt = select([
            self.table.c.id,
            self.table.c.roma_name,
            self.table.c.kana_name,
            self.table.c.kanji_name,
            self.table.c.graduation]) \
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
            self.table.c.graduation,
        ]) \
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
