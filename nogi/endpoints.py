import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
}


def get_web_archive_archive_snapshot_url(member_sub: str) -> str:
    return requests.get(
        url='http://web.archive.org/web/timemap/link/http://blog.nogizaka46.com/{}/'.format(member_sub),
        headers=HEADERS).text


# Nogizaka Official Blog
def get_nogi_official_archives_html(roma_name: str) -> str:
    return requests.get(url='http://blog.nogizaka46.com/{}/'.format(roma_name), headers=HEADERS).text
