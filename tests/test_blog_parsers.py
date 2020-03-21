import os
from datetime import datetime
import requests

from nogi.utils import parsers

HTML_STRING = open(os.path.join(os.path.dirname(__file__), 'blog_sample.html'),  'r').read()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}


def test_generate_post_key():
    sample = 'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/001000.php'
    assert parsers.BlogParser._generate_post_key(sample) == 'nanami.hashimoto_2011_11_001000'


def test_parse_images():
    results = parsers.BlogParser(HTML_STRING).post_images
    assert len(results) == 4
    assert results == [
        'https://web.archive.org/web/20120305131600im_/http://blog.nogizaka46.com/photos/uncategorized/2011/11/17/f1010105.jpg',
        'https://web.archive.org/web/20120305131600im_/http://blog.nogizaka46.com/photos/uncategorized/2011/11/17/f1010455.jpg',
        'https://web.archive.org/web/20120305131600im_/http://blog.nogizaka46.com/photos/uncategorized/2011/11/16/f1010464.jpg',
        'https://web.archive.org/web/20120305131600im_/http://blog.nogizaka46.com/photos/uncategorized/2011/11/16/f1010461.jpg']


def test_parse_blog_url():
    results = parsers.BlogParser(HTML_STRING).blog_urls
    assert len(results) == 5
    assert results == [
        'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/001000.php',
        'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/000999.php',
        'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/000998.php',
        'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/000997.php',
        'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/000996.php']


def test_parse_post_date():
    assert [datetime.strftime(result, '%Y/%m/%d') for result in parsers.BlogParser(HTML_STRING).blog_dates] == [
        '2011/11/17',
        '2011/11/16',
        '2011/11/16',
        '2011/11/14',
        '2011/11/13', ]


def test_parse_blog_title():
    assert [x for x in parsers.BlogParser(HTML_STRING).blog_titles] == [
        'しらたま ( ´_ゝ｀)',
        'はちみつ生姜湯で風邪予防♪',
        '今日地元では雪が積もったみたいです(^^)',
        '眠いよーーっ。',
        'お初です。']


def test_parse_blog_total_page():
    assert parsers.BlogParser(HTML_STRING).blog_next_pages == [
        '?page=1',
        '?page=2',
        '?page=3',
        '?page=4',
        '?page=5',
        '?page=all']


def test_get_blog_stat():
    assert parsers.BlogParser(HTML_STRING).get_page_blog_stats() == [
        {'created_at': '2011/11/17',
         'key': 'nanami.hashimoto_2011_11_001000',
         'title': 'しらたま ( ´_ゝ｀)',
         'url': 'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/001000.php'},
        {'created_at': '2011/11/16',
         'key': 'nanami.hashimoto_2011_11_000999',
         'title': 'はちみつ生姜湯で風邪予防♪',
         'url': 'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/000999.php'},
        {'created_at': '2011/11/16',
         'key': 'nanami.hashimoto_2011_11_000998',
         'title': '今日地元では雪が積もったみたいです(^^)',
         'url': 'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/000998.php'},
        {'created_at': '2011/11/14',
         'key': 'nanami.hashimoto_2011_11_000997',
         'title': '眠いよーーっ。',
         'url': 'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/000997.php'},
        {'created_at': '2011/11/13',
         'key': 'nanami.hashimoto_2011_11_000996',
         'title': 'お初です。',
         'url': 'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/000996.php'}]


def test_parse_web_archive_urls():
    samples = '''<http://blog.nogizaka46.com:80/nanami.hashimoto/>; rel="original",
<http://web.archive.org/web/timemap/link/http://blog.nogizaka46.com/nanami.hashimoto/>; rel="self"; type="application/link-format"; from="Fri, 24 Feb 2012 10:27:47 GMT",
<http://web.archive.org>; rel="timegate",
<http://web.archive.org/web/20120224102747/http://blog.nogizaka46.com:80/nanami.hashimoto/>; rel="first memento"; datetime="Fri, 24 Feb 2012 10:27:47 GMT",
<http://web.archive.org/web/20120225014230/http://blog.nogizaka46.com:80/nanami.hashimoto>; rel="memento"; datetime="Sat, 25 Feb 2012 01:42:30 GMT",
<http://web.archive.org/web/20120304002750/http://blog.nogizaka46.com:80/nanami.hashimoto>; rel="memento"; datetime="Sun, 04 Mar 2012 00:27:50 GMT",
'''

    for url in parsers.parse_web_archive_urls(samples):
        print(url)
    assert True


def test_parse_blog_image_urls():
    html = requests.get(url='http://blog.nogizaka46.com/manatsu.akimoto/2019/03/049734.php', headers=HEADERS).text
    print(parsers.BlogParser(html)._parse_blog_context_images())
    assert False


def test_parse_blog_context():
    html = requests.get(url='http://blog.nogizaka46.com/manatsu.akimoto/2019/03/049734.php', headers=HEADERS).text
    print(parsers.PostParser(html).blog_context)
    assert False
