"""Application factory for dependency injection and service creation."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlmodel import Session
from decouple import config

from app.services.mqtt.mqtt_service import MQTTService
from app.repositories.ttf.ttf_repository import PostgresTTFRepository
from app.services.ttf.ttf_service import TTFService
from app.services.weather.weather_service import WeatherService
from app.services.weather import weather_static


class ServiceFactory:
    def __init__(self, database_url: str, service_config: dict):
        self.engine: Engine = create_engine(database_url)
        self.weather_service = self._build_weather_service(service_config)
        self.mqtt_service = self._build_mqtt_service(service_config)

    def _build_weather_service(self, service_config: dict) -> WeatherService:
        return WeatherService(
            base_url=service_config["base_url"],
            headers=service_config["headers"],
            timeout=service_config["timeout"],
        )

    def _build_mqtt_service(self, service_config: dict) -> MQTTService:
        return MQTTService(
            host=service_config["mqtt_broker_host"],
            port=service_config["mqtt_broker_port"],
            topic=service_config["mqtt_topic"],
            client_id=service_config["mqtt_client_id"],
            username=service_config["mqtt_username"],
            password=service_config["mqtt_password"],
        )

    def create_ttf_service(self, session: Session) -> TTFService:
        """Create a TTF service — caller manages the session."""
        repo = PostgresTTFRepository(session)
        return TTFService(
            repo=repo,
            weather_service=self.weather_service,
            mqtt_service=self.mqtt_service,
        )


factory: ServiceFactory | None = None


def get_factory() -> ServiceFactory:
    """Get or create the default factory instance."""
    global factory
    if factory is None:
        factory = ServiceFactory(
            database_url=config("DATABASE_URL"),
            service_config=_build_service_config(),
        )
    return factory


def _build_service_config() -> dict:
    return {
        "base_url": weather_static.met_base_url,
        "headers": weather_static.met_required_headers,
        "timeout": 10,
        "mqtt_broker_host": config("MQTT_BROKER_HOST", default="mqtt"),
        "mqtt_broker_port": config("MQTT_BROKER_PORT", default=1883, cast=int),
        "mqtt_topic": config("MQTT_TOPIC", default="firebuster/fire-risk"),
        "mqtt_client_id": config("MQTT_CLIENT_ID", default="firebuster-api"),
        "mqtt_username": config("MQTT_USERNAME", default=""),
        "mqtt_password": config("MQTT_PASSWORD", default=""),
    }


def get_ttf_service():
    """FastAPI dependency — yields a TTFService with a managed session."""
    factory = get_factory()
    with Session(factory.engine) as session:
        yield factory.create_ttf_service(session)
