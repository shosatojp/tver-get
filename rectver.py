import sys
import time
import re
import requests


def parse_video_entry(e):
    link = 'https://tver.jp' + e.select_one('a')['href']
    progtitle = e.select_one('.progtitle')
    title = progtitle.select_one('h3').text
    episode = progtitle.select_one('.summary').text
    info = progtitle.select_one('.tv').text
    vid = re.match('.*/(.*?)$', link)[1]
    return {
        'link': link,
        'title': title,
        'episode': episode,
        'info': info,
        'vid': vid,
    }


def get_access_token():
    url = f'https://tver.jp/api/access_token.php?_t={int(time.time()*1000)}'
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()['token']


def search(query: str, token: str):
    url = f'https://api.tver.jp/v4/search'
    res = requests.get(url, params={
        'keyword': query,
        'catchup': 1,
        'token': token,
    })
    if res.status_code == 200:
        return res.json()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', '-q', required=True, type=str)
    args = parser.parse_args()

    access_token = get_access_token()
    if not access_token:
        sys.stderr.write('Error: failed to obtain access token.\n')
        exit(1)
    result = search(args.query, access_token)

    for prog in result['data']:
        rid = prog["reference_id"]
        brightcove_url = f'https://players.brightcove.net/{prog["publisher_id"]}/default_default/index.html?videoId=ref:{rid}'
        print(brightcove_url)
