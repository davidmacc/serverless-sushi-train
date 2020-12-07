import boto3
import json
import os
from boto3.dynamodb.conditions import Key, Attr
from dynamodb_json import json_util as ddb_json

event_bus_name = os.environ['EVENT_BUS']
eventbridge = boto3.client('events')
event_source = 'sushitrain-billingsvc'


def lambda_handler(event, context):
    print(event)
    return process_records(event['Records'])


def process_records(records):
    for record in records:
        if (record['eventName'] == 'INSERT'):
            item = record['dynamodb']['NewImage']
            event_meal_billed(item)


def event_meal_billed(item):
    event = {
        'DetailType': 'sushitrain.meal_billed',
        'Time': item['paymentProcessTime']['S'],
        'Resources': [],
        'Detail': json.dumps(ddb_json.loads(json.dumps(item))),
        'Source': event_source,
        'EventBusName': event_bus_name
    }
    eventbridge.put_events(Entries=[event])
