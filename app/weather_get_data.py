import requests
import json

#data from client
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

########################
#INFORMATION ABOUT DATA#
########################
#data contains lots of unnecessary information, so remove everything except for:
#Timestamp with included: temperature, humidity, windspeed
#Note: The data contains hourly values for 3 days, then, every 6h for 7 days (total 10 days)
#The values we want are in:
#"properties":
#   "timeseries":
#       "data":
#           "instant":
#               "details":

def process_weather_data(raw_data):
    clean_data = []
    
    # 1. Access the list of time entries
    timeseries = raw_data['properties']['timeseries']
    
    # 2. Loop through each hour
    for entry in timeseries:
        # 3. Use 'get' or direct keys to extract specific values
        # We go deep into the 'details' folder for each entry
        details = entry['data']['instant']['details']
        
        # 4. Create a simplified dictionary
        simplified_entry = {
            "timestamp": entry['time'],
            "temp": details['air_temperature'],
            "humidity": details['relative_humidity'],
            "wind_speed": details['wind_speed']
        }
        
        # 5. Add it to our clean list
        clean_data.append(simplified_entry)
    
    return clean_data

processed_list = process_weather_data(data)
print(processed_list)