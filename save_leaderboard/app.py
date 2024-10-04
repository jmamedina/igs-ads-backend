import json
from datetime import datetime

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
        },
        "body": "post leaderboard",
    }
