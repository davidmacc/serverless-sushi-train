import os
import json
import boto3
import datetime

dynamodb = boto3.resource('dynamodb')
billing_table = dynamodb.Table(os.environ['BILLING_TABLE'])
order_free_threshold_sec = int(os.environ['ORDER_FREE_THRESHOLD_SEC'])

def lambda_handler(event, context):
    print(event)
    return bill_meals(event['Records'])


def bill_meals(mealfinished_messages):
    for message in mealfinished_messages:
        meal = json.loads(message['body'])
        meal_id = meal['mealId']
        total_price = 0

        for item in meal['mealItems']:
            qty = item['itemQty']
            orderTime = datetime.datetime.fromisoformat(item['orderedTime'])
            servedTime = datetime.datetime.fromisoformat(item['servedTime'])
            served_late = (servedTime - orderTime).total_seconds() > order_free_threshold_sec
            price = 0 if served_late else qty * 1
            item['price'] = price
            item['priceReasonCode'] = 'SERVED_LATE' if served_late else 'SERVED_ON_TIME'
            total_price += price

        meal['totalPrice'] = total_price
        now = str(datetime.datetime.now())

        billed_meal = {
            'mealId': meal_id,
            'paymentProcessTime': now,
            'totalPayment': total_price,
            'mealDetails': meal
        }

        billing_table.put_item(Item=billed_meal)