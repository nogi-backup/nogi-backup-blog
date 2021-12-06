import os

import pytest
from sqlalchemy import MetaData, create_engine, engine
from nogi import members


@pytest.fixture
def app():
    app = dict()

    _connection = 'postgresql+pg8000://{username}:{password}@{host}/{name}'.format(
        username=os.environ.get('DB_USERNAME', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'admin'),
        host=os.environ.get('DB_HOST', '127.0.0.1'),
        name=os.environ.get('DB_NAME', 'postgres')
    )
    engine = create_engine(_connection, encoding='utf8')
    metadata = MetaData(bind=engine)
    app['engine'], app['metadata'] = engine, metadata
    app['member_list'] = members.MEMBERS

    return app
