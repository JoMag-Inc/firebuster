import pandas as pd
import requests
import json
import weather_static

headers = weather_static.met_required_headers
url = weather_static.met_base_url
params = weather_static.met_example_coordinates
response = requests.get(url, params=params, headers=headers)

#raw data
data = response.json()

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
    
    #csv formatted weather data
    return df_filtered

print(process_weather_data(data))