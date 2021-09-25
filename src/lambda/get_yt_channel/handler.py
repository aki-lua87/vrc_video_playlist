import os
import time
import urllib.request
import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table(os.environ['VRC_VIDEO_TABLE'])

def main(event, context):
    channel_id = event['pathParameters'].get('channel_id')
    queryStringParameters = event.get('queryStringParameters')
    httpMethod = event.get('httpMethod')
    if channel_id == None or queryStringParameters == None:
        return {
            'headers': { 
                    "Access-Control-Allow-Origin": "*"
                },
            'statusCode': 400,
            'body': json.dumps(
                {
                    'result':'NG',
                    'error': 'bad request [1]'
                }
            )
        }
    before = queryStringParameters.get('n')
    urls = getVideoURLList(channel_id)
    b_int = int(before)
    if b_int >= len(urls):
        return {
            'headers': { 
                    "Access-Control-Allow-Origin": "*"
                },
            'statusCode': 400,
            'body': json.dumps(
                {
                    'result':'NG',
                    'error': 'bad request [2]'
                }
            )
        }
    print(urls[b_int])
    if httpMethod == 'HEAD':
        print('HEAD Return')
        return {
            'headers': { 
                    "Content-type": "text/html; charset=utf-8",
                    "Access-Control-Allow-Origin": "*",
                    "location": urls[b_int]['urls']
                },
            'statusCode': 302,
            'body': "",
        }
    body = getVideoPage(urls[b_int]['urls'])
    return {
        'headers': { 
                "Content-type": "text/html; charset=utf-8",
                "Access-Control-Allow-Origin": "*"
            },
        'statusCode': 200,
        'body': body,
    }


def getVideoURLList(channel_id):
    # Videoのlistを取得
    v_list = GetVideoList(channel_id)
    if v_list == None:
        return None
    res = []
    for i in range(len(v_list['urls'])):
        res.append({'urls': v_list['urls'][i],
                   'titles': v_list['titles'][i]})
    return res

def GetVideoList(channel_id):
    response = table.get_item(
        Key={
            'user_id': 'list_yt_ch',
            'video_id': f'{channel_id}',
        }
    )
    record = response.get('Item')
    if record == None:
        return None
    return record

# youtubeの内容をそのまま返す(for quest?)
def getVideoPage(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as res:
        body = res.read().decode('utf-8')
    return body