import os
import json
import boto3

client = boto3.client('stepfunctions')
state_machine_ARN = os.environ['STATE_MACHINE_ARN']


def lambda_handler(event, context):
    print(event)
    return process_orders(event['Records'])


def process_orders(order_messages):
    for order_message in order_messages:
        msg_id = order_message['messageId']
        order = json.loads(order_message['body'])
        execution = client.start_execution(
            stateMachineArn=state_machine_ARN,
            name=msg_id,
            input=json.dumps({'order': order})
        )
