"""Application factory for dependency injection and service creation."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlmodel import Session
from decouple import config

from app.repositories.ttf.ttf_repository import PostgresTTFRepository
from app.services.ttf.ttf_service import TTFService
from app.services.weather.weather_service import WeatherService
from app.services.weather import weather_static


class ServiceFactory:
    def __init__(self, database_url: str, weather_config: dict):
        self.engine: Engine = create_engine(database_url)
        self.weather_service = WeatherService(
            base_url=weather_config["base_url"],
            headers=weather_config["headers"],
            timeout=weather_config["timeout"],
        )

    def create_ttf_service(self, session: Session) -> TTFService:
        """Create a TTF service — caller manages the session."""
        repo = PostgresTTFRepository(session)
        return TTFService(repo=repo, weather_service=self.weather_service)


factory: ServiceFactory | None = None


def get_factory() -> ServiceFactory:
    """Get or create the default factory instance."""
    global factory
    if factory is None:
        factory = ServiceFactory(
            database_url=config("DATABASE_URL"),
            weather_config={
                "base_url": weather_static.met_base_url,
                "headers": weather_static.met_required_headers,
                "timeout": 10,
            },
        )
    return factory


def get_ttf_service():
    """FastAPI dependency — yields a TTFService with a managed session."""
    factory = get_factory()
    with Session(factory.engine) as session:
        yield factory.create_ttf_service(session)
