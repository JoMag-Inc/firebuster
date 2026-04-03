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
    """Factory for creating and configuring application services."""

    def __init__(
        self,
        database_url: str | None = None,
        weather_config: dict | None = None,
    ):
        # Set database URL from parameter or environment
        if database_url is None:
            database_url = config("DATABASE_URL", default="")

        self.database_url = database_url
        if not self.database_url:
            raise ValueError(
                "Database URL must be provided or set in DATABASE_URL environment variable"
            )

        # Create database engine
        self.engine: Engine = create_engine(self.database_url)

        # Set weather configuration
        if weather_config is None:
            self.weather_config = {
                "base_url": weather_static.met_base_url,
                "headers": weather_static.met_required_headers,
                "timeout": 10,
            }
        else:
            self.weather_config = weather_config

    def create_ttf_service(self):
        """Create a fully configured TTF service with all dependencies."""
        with Session(self.engine) as session:
            repo = PostgresTTFRepository(session)
            weather_service = WeatherService(**self.weather_config)
            yield TTFService(repo=repo, weather_service=weather_service)


# Module-level factory instance
factory: ServiceFactory | None = None


def get_factory() -> ServiceFactory:
    """Get or create the default factory instance."""
    global factory
    if factory is None:
        factory = ServiceFactory()
    return factory


def get_ttf_service():
    """Get a TTF service instance (for FastAPI dependency injection)."""
    factory = get_factory()
    yield from factory.create_ttf_service()
