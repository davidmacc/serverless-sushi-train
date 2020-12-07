import os
import boto3

dynamodb = boto3.resource('dynamodb')
websockets_table = dynamodb.Table(os.environ['WEBSOCKETS_TABLE'])


def lambda_handler(event, context):
    print(event)
    meal_id = event['queryStringParameters']['mealId']
    connection_id = event['requestContext']['connectionId']
    return record_ws_connection(meal_id, connection_id)

def record_ws_connection(meal_id, connection_id):
    websockets_table.put_item(
        Item={
            'mealId': meal_id,
            'wsConnectionId': connection_id
        })

    return {
        'statusCode': 200,
        'body': ''
    }
