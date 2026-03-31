from datetime import datetime, timezone

from app.models.ttf_result import TTFResult
from app.services.ttf_calculator import TTFCalculator


class TTFService:
    def __init__(self, repo, weather_service):
        self.repo = repo
        self.weather_service = weather_service

    def get(self, lat, lon):
        cached = self.repo.get(lat, lon)
        if cached:
            return cached

        data_csv = self.weather_service.get_weather_at_location(lat, lon)
        ttf_points = TTFCalculator.calculate_from_csv(data_csv)

        result = TTFResult(
            latitude=lat,
            longitude=lon,
            calculated_at=datetime.now(timezone.utc),
            ttf_minutes=[p.ttf for p in ttf_points],
            weather_input=[p.weather_point.model_dump(mode="json") for p in ttf_points],
        )

        self.repo.save(result)
        return result
