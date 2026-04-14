"""TTF (Time To Flashover) Service.

This service provides the main business logic for calculating Time To Flashover
values based on weather data. It orchestrates between the weather service,
TTF calculator, and repository to provide cached and fresh TTF calculations.
"""

from datetime import datetime, timezone
from fastapi import HTTPException

from app.models.ttf_result import TTFResult
from app.services.ttf.ttf_calculator import TTFCalculator


class TTFService:
    """Service for calculating and managing Time To Flashover (TTF) data.

    This service acts as the main coordinator for TTF calculations, managing
    the interaction between weather data fetching, TTF calculations, and
    result persistence.

    Attributes:
        repo: Repository instance for storing and retrieving TTF results
        weather_service: Service instance for fetching weather data
    """

    def __init__(self, repo, weather_service, mqtt_service=None):
        self.repo = repo
        self.weather_service = weather_service
        self.mqtt_service = mqtt_service

    def get(self, lat: float, lon: float) -> TTFResult:
        cached = self._get_cached_result(lat, lon)
        if cached:
            return cached

        data_csv = self._fetch_weather_csv(lat, lon)
        result = self._build_ttf_result(lat, lon, data_csv)

        self.repo.save(result)
        self._publish_fire_risk(result)

        return result

    def _get_cached_result(self, lat: float, lon: float) -> TTFResult | None:
        return self.repo.get(lat, lon)

    def _fetch_weather_csv(self, lat: float, lon: float) -> str:
        try:
            return self.weather_service.get_weather_at_location(lat, lon)
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Failed to fetch weather data") from exc

    def _build_ttf_result(self, lat: float, lon: float, data_csv: str) -> TTFResult:
        ttf_points = TTFCalculator.calculate_from_csv(data_csv)

        return TTFResult(
            latitude=lat,
            longitude=lon,
            calculated_at=datetime.now(timezone.utc),
            ttf_points=[p.model_dump(mode="json") for p in ttf_points],
        )

    def _publish_fire_risk(self, result: TTFResult) -> None:
        if self.mqtt_service is None:
            return

        try:
            self.mqtt_service.publish_fire_risk(result)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail="Failed to publish fire-risk message",
            ) from exc
