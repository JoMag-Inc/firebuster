from sqlalchemy import create_engine
from sqlmodel import Session
from decouple import config

from app.repositories.ttf.ttf_repository import PostgresTTFRepository
from app.services.ttf.ttf_service import TTFService
from app.services.weather.weather_service import WeatherService


def _get_engine():
    url = config("DATABASE_URL", default="")
    if not url:
        return None
    return create_engine(url)


engine = _get_engine()


def get_ttf_service():
    db_engine = engine
    if db_engine is None:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    with Session(db_engine) as session:
        repo = PostgresTTFRepository(session)
        weather_service = WeatherService()
        yield TTFService(repo=repo, weather_service=weather_service)
