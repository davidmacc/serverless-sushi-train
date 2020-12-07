import boto3
import json
import os
from boto3.dynamodb.conditions import Key, Attr

event_bus_name = os.environ['EVENT_BUS']
eventbridge = boto3.client('events')
dynamodb = boto3.resource('dynamodb')
meals_table = dynamodb.Table(os.environ['MEALS_TABLE'])
event_source = 'sushitrain-orderingsvc'


def lambda_handler(event, context):
    print(event)
    return process_records(event['Records'])


def process_records(records):
    for record in records:
        if (record['eventName'] == 'INSERT'):
            item = record['dynamodb']['NewImage']
            sortKey = item['SK']['S']
            if (sortKey == '#MEAL#'):
                event_meal_started(item)
            elif (sortKey.startswith('ITEM#')):
                event_item_ordered(item)
        elif (record['eventName'] == 'MODIFY'):
            item = record['dynamodb']['NewImage']
            sortKey = item['SK']['S']
            if (sortKey == '#MEAL#' and item['mealStatus']['S'] == 'FINISHED'):
                event_meal_finished(item)


def event_meal_started(item):
    event = {
        'DetailType': 'sushitrain.meal_started',
        'Time': item['startTime']['S'],
        'Resources': [],
        'Detail': json.dumps({
            'mealId': item['PK']['S'].split("MEAL#", 1)[1],
            # 'customerId': item['customerId']['S'],
            'seatNumber': item['seatNumber']['S'],
            'startTime': item['startTime']['S']
        }),
        'Source': event_source,
        'EventBusName': event_bus_name
    }
    eventbridge.put_events(Entries=[event])


def event_item_ordered(item):
    partition_key = item['PK']['S']
    meal_item = meals_table.get_item(
        Key={'PK': partition_key, 'SK': '#MEAL#'}, AttributesToGet=['seatNumber'])['Item']
    event = {
        'DetailType': 'sushitrain.item_ordered',
        'Time': item['orderedTime']['S'],
        'Resources': [],
        'Detail': json.dumps({
            'mealId': item['PK']['S'].split("MEAL#", 1)[1],
            'itemId': item['SK']['S'].split("ITEM#", 1)[1],
            'itemName': item['itemName']['S'],
            'itemQty': item['itemQty']['N'],
            'seatNumber': meal_item['seatNumber'],
            'orderedTime': item['orderedTime']['S']
        }),
        'Source': event_source,
        'EventBusName': event_bus_name
    }
    eventbridge.put_events(Entries=[event])


def event_meal_finished(item):
    # Get served menu items for this meal and inject into event
    meal_items = meals_table.query(
        KeyConditionExpression=Key('PK').eq(
            item['PK']['S']) & Key('SK').begins_with('ITEM#'),
        FilterExpression=Attr('servedTime').exists()
    )
    items = []
    for mi in meal_items['Items']:
        items.append({
            'itemId': mi['SK'].split("ITEM#", 1)[1],
            'itemName': mi['itemName'],
            'itemQty': int(mi['itemQty']),
            'orderedTime': mi['orderedTime'],
            'servedTime': mi['servedTime']
        })
    event = {
        'DetailType': 'sushitrain.meal_finished',
        'Time': item['endTime']['S'],
        'Resources': [],
        'Detail': json.dumps({
            'mealId': item['PK']['S'].split("MEAL#", 1)[1],
            # 'customerId': item['customerId']['S'],
            'seatNumber': item['seatNumber']['S'],
            'startTime': item['startTime']['S'],
            'endTime': item['endTime']['S'],
            'mealItems': items
        }),
        'Source': event_source,
        'EventBusName': event_bus_name
    }
    eventbridge.put_events(Entries=[event])
