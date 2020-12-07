import os
import random

min_time_sec = int(os.environ['MIN_PREP_TIME_SEC'])
max_time_sec = int(os.environ['MAX_PREP_TIME_SEC'])

def lambda_handler(event, context):
    return random.randint(min_time_sec, max_time_sec)