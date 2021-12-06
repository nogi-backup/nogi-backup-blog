import pytest
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine

from nogi.db.nogi_members import NogiMembers


@pytest.mark.usefixtures('app')
class TestNogiMemberTable:

    @pytest.fixture(autouse=True)
    def before_after(self, app: dict):
        engine: Engine = app['engine']
        metadata: MetaData = app['metadata']
        self.member_table = NogiMembers(engine, metadata, schema='public', role='writer')

        metadata.drop_all()
        metadata.create_all()

        for member in app['member_list'].values():
            self.member_table.insert_new_member(**member)
        yield

    def test_get_member_profile(self, app: dict):
        member = self.member_table.get_member_profile('manatsu.akimoto')
        assert member['kanji_name'] == '秋元真夏'
        assert member['kana_name'] == 'あきもと まなつ'
        assert member['roma_name'] == 'manatsu.akimoto'
        assert member['term'] == 1

    def get_current_members(self, app: dict):
        assert self.member_table.get_current_members()
