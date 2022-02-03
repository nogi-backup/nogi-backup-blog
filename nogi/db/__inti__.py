from typing import Tuple

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine


def connect(db_username: str, db_password: str, db_host: str, db_name: str) -> Tuple[Engine, MetaData]:
        _connection = 'postgresql+pg8000://{db_username}:{db_password}@{db_host}:5432/{db_name}'.format(
            db_username=db_username, db_password=db_password, db_host=db_host, db_name=db_name
        )
        _engine = create_engine(_connection, client_encoding='utf8')
        _meta = MetaData(_engine)
        return _engine, _meta