import os
import json
import boto3

dynamodb = boto3.resource('dynamodb')
meals_table = dynamodb.Table(os.environ['MEALS_TABLE'])


def lambda_handler(event, context):
    print(event)
    return record_items_served(event['Records'])


def record_items_served(item_messages):
    for item_message in item_messages:
        item = json.loads(item_message['body'])
        print(item)
        key = {'PK': 'MEAL#' + item['mealId'],
               'SK': 'ITEM#' + item['itemId']}
        meals_table.update_item(
            Key=key, UpdateExpression="set servedTime = :s",
            ExpressionAttributeValues={':s': item['servedTime'], })
