from datetime import datetime

import requests

HEADER = {'Content-Type': "application/json", 'cache-control': "no-cache"}

# Slack


def send_slack_notification(url: str, channel_name: str, member: str, post: dict):
    requests.post(
        url=url, headers=HEADER,
        json=render_slack_message(channel_name=channel_name, member=member, post=post)
    )


def render_slack_message(channel_name: str, member: dict, post: dict) -> dict:
    first_name, last_name = member['roma_name'].split('.')
    return dict(
        channel=channel_name,
        blocks=[
            dict(
                type='section',
                text=dict(
                    type='mrkdwn',
                    text='New Blog Discover: *<{url}|{title}>*'.format_map(post))),
            dict(
                type='section',
                fields=[
                     dict(type='mrkdwn', text='*Title:*\n{title}'.format_map(post)),
                     dict(type='mrkdwn', text='*Member:*\n{}'.format(member['kanji_name'])),
                     dict(
                         type='mrkdwn', text='*Created At:*\n{}'.format(datetime.utcfromtimestamp(post['blog_created_at']).strftime('%Y-%m-%d'))),
                     dict(type='mrkdwn', text='*Url:*\n<{url}>'.format_map(post))
                ],
                accessory=dict(
                    type='image',
                    image_url='https://img.nogizaka46.com/blog/pic/{}{}_list.jpg'.format(last_name, first_name),
                    alt_text='palm tree'))
        ])

# Telegram


def send_telegram_notification(token: str, channel_name: str, member: dict, post: dict):
    requests.post(
        url='https://api.telegram.org/bot{}/sendMessage'.format(token),
        header=HEADER,
        json=dict(
            chat_id="@{}".format(channel_name),
            text=render_telegram_message(member=member, post=post),
            disable_web_page_preview=False,
            parse_mode='markdown',
        )
    )


def render_telegram_message(member: dict, post: dict) -> dict:
    return '''
    {title}
    
    Member: {member}
    Created At: {created_at}
    Url: {url}
    '''.format(
        title=post['title'],
        member=member['kanji_name'],
        created_at=datetime.utcfromtimestamp(post['blog_created_at']).strftime('%Y-%m-%d'),
        url=post['url']
    )
