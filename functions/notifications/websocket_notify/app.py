import os
import json
import boto3
import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from urllib.parse import urlparse

dynamodb = boto3.resource('dynamodb')
websockets_table = dynamodb.Table(os.environ['WEBSOCKETS_TABLE'])
ws_connection_url = os.environ['WS_CONNECTION_URL']
ws_connection_hostname = urlparse(ws_connection_url).hostname
auth = BotoAWSRequestsAuth(aws_host=ws_connection_hostname,
                           aws_region='ap-southeast-2', aws_service='execute-api')


def lambda_handler(event, context):
    print(event)
    send_notification(event)


def send_notification(event):
    # get meal_id from event and lookup WS connection
    meal_id = event['detail']['mealId']
    connection_id = websockets_table.get_item(Key={'mealId': meal_id})[
        'Item']['wsConnectionId']
    ws_event = {
        'eventType': event['detail-type'],
        'eventDetail': event['detail']
    }
    requests.post(ws_connection_url + connection_id, json=ws_event, auth=auth)
