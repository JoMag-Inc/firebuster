from app.repositories.weather_repository import WeatherRepository


class WeatherService:
    def __init__(self) -> None:
        self.repository = WeatherRepository()

    def get_weather(self):
        weather_csv = self.repository.get_weather()
        return weather_csv

    def save_weather_csv(self, weather_csv):
        pass
