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

    def __init__(self, repo, weather_service, messaging_service=None):
        self.repo = repo
        self.weather_service = weather_service
        self.messaging_service = messaging_service

    def _publish_fire_risk(self, result: TTFResult, source: str) -> None:
        """Best-effort fire-risk publish to keep API responses resilient."""
        if self.messaging_service is None:
            return
        self.messaging_service.publish_fire_risk(result, source=source)

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
        cached = self.repo.get(lat, lon)
        if cached:
            self._publish_fire_risk(cached, source="cache")
            return cached

        try:
            data_csv = self.weather_service.get_weather_at_location(lat, lon)
        except Exception:
            raise HTTPException(status_code=503, detail="Failed to fetch weather data")

        ttf_points = TTFCalculator.calculate_from_csv(data_csv)

        result = TTFResult(
            latitude=lat,
            longitude=lon,
            calculated_at=datetime.now(timezone.utc),
            ttf_points=[p.model_dump(mode="json") for p in ttf_points],
        )

        self.repo.save(result)
        self._publish_fire_risk(result, source="fresh")
        return result
