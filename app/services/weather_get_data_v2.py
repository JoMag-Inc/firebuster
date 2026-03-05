import pandas as pd
import requests
import json

#test data from client
lat = 21.37852609079965
lon = 39.79370287864698

#required for MET authentication
headers = {
    "User-Agent": "Firebuster/1.0 (firebuster.no)"
}

#use compact api to limit amount of data
url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
params = {"lat": lat, "lon": lon}
response = requests.get(url, params=params, headers=headers)

#raw data goes here
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
    df_filtered.to_csv('weather_data.csv', index=False)
    
    return df_filtered

processed_list = process_weather_data(data) #move to test
print(processed_list)
