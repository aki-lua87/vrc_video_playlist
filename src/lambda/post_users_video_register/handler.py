import os
import time
import urllib.request
import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table(os.environ['VRC_VIDEO_TABLE'])

def main(event, context):
    user_id = event['pathParameters'].get('user_id')
    body = json.loads(event['body'])
    video_url = body.get('video_url')
    video_discprition = body.get('discprition')
    # 引数チェック
    if user_id == None or video_url == None:
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
    # video用のID生成＆登録
    video_id = createVideoID()
    registVideo(user_id,video_id,video_url,video_discprition)
    return {
        'headers': { 
                "Access-Control-Allow-Origin": "*"
            },
        'statusCode': 200,
        'body': json.dumps(
            {
                'video_id': video_id,
                'create_url': f'(未実装)https//:{user_id}/{video_id}'
            }
        )
    }


def createVideoID():
    return str(uuid.uuid4())

def registVideo(user_id,video_id,video_url,video_discprition):
    table.put_item(
        Item={
            'user_id': user_id,
            'video_id': video_id,
            'url':video_url,
            'discprition':video_discprition
        }
    )

def isUserExist(user_id):
    response = table.get_item(
        Key={
            'user_id': user_id,
            'video_id': 'user'
        }
    )
    isExistRecord = response.get('Item')
    if isExistRecord == None:
        return False
    return True
