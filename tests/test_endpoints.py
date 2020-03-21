import pytest
from nogi import endpoints

MEMBER = 'nanami.hashimoto'


def test_get_web_archive_post():
    # print(endpoints.get_web_archive_post(MEMBER, 2013, 8, 1))
    assert True


@pytest.mark.skip()
def test_get_web_archive_archive_ts():
    assert endpoints.get_web_archive_archive_snapshot_url(MEMBER) == \
        'http://web.archive.org/web/20130727063641/http://blog.nogizaka46.com:80/nanami.hashimoto/'
