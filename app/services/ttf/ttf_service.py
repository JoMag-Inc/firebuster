"""TTF (Time To Flashover) Service.

This service provides the main business logic for calculating Time To Flashover
values based on weather data. It orchestrates between the weather service,
TTF calculator, and repository to provide cached and fresh TTF calculations.
"""

from datetime import datetime, timezone

import requests

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

    def __init__(self, repo, weather_service, messaging_service=None):
        self.repo = repo
        self.weather_service = weather_service
        self.messaging_service = messaging_service

    def _publish_fire_risk(self, result: TTFResult, source: str) -> None:
        """Best-effort fire-risk publish to keep API responses resilient."""
        if self.messaging_service is None:
            return
        self.messaging_service.publish_fire_risk(result, source=source)

    @staticmethod
    def _is_from_current_hour(timestamp: datetime) -> bool:
        if timestamp.tzinfo is None:
            cached_utc = timestamp.replace(tzinfo=timezone.utc)
        else:
            cached_utc = timestamp.astimezone(timezone.utc)

        current_utc = datetime.now(timezone.utc)

        cached_hour = cached_utc.replace(minute=0, second=0, microsecond=0)
        current_hour = current_utc.replace(minute=0, second=0, microsecond=0)
        return cached_hour == current_hour

    def get(self, lat: float, lon: float) -> TTFResult:
        """Get TTF calculation results for specific coordinates.

        This method first checks for cached results in the repository. If no
        cached data exists, it fetches fresh weather data, calculates TTF values,
        stores the result, and returns it.

        Args:
            lat: Latitude coordinate (decimal degrees, -90 to 90)
            lon: Longitude coordinate (decimal degrees, -180 to 180)

        Returns:
            TTFResult: Object containing TTF calculations and metadata including:
                - latitude: The requested latitude
                - longitude: The requested longitude
                - calculated_at: UTC timestamp of calculation
                - ttf_points: List of combined weather data and TTF values
        """
        try:
            cached = self.repo.get(lat, lon)
        except Exception as e:
            raise RuntimeError("Failed to read cached TTF result") from e

        if cached:
            if self._is_from_current_hour(cached.calculated_at):
                self._publish_fire_risk(cached, source="cache")
                return cached

            try:
                self.repo.delete(lat, lon)
            except Exception as e:
                raise RuntimeError("Failed to delete stale cached TTF result") from e

        try:
            data_csv = self.weather_service.get_weather_at_location(lat, lon)
        except requests.RequestException as e:
            raise ConnectionError("Weather provider is unavailable") from e
        except ValueError as e:
            raise ValueError("Weather provider returned invalid data") from e

        # calculate ttf points using frcm module
        ttf_points = TTFCalculator.calculate_from_csv(data_csv)

        result = TTFResult(
            latitude=lat,
            longitude=lon,
            calculated_at=datetime.now(timezone.utc),
            ttf_points=[p.model_dump(mode="json") for p in ttf_points],
        )

        try:
            self.repo.save(result)
        except Exception as e:
            raise RuntimeError("Failed to store TTF result") from e

        self._publish_fire_risk(result, source="fresh")
        return result
