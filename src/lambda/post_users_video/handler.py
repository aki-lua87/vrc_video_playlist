import os
import time
import urllib.request
import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table(os.environ['VRC_VIDEO_TABLE'])
my_url   = os.environ['MY_URL']

def main(event, context):
    user_id = event['pathParameters'].get('user_id')
    body = json.loads(event['body'])
    video_id = body.get('video_id')
    video_url = body.get('video_url')
    video_description = body.get('description')
    # 引数チェック
    if user_id == None or video_id == None or video_url == None:
        return {
            'headers': { 
                    "Access-Control-Allow-Origin": "*"
                },
            'statusCode': 400,
            'body': json.dumps(
                {
                    'error': 'bad request'
                }
            )
        }
    # ユーザチェック
    isExist = isUserExist(user_id)
    if not isExist:
        return {
            'headers': { 
                    "Access-Control-Allow-Origin": "*"
                },
            'statusCode': 400,
            'body': json.dumps(
                {
                    'error': 'user not exist'
                }
            )
        }
    # videoのチェック
    isExist = isVideoExist(user_id, video_id)
    if not isExist:
        return {
            'headers': { 
                    "Access-Control-Allow-Origin": "*"
                },
            'statusCode': 400,
            'body': json.dumps(
                {
                    'error': 'user not exist'
                }
            )
        }
    # video登録
    registVideo(user_id,video_id,video_url,video_description)
    return {
        'headers': { 
                "Access-Control-Allow-Origin": "*"
            },
        'statusCode': 200,
        'body': json.dumps(
            {
                'url': f'{my_url}/users/{user_id}/video?video_id={video_id}'
            }
        )
    }


def createVideoID():
    return str(uuid.uuid4())

def registVideo(user_id,video_id,video_url,video_description):
    table.put_item(
        Item={
            'user_id': user_id,
            'video_id': video_id,
            'url':video_url,
            'description':video_description
        }
    )

def isUserExist(user_id):
    response = table.get_item(
        Key={
            'user_id': 'user',
            'video_id': user_id
        }
    )
    isExistRecord = response.get('Item')
    if isExistRecord == None:
        return False
    return True

def isVideoExist(user_id, video_id):
    response = table.get_item(
        Key={
            'user_id': user_id,
            'video_id': video_id
        }
    )
    isExistRecord = response.get('Item')
    if isExistRecord == None:
        return False
    return True