import io
import pandas as pd
from app.repositories.weather_repository import WeatherRepository
from app.services.weather.weather_get import (
    get_weather_data_for_coordinates,
    process_weather_data,
)


class WeatherService:
    def __init__(self) -> None:
        self.repository = WeatherRepository()

    def get_weather_at_location(self, long, lat):
        cached_csv = self.repository.get_by_location(long, lat)
        if cached_csv:
            print("Cache hit! Retrieving from database")
            return cached_csv

        print("Cache Miss! Retrieving from API")
        data = get_weather_data_for_coordinates(long, lat)
        csv_output = process_weather_data(data)
        self.save_weather_csv(csv_output, long, lat)
        return csv_output

    def save_weather_csv(self, csv_output, long, lat):
        df = pd.read_csv(io.StringIO(csv_output))
        self.repository.add(df, long, lat)
