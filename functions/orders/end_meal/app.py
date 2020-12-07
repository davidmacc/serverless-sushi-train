import os
import boto3
import datetime

dynamodb = boto3.resource('dynamodb')
meals_table = dynamodb.Table(os.environ['MEALS_TABLE'])


def lambda_handler(event, context):
    print(event)
    meal_id = event['pathParameters']['mealId']
    return end_meal(meal_id)


def end_meal(meal_id):
    key = {'PK': 'MEAL#' + meal_id, 'SK': '#MEAL#'}
    now = str(datetime.datetime.now())
    meals_table.update_item(
        Key=key, UpdateExpression="set endTime = :t, mealStatus = :s", 
        ExpressionAttributeValues={':t': now, ':s': 'FINISHED'})

    return {
        'statusCode': 200,
        'body': '',
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    }
