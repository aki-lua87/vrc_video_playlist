import os
import urllib.request
import json
import boto3
import datetime

import ddbutils
import ytutils

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['VRC_VIDEO_TABLE'])


def main(event, context):
    print('event:', event)
    channel_id = event['pathParameters'].get('channel_id')
    channel_id = channel_id.strip()
    queryStringParameters = event.get('queryStringParameters')
    httpMethod = event.get('httpMethod')
    print('channel_id:', channel_id)
    print('httpMethod:', httpMethod)
    if channel_id is None or queryStringParameters is None:
        return {
            'headers': {
                "Access-Control-Allow-Origin": "*"
            },
            'statusCode': 400,
            'body': json.dumps(
                {
                    'result': 'NG',
                    'error': 'bad request [1]'
                }
            )
        }
    before = queryStringParameters.get('n', 0)
    b_int = int(before)
    url = getVideoURL(channel_id, b_int)
    if httpMethod == 'HEAD':
        print('HEAD Return')
        return {
            'headers': {
                "Content-type": "text/html; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "location": url
            },
            'statusCode': 302,
            'body': "",
        }
    # TODO: Questはこれでいけるだろうか
    body = getVideoPage(url)
    return {
        'headers': {
            "Content-type": "text/html; charset=utf-8",
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 200,
        'body': body,
    }


def getVideoURL(channel_id, n):
    # Videoのlistを取得
    v_list = ddbutils.getVideoList(channel_id)
    # 更新有無の確認
    latestDateStr = v_list.get('latest_update', 'NoData')
    print('latestDateStr:', latestDateStr)
    now = datetime.datetime.now()
    nowstr = now.strftime('%Y%m%d%H')
    if (latestDateStr != nowstr):
        # 更新
        print('update')
        try:
            data = ytutils.ytapi_search_channelId(channel_id)
            ddbutils.registVideoListV2(data, True)
            urls = data['videos']['urls']
            titles = data['videos']['titles']
        except Exception as e:
            print('[WARN]', e)
            urls = v_list['urls']
            titles = v_list['titles']
    else:
        urls = v_list['urls']
        titles = v_list['titles']
    print(urls[n], titles[n])
    return urls[n]


def getVideoPage(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as res:
        body = res.read().decode('utf-8')
    return body
