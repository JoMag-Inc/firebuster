from sqlalchemy import create_engine
from sqlmodel import Session
from decouple import config

from app.repositories.ttf.ttf_repository import PostgresTTFRepository
from app.services.ttf.ttf_service import TTFService
from app.services.weather.weather_service import WeatherService

engine = create_engine(config("DATABASE_URL"))


def get_ttf_service():
    with Session(engine) as session:
        repo = PostgresTTFRepository(session)
        weather_service = WeatherService()
        yield TTFService(repo=repo, weather_service=weather_service)
