from sqlalchemy import create_engine
from sqlmodel import Session
from decouple import config

from app.repositories.ttf.ttf_repository import PostgresTTFRepository
from app.services.ttf.ttf_service import TTFService
from app.services.weather.weather_service import WeatherService
from app.services.weather import weather_static


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
        weather_service = WeatherService(
            base_url=weather_static.met_base_url,
            headers=weather_static.met_required_headers,
            timeout=10,
        )
        yield TTFService(repo=repo, weather_service=weather_service)
