import requests

#data from client
lat = 21.37852609079965
lon = 39.79370287864698

#required for MET authentication
headers = {
    "User-Agent": "Firebuster/1.0 (firebuster.no)"
}

url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
params = {"lat": lat, "lon": lon}
response = requests.get(url, params=params, headers=headers)

data = response.json()
print(data)