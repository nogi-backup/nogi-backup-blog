from datetime import datetime
import os
import time
from typing import Tuple

from sqlalchemy import Table, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.schema import MetaData
from sqlalchemy.sql.expression import insert, update


class BaseModel:
    def __init__(self, engine: Engine, metadata: MetaData, table: Table, role='reader'):
        self.engine = engine
        self.metadata = metadata
        self.table = table
        self.role = role

    def execute(self, stmt: str):
        return self.engine.execute(stmt)

    def raw_insert(self, row: dict):
        assert self.role == 'writer'
        row['created_at'] = datetime.utcfromtimestamp(time.time())
        row['updated_at'] = datetime.utcfromtimestamp(time.time())
        return self.execute(insert(self.table, row))

    def raw_update(self, where: dict, row: dict):
        assert self.role == 'writer'
        row['updated_at'] = datetime.utcfromtimestamp(time.time())
        return self.execute(update(self.table).where(where).values(row))
