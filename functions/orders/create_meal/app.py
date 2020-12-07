import os
import json
import boto3
import datetime
import shortuuid

dynamodb = boto3.resource('dynamodb')
meal_table = dynamodb.Table(os.environ['MEALS_TABLE'])

def lambda_handler(event, context):
    print(event)
    meal = json.loads(event['body'])
    return create_meal(meal)

def create_meal(meal):
    meal_id = shortuuid.uuid()
    now = str(datetime.datetime.now())
    item = {
        'PK': 'MEAL#' + meal_id,
        'SK': '#MEAL#',
        'seatNumber': meal['seatNum'],
        'mealStatus': 'STARTED',
        'startTime': now
    }
    meal_table.put_item(Item=item)

    return {
        'statusCode': 201,
        'body': json.dumps({
            'mealId': meal_id
        }),
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    }
