import os
import json
import boto3
import datetime
import shortuuid

dynamodb = boto3.resource('dynamodb')
meal_table = dynamodb.Table(os.environ['MEALS_TABLE'])

def lambda_handler(event, context):
    print(event)
    meal_id = event['pathParameters']['mealId']
    ordered_item = json.loads(event['body'])
    return order_item(meal_id, ordered_item)


def order_item(meal_id, ordered_item):
    item_id = shortuuid.uuid()
    now = str(datetime.datetime.now())

    item = {
        'PK': 'MEAL#' + meal_id,
        'SK': 'ITEM#' + item_id,
        'itemName': ordered_item['item'],
        'itemQty': ordered_item['qty'],
        'orderedTime': now
    }

    meal_table.put_item(Item=item)

    return {
        'statusCode': 201,
        'body': json.dumps({
            'itemId': item_id,
            'orderedTime': item['orderedTime']
        }),
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    }
