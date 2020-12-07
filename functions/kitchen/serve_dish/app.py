import boto3
import json
import os
import datetime

eventbridge = boto3.client('events')
event_bus = os.environ['EVENT_BUS']
event_source = 'sushitrain-kitchensvc'


def lambda_handler(event, context):
    order = event['order']
    return serve_dish(order)


def serve_dish(order):
    now = str(datetime.datetime.now())
    order['servedTime'] = now
    eventbridge.put_events(
        Entries=[
            {
                'DetailType': 'sushitrain.item_served',
                'Time': now,
                'Resources': [],
                'Detail': json.dumps(order),
                'Source': event_source,
                'EventBusName': event_bus
            }
        ]
    )
    return order
