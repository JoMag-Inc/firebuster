met_base_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"

#required for MET authentication
met_required_headers = {
    "User-Agent": "Firebuster/1.0 (firebuster.no)"
}

#put this in test later
#test data from client
lat = 21.37852609079965
lon = 39.79370287864698
met_example_coordinates = {"lat": lat, "lon": lon}