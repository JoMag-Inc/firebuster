from app.repositories.weather.weather_repository import WeatherRepository
from sqlalchemy import create_engine
from decouple import config


class SQLAlchemyWeatherRepository(WeatherRepository):
    def get_connection(self):
        engine = create_engine(config("DATABASE_URL"))
        return engine

    def get_by_location(self):
        engine = self.get_connection()

    def add_weather_data(self, data_csv):
        pass
