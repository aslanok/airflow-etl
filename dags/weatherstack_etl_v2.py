from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import time
import requests
from dag_utils.config_loader import load_config
from dag_plugins.postgre_module import PostgresClient
config = load_config()

WEATHERSTACK_ACCESS_KEY = config['weatherstack']['access_key']
CITIES = config['weatherstack']['cities']
HOST = config['postgres']['host']
DBNAME = config['postgres']['dbname']
USERNAME = config['postgres']['username']
PASSWORD = config['postgres']['password']
weather_create_query = config['postgres']['weather_create_query']
weather_insert_query = config['postgres']['weather_insert_query']

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 4),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='weatherstack_etl_v2',
    default_args=default_args,
    schedule='@daily',  # ✅ new argument name
    catchup=False,
    description='Efficient ETL from Weatherstack API to Postgres',
) as dag:


    @task
    def extract_weather():
        base_url = "http://api.weatherstack.com/current"
        all_data = []

        for city in CITIES:
            params = {
                'access_key': WEATHERSTACK_ACCESS_KEY,
                'query': city.get('lat_long', city['name']),
                'units': 'm'
            }
            response = requests.get(base_url, params=params)
            data = response.json()
            if data.get("success") is False:
                print(f"API error for {city['name']}: {data['error'].get('info')}")
                continue

            if "location" not in data or "current" not in data:
                print(f"Invalid response for {city['name']}: {data}")
                continue

            location = data['location']
            current = data['current']

            # Parse localtime to epoch
            localtime_str = location.get('localtime')
            localtime_dt = date_parser.parse(localtime_str)
            localtime_epoch = int(time.mktime(localtime_dt.timetuple()))

            row = {
                'name': location.get('name'),
                'region': location.get('region'),
                'country': location.get('country'),
                'lat': float(location.get('lat')),
                'long': float(location.get('lon')),
                'timezone': location.get('timezone_id'),
                'local_time': localtime_dt,
                'temp_c': current.get('temperature'),
                'feelslike_c': current.get('feelslike'),
                'condition': current.get('weather_descriptions', [None])[0],
                'condition_icon': current.get('weather_icons', [None])[0],
                'wind_kph': current.get('wind_speed'),
                'pressure_mb': current.get('pressure'),
                'precipitation_mm': current.get('precip'),
                'humidity': current.get('humidity'),
                'cloud': current.get('cloudcover'),
                'uv_index': current.get('uv_index'),
                'visibility_km': current.get('visibility'),
                'last_updated_epoch': localtime_epoch
            }

            all_data.append(row)

        return all_data

    @task
    def load_weather_to_postgres(weather_records: list):
        """Create table if not exists and bulk insert records."""
        if not weather_records:
            print("No data to insert.")
            return

        client = PostgresClient(HOST, DBNAME, USERNAME, PASSWORD)
        client.execute_query(weather_create_query)
        columns = [
            'name', 'region', 'country', 'lat', 'long', 'timezone', 'local_time',
            'temp_c', 'feelslike_c', 'condition', 'condition_icon', 'wind_kph',
            'pressure_mb', 'precipitation_mm', 'humidity', 'cloud',
            'uv_index', 'visibility_km', 'last_updated_epoch'
        ]
        # Convert list of dicts to list of tuples for insertion
        rows = [tuple(record[col] for col in columns) for record in weather_records]
        try:
            client.cur.executemany(weather_insert_query, rows)
            client.conn.commit()
            print(f"Inserted {len(rows)} rows into 'weather'")
        except Exception as e:
            client.conn.rollback()
            print("Bulk insert failed:", e)
        finally:
            client.connection_close()

    # Set up task dependencies
    weather_data = extract_weather()
    load_weather_to_postgres(weather_data)
