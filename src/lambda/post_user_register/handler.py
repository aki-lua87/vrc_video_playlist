import os
import time
import urllib.request
import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table(os.environ['VRC_VIDEO_TABLE'])

def main(event, context):
    user_id = createUserID()
    registerUser(user_id)
    return {
        'headers': { 
                "Access-Control-Allow-Origin": "*"
            },
        'statusCode': 200,
        'body': json.dumps(
            {
                'user_id': user_id
            }
        )
    }

def createUserID():
    return str(uuid.uuid4())

def registerUser(user_id):
    table.put_item(
        Item={
            "user_id": user_id,
            "video_id": 'user'
        }
    )