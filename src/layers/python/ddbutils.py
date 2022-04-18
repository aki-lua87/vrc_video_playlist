import os
import boto3
import datetime
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['VRC_VIDEO_TABLE'])


# チャンネルが登録済みか確認
def isExistChannelID(channel_id):
    response = table.get_item(
        Key={
            'user_id': 'yt_channnel_id',
            'video_id': channel_id
        }
    )
    isExistRecord = response.get('Item')
    if isExistRecord is None:
        return False, ""
    return True, isExistRecord.get('author')


# チャンネルIDに紐づくリストを取得
def getVideoList(channel_id):
    response = table.get_item(
        Key={
            'user_id': 'list_yt_ch',
            'video_id': f'{channel_id}',
        }
    )
    record = response.get('Item')
    if record is None:
        return None
    return record


# 登録情報更新
def registChannel(channel_id, author):
    table.put_item(
        Item={
            'user_id': 'yt_channnel_id',
            'video_id': channel_id,
            'author': author
        }
    )


# List更新
def registVideoList(channel_id, video_urls, descriptions, index_create):
    now = datetime.datetime.now()
    table.put_item(
        Item={
            'user_id': 'list_yt_ch',
            'video_id': f'{channel_id}',
            'titles': descriptions,
            'urls': video_urls,
            'is_exec_index_create': index_create,
            'latest_update': now.strftime('%Y%m%d%H'),
        }
    )


# List更新ver.api
def registVideoListV2(video_datas, index_create):
    now = datetime.datetime.now()
    table.put_item(
        Item={
            'user_id': 'list_yt_ch',
            'video_id': video_datas['channelId'],
            'titles': video_datas['videos']['titles'],
            'urls': video_datas['videos']['urls'],
            'live': video_datas['live']['url'],
            'is_exec_index_create': index_create,
            'latest_update': now.strftime('%Y%m%d%H'),
        }
    )


# チャンネルIDに紐づくリストを取得
def getTVer(attribute):
    response = table.get_item(
        Key={
            'user_id': 'tver',
            'video_id': f'{attribute}',
        }
    )
    record = response.get('Item')
    if record is None:
        return None
    return record


# attributeから番組名で取得
def getTVer2(attribute, title):
    response = table.query(
        KeyConditionExpression=Key('user_id').eq(
            f'tver_{attribute}') & Key('video_id').begins_with(title)
    )
    record = response.get('Items')
    if record is None:
        return None
    return record
