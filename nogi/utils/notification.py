from datetime import datetime


def render_slack_message(title: str, member: dict, blog_created_at: datetime, url: str, channel_name: str) -> dict:
    first_name, last_name = member['roma_name'].split('.')
    return dict(
        channel=channel_name,
        blocks=[
            dict(
                type='section',
                text=dict(
                    type='mrkdwn',
                    text='New Blog Discover: *<{url}|{title}>*'.format(url=url, title=title))),
            dict(
                type='section',
                fields=[
                     dict(type='mrkdwn', text='*Title:*\n{}'.format(title)),
                     dict(type='mrkdwn', text='*Member:*\n{}'.format(member['kanji_name'])),
                     dict(type='mrkdwn', text='*Created At:*\n{}'.format(datetime.utcfromtimestamp(blog_created_at).strftime('%Y-%m-%d'))),
                     dict(type='mrkdwn', text='*Url:*\n<{}>'.format(url))
                ],
                accessory=dict(
                    type='image',
                    image_url='https://img.nogizaka46.com/blog/pic/{}{}_list.jpg'.format(last_name, first_name),
                    alt_text='palm tree'))
        ])
