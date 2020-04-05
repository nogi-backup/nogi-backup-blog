import os
from datetime import datetime
import pytest
from nogi.utils import parsers
from nogi.utils.parsers import BlogParser, PostParser

HTML_STRING = open(os.path.join(os.path.dirname(__file__), 'blog_sample.html'),  'r').read()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}

blog = BlogParser(HTML_STRING)
post = PostParser(HTML_STRING)


def test_generate_post_key():
    sample = 'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/001000.php'
    assert parsers.generate_post_key(sample) == 'nanami.hashimoto_2011_11_001000'


@pytest.mark.skip(reason='Need to update this testcase')
def test_parse_images():
    assert len(post.post_content_images) == 4
    assert post.post_content_images == [
        'https://web.archive.org/web/20120305131600im_/http://blog.nogizaka46.com/photos/uncategorized/2011/11/17/f1010105.jpg',
        'https://web.archive.org/web/20120305131600im_/http://blog.nogizaka46.com/photos/uncategorized/2011/11/17/f1010455.jpg',
        'https://web.archive.org/web/20120305131600im_/http://blog.nogizaka46.com/photos/uncategorized/2011/11/16/f1010464.jpg',
        'https://web.archive.org/web/20120305131600im_/http://blog.nogizaka46.com/photos/uncategorized/2011/11/16/f1010461.jpg']


def test_parse_blog_url():
    assert len(blog.blog_urls) == 5
    assert blog.blog_urls == [
        'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/001000.php',
        'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/000999.php',
        'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/000998.php',
        'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/000997.php',
        'https://web.archive.org/web/20120305131600/http://blog.nogizaka46.com/nanami.hashimoto/2011/11/000996.php']


def test_parse_post_date():
    assert [datetime.strftime(result, '%Y/%m/%d') for result in blog.blog_dates] == [
        '2011/11/17', '2011/11/16', '2011/11/16', '2011/11/14', '2011/11/13']


def test_parse_blog_title():
    assert blog.blog_titles == ['しらたま ( ´_ゝ｀)', 'はちみつ生姜湯で風邪予防♪', '今日地元では雪が積もったみたいです(^^)', '眠いよーーっ。', 'お初です。']


def test_parse_blog_total_page():
    assert parsers.BlogParser(HTML_STRING).blog_next_pages == [
        '?page=1', '?page=2', '?page=3', '?page=4', '?page=5', '?page=all']
