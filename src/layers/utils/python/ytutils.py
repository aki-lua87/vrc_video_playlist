import urllib.request
import xml.etree.ElementTree as ET
from apiclient.discovery import build
import subprocess
import os


def getRSS(channel_id):
    url = "https://www.youtube.com/feeds/videos.xml?channel_id="+channel_id
    body = getRssFeed(url)
    root = ET.fromstring(body)
    if len(root) == 0:
        return [], False
    return root, True


def getRssFeed(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as res:
        body = res.read().decode('utf-8')
    return body


def scrapingRSS(rssdata):
    descriptions = []
    urls = []
    name = ""
    for child in rssdata:
        if child.tag == '{http://www.w3.org/2005/Atom}author':
            for author in child:
                if author.tag == '{http://www.w3.org/2005/Atom}name':
                    name = child.find('{http://www.w3.org/2005/Atom}name').text
        if child.tag == '{http://www.w3.org/2005/Atom}entry':
            for childchild in child:
                if childchild.tag == '{http://www.w3.org/2005/Atom}title':
                    descriptions.append(child.find(
                        '{http://www.w3.org/2005/Atom}title').text)
                if childchild.tag == '{http://www.w3.org/2005/Atom}link':
                    urls.append(childchild.attrib['href'])
    return name, urls, descriptions


def ytapi_search_channelId(channelId):
    API_KEY = os.environ['API_KEY']
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    YOUTUBE_URL = 'https://www.youtube.com/watch?v='

    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=API_KEY
    )

    search_response = youtube.search().list(
        channelId=channelId,
        part='snippet',
        type='video',
        order='date',
        maxResults=25
    ).execute()

    video_datas = {
        'channelId': channelId,
        'auther': '',
        'live': {
            'title': '',
            'url': ''
        },
        'videos': {
            'titles': [],
            'urls': [],
        }
    }
    titles = []
    urls = []

    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            video_datas['auther'] = search_result["snippet"]["channelTitle"]
            if search_result["snippet"]["liveBroadcastContent"] == "live":
                video_datas['live']['title'] = search_result["snippet"]["title"]
                video_datas['live']['url'] = f'{YOUTUBE_URL}{search_result["id"]["videoId"]}'
            elif search_result["snippet"]["liveBroadcastContent"] == "none":
                title = search_result["snippet"]["title"]
                url = f'{YOUTUBE_URL}{search_result["id"]["videoId"]}'
                titles.append(title)
                urls.append(url)
    video_datas['videos']['titles'] = titles
    video_datas['videos']['urls'] = urls
    return video_datas


def ytapi_search_query(query):
    API_KEY = os.environ['API_KEY']
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    YOUTUBE_URL = 'https://www.youtube.com/watch?v='

    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=API_KEY
    )

    search_response = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        order='date',
        maxResults=20
    ).execute()

    video_datas = {
        'query': query,
        'videos': {
            'authers': [],
            'titles': [],
            'urls': [],
        }
    }
    for search_result in search_response.get("items", []):
        if search_result["snippet"]["liveBroadcastContent"] == "none":
            title = search_result["snippet"]["title"]
            url = f'{YOUTUBE_URL}{search_result["id"]["videoId"]}'
            auther = search_result["snippet"]["channelTitle"]
            video_datas['videos']['titles'].append(title)
            video_datas['videos']['urls'].append(url)
            video_datas['videos']['authers'].append(auther)
    return video_datas


def ytapi_search_channelId_ALL(channelId, n=19):
    # 再起させても MAX 500 らしい・・・
    API_KEY = os.environ['API_KEY']
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    YOUTUBE_URL = 'https://www.youtube.com/watch?v='

    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=API_KEY
    )

    nextPagetoken = None
    video_datas = {
        'auther': '',
        'videos': []
    }
    count = 0
    isOverN = False
    for num in range(20):
        search_response = youtube.search().list(
            channelId=channelId,
            part='snippet',
            type='video',
            order='date',
            maxResults=50,
            pageToken=nextPagetoken
        ).execute()

        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                video_datas['auther'] = search_result["snippet"]["channelTitle"]
                if search_result["snippet"]["liveBroadcastContent"] == "none":
                    title = search_result["snippet"]["title"]
                    url = f'{YOUTUBE_URL}{search_result["id"]["videoId"]}'
                    video_data = {
                        'title': title,
                        'url': url
                    }
                    video_datas['videos'].append(video_data)
                    count = count+1
                    if count > n:
                        isOverN = True
                        break
        if isOverN:
            break
        try:
            nextPagetoken = search_response["nextPageToken"]
        except Exception as e:
            print('[WARN]', e)
            break
    print(len(video_datas['videos']))
    return video_datas


def exec_ytdlp_cmd(url):
    # yt-dlp -i -q --no-warnings --no-playlist -g https://www.youtube.com/watch?v=xxxxxxxx
    cp = subprocess.run(
        ["/var/task/addon/yt-dlp", '-i', '-q', '--no-warnings', '--no-playlist', '-f', 'b', '-g', url], capture_output=True)
    # print("stdout:", cp.stdout)
    return cp.stdout
