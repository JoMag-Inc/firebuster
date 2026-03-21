import pandas as pd
import requests
import json
from app.services.weather import weather_static

headers = weather_static.met_required_headers
url = weather_static.met_base_url
params = weather_static.met_example_coordinates

#raw data from met
def get_weather_data():
    response = requests.get(url, params=params, headers=headers)
    #raw_data = response.json()
    #return raw_data
    return response.json()

#convert to CSV
def process_weather_data(raw_data):
   
    # Flatten the timeseries list
    df = pd.json_normalize(raw_data['properties']['timeseries'])

    # Rename and select specific columns
    # Note: json_normalize uses dots for nested keys
    column_map = {
        'time': 'timestamp',
        'data.instant.details.air_temperature': 'temperature',
        'data.instant.details.relative_humidity': 'humidity',
        'data.instant.details.wind_speed': 'wind_speed'
    }

    df_filtered = df[column_map.keys()].rename(columns=column_map)
    #df_filtered.to_csv('weather_data.csv', index=False) #write to file
    
    return df_filtered
print("done")
print(process_weather_data(get_weather_data()))