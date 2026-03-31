from app.services.weather.weather_get import (
    get_weather_data_for_coordinates,
    process_weather_data,
)


class WeatherService:
    def get_weather_at_location(self, lat, lon):
        data = get_weather_data_for_coordinates(lat, lon)
        csv_output = process_weather_data(data)
        return csv_output
