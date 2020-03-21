import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
}

# Bilibili Videos Backup


def get_channel_info(member_id: int):
    return requests.get(
        url='https://api.bilibili.com/x/space/acc/info',
        params=dict(mid=member_id, jsonp='jsonp'),
        headers=HEADERS,).json()


def get_videos(member_id: int, page_num: int = 1, page_size: int = 30, keyword: str = None) -> list:
    return requests.get(
        url='https://space.bilibili.com/ajax/member/getSubmitVideos',
        params=dict(
            mid=member_id, pagesize=page_size, tid=0,
            page=page_num, keyword=keyword, order='pubdate'),
        headers=HEADERS,).json()


# Nogizaka Web Archive Backup

def get_web_archive_archive_snapshot_url(member_sub: str) -> str:
    return requests.get(
        url='http://web.archive.org/web/timemap/link/http://blog.nogizaka46.com/{}/'.format(member_sub),
        headers=HEADERS).text


# Nogizaka Official Blog
def get_nogi_official_archives_html(roma_name: str) -> str:
    return requests.get(url='http://blog.nogizaka46.com/{}/'.format(roma_name), headers=HEADERS).text
