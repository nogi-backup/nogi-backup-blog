from datetime import datetime
import re
from typing import Generator, List

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

PATTERN = r'^\<(?P<url>.*)\>; rel\=\"(?P<archive_type>.*)\"; (.*)$'


def parse_web_archive_urls(response: str) -> list:
    results = set()
    for record in response.split('\n'):
        if re.search(PATTERN, record):
            result = re.search(PATTERN, record).groupdict()
            if 'memento' in result['archive_type']:
                results.add(result['url'])
    return sorted(results)


def parse_official_archive_urls(response: str) -> list:
    return [item['value'] for item in BeautifulSoup(response, 'lxml').find_all('option') if item['value']]


def generate_post_key(post_url: str) -> str:
    return '_'.join(post_url.split('/')[-4:]).replace('.php', '')


class BlogParser:

    def __init__(self, html: str) -> None:
        self._parser = BeautifulSoup(html, 'lxml')
        self._images = list()

    @property
    def profile_images(self) -> list:
        return [item['src'] for item in self._parser.find_all('img', class_='image-embed')]

    @property
    def archive_blogs(self) -> list:
        return [item['value'] for item in self._parser.find_all('option') if item['value']]

    @property
    def blog_urls(self) -> list:
        return [item['href'] for item in self._parser.find_all('a', rel='bookmark')]

    @property
    def blog_titles(self) -> list:
        return [item.text for item in self._parser.find_all('a', rel='bookmark')]

    @property
    def blog_dates(self) -> Generator[datetime, None, None]:
        days = self._parser.find_all('span', attrs={'class': 'dd1'})
        for index, yearmonth in enumerate(self._parser.find_all('span', attrs={'class': 'yearmonth'})):
            yield datetime(
                year=int(yearmonth.string.split('/')[0]),
                month=int(yearmonth.string.split('/')[1]),
                day=int(days[index].string))

    @property
    def blog_next_pages(self) -> list:
        results = set()
        for item in self._parser.select('div.paginate a[href]'):
            if 'index.php' in item['href']:
                results.add(item['href'].replace('index.php', ''))
            else:
                results.add(item['href'])
        return sorted(results)

    def get_page_blog_abstract(self):
        urls = self.blog_urls
        dates = self.blog_dates
        titles = self.blog_titles
        results = []
        for index, date in enumerate(dates):
            results.append(dict(
                key=generate_post_key(urls[index]), title=titles[index], created_at=int(date.timestamp()), url=urls[index])
            )
        return sorted(results, key=lambda x: x['created_at'], reverse=True)


class PostParser:

    def __init__(self, html: str) -> None:
        self._parser = BeautifulSoup(html, 'lxml')

    @property
    def post_title(self) -> str:
        for item in self._parser.select('span.entrytitle'):
            return item.text

    @property
    def post_content(self) -> str:
        contents = []
        for html_tags in self._parser.select('div.entrybody'):
            for tag in html_tags:
                if isinstance(tag, Tag):
                    line = tag.decode_contents() \
                        .replace(u'\xa0', u'\n') \
                        .replace(u'\u3000', '') \
                        .replace('<br/>', '\n')
                    contents.append(line)
                if isinstance(tag, NavigableString):
                    contents.append(tag)
        return ''.join(contents)

    @property
    def post_content_images(self) -> List[dict]:
        blog_image_urls = [item['src'] for item in self._parser.select('div.entrybody img[src]')]
        print(blog_image_urls)
        results = list()
        for index, item in enumerate(self._parser.select('div.entrybody a[href]')):
            print(index, item)
            url = item['href'] if 'http://dcimg.awalker.jp/' in item['href'] else ''
            results.append(
                dict(
                    image_url=blog_image_urls[index],
                    high_resolution_url=url if url else blog_image_urls[index]
                )
            )
        print(results)
        return results

    @property
    def post_content_images_link(self) -> list:
        return

    @property
    def post_created_at(self) -> str:
        day = self._parser.select('span.dd1')[0].text
        year, month = self._parser.select('span.yearmonth')[0].text.split('/')
        return datetime(year=int(year), month=int(month), day=int(day))

    def to_dict(self) -> dict:
        return dict(
            title=self.post_title,
            content=self.post_content,
            image_urls=self.post_content_images,
            created_at=self.post_created_at)

    @staticmethod
    def blog_format_1(html_tags: Tag) -> list:
        results = []
        for tag in html_tags:
            if isinstance(tag, Tag):
                line = tag.decode_contents() \
                    .replace(u'\xa0', u'\n') \
                    .replace(u'\u3000', '') \
                    .replace('<br/>', '\n')
                results.append(line)
            if isinstance(tag, NavigableString):
                results.append(tag)
        return results
