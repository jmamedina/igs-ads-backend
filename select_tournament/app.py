import sys
import pymysql # type: ignore
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

db_user = os.environ.get('DB_USER', 'default_user')
db_password = os.environ.get('DB_PASSWORD', 'default_password')

#create the database connection outside of the lambda handler
def get_db_connection(db_name, db_host):
    try:
        conn = pymysql.connect(host=db_host, user=db_user, passwd=db_password, db=db_name, connect_timeout=10)
        logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
        return conn
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()

def query_database(conn, sql_query):
    try:
        with conn.cursor() as cur:
            cur.execute(sql_query)
            result = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]  # Get column names
            return result, column_names
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not query database.")
        logger.error(e)
        return None

def convert_datetime_to_string(data):
    if isinstance(data, tuple):
        return tuple(convert_datetime_to_string(item) for item in data)
    elif isinstance(data, list):
        return [convert_datetime_to_string(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_datetime_to_string(value) for key, value in data.items()}
    elif isinstance(data, datetime):
        return data.isoformat() 
    else:
        return data

def lambda_handler(event, context):
    query_params = event.get('queryStringParameters', {})
    
    if not query_params or 'db_name' not in query_params:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "db_name parameter is required"})
        }
        
    if 'db_host' not in query_params:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "db_host parameter is required"})
        }
        
    db_name = query_params['db_name']
    db_host = query_params['db_host']

    conn = get_db_connection(db_name, db_host)
    if not conn:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to connect to the database."})
        }

    print("db_name" + db_name)
    print("db_name" + db_host)

    try:
        today = datetime.now().strftime("%Y-%m-%d")
        start_of_day = today + " 00:00:00"
        end_of_day = today + " 23:59:59"

        sql_query = f"SELECT id, name, link_tournament_id, group_count, use_yesterday_score FROM tournament WHERE start_date >= '{start_of_day}' AND start_date <= '{end_of_day}'"
        query_results , column_names= query_database(conn, sql_query)

        if query_results is not None:
            results_as_dicts = [dict(zip(column_names, row)) for row in query_results]
            results_convert = convert_datetime_to_string(results_as_dicts)
            results_json = json.dumps(results_convert, ensure_ascii=False) # Convert results to JSON
            results_json = json.loads(results_json)
        else:
            results_json = "Error: Could not query database."
        
        return {
            "statusCode": 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
            },
            "body": json.dumps({
                "tournament_list": results_json
            }),
        }
    except Exception as e:
        logger.error("ERROR: Unexpected error: Could not query database.")
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to query the database."})
        }
    finally:
        conn.close()
