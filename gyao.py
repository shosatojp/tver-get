import sys
import argparse
import requests
import json
import re


query = '''query Playback(
  $videoId: ID!
  $logicaAgent: LogicaAgent!
  $clientSpaceId: String!
  $os: Os!
  $device: Device!
) {
  content(
    parameter: {
      contentId: $videoId
      logicaAgent: $logicaAgent
      clientSpaceId: $clientSpaceId
      os: $os
      device: $device
      view: WEB
    }
  ) {
    tracking {
      streamLog
      vrLog
      stLog
    }
    inStreamAd {
      forcePlayback
      source {
        ... on YjAds {
          __typename
          ads {
            location
            positions
            time
            urlWhenNoAd
          }
          spaceId
        }
        ... on Vmap {
          __typename
          url
        }
        ... on CatchupVmap {
          __typename
          url
          siteId
        }
      }
    }
    video {
      id
      title
      delivery {
        id
        drm
      }
      duration
      images {
        url
        width
        height
      }
      cpId
      playableAge
      maxPixel
      embeddingPermission
      playableAgents
      gyaoUrl
    }
  }
}
'''


def get_brightcove_video_id(gyao_video_id: str):
    variables = {
        "videoId": gyao_video_id,
        "logicaAgent": "PC_WEB",
        "clientSpaceId": "1183082802",
        "os": "UNKNOWN",
        "device": "PC"
    }
    res = requests.get('https://gyao.yahoo.co.jp/apis/playback/graphql', params={
        'appId': 'dj00aiZpPUNJeDh2cU1RazU3UCZzPWNvbnN1bWVyc2VjcmV0Jng9NTk-',
        'query': query,
        'variables': json.dumps(variables),
    }, headers={
        'referer': 'https://gyao.yahoo.co.jp/'
    })
    if res.status_code == 200:
        return res.json()['data']['content']['video']['delivery']['id']
    else:
        print(f'Error: status code is {res.status_code}', file=sys.stderr)
        exit(1)


def get_brightcove_url(gyao_url: str):
    while True:
        m = re.match(r'https://gyao\.yahoo\.co\.jp/episode/(?:[^/]+/)?([\d\w-]+)$', gyao_url)
        if m:
            gyao_id = m[1]
            break

        m = re.match(r'https://gyao.yahoo.co.jp/player/(.+?)/?$', gyao_url)
        if m:
            gyao_id = m[1].replace('/', ':')
            break

        print('not a valid gyao url.', file=sys.stderr)
        exit(1)

    print(f'gyao_id : {gyao_id}')

    html = requests.get(gyao_url).text
    publisher_id = re.search(r'https://players\.brightcove\.net/(\d+)/\w+_default/index\.min\.js', html)[1]
    print(f'publisher_id : {publisher_id}')
    video_id = get_brightcove_video_id(gyao_id)
    print(f'video_id : {video_id}')

    brightcove_url = f'https://players.brightcove.net/{publisher_id}/default_default/index.html?videoId={video_id}'
    return brightcove_url


if __name__ == "__main__":
    parser = argparse.ArgumentParser('gyao brightcove url getter')
    parser.add_argument('url',  type=str)
    args = parser.parse_args()
    print(get_brightcove_url(args.url))
