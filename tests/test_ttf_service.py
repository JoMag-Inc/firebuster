import unittest
from unittest.mock import Mock, patch

from fastapi import HTTPException

from app.services.ttf.ttf_service import TTFService


class TestTTFServiceMQTT(unittest.TestCase):
    @patch("app.services.ttf.ttf_service.TTFCalculator.calculate_from_csv")
    def test_get_publishes_fire_risk_after_save(self, mock_calculate):
        point = Mock()
        point.model_dump.return_value = {
            "timestamp": "2026-04-14T12:00:00Z",
            "temperature": 10.0,
            "humidity": 60.0,
            "wind_speed": 3.0,
            "ttf": 42.0,
        }
        mock_calculate.return_value = [point]

        repo = Mock()
        repo.get.return_value = None
        weather_service = Mock()
        weather_service.get_weather_at_location.return_value = (
            "timestamp,temperature,humidity,wind_speed\n"
            "2026-04-14T12:00:00Z,10,60,3\n"
            "2026-04-14T13:00:00Z,11,59,4\n"
        )
        mqtt_service = Mock()

        service = TTFService(
            repo=repo,
            weather_service=weather_service,
            mqtt_service=mqtt_service,
        )

        result = service.get(60.0, 5.0)

        repo.save.assert_called_once()
        mqtt_service.publish_fire_risk.assert_called_once_with(result)
        self.assertEqual(60.0, result.latitude)
        self.assertEqual(5.0, result.longitude)
        self.assertEqual(1, len(result.ttf_points))

    @patch("app.services.ttf.ttf_service.TTFCalculator.calculate_from_csv")
    def test_get_raises_when_mqtt_publish_fails(self, mock_calculate):
        point = Mock()
        point.model_dump.return_value = {
            "timestamp": "2026-04-14T12:00:00Z",
            "temperature": 10.0,
            "humidity": 60.0,
            "wind_speed": 3.0,
            "ttf": 42.0,
        }
        mock_calculate.return_value = [point]

        repo = Mock()
        repo.get.return_value = None
        weather_service = Mock()
        weather_service.get_weather_at_location.return_value = (
            "timestamp,temperature,humidity,wind_speed\n"
            "2026-04-14T12:00:00Z,10,60,3\n"
            "2026-04-14T13:00:00Z,11,59,4\n"
        )
        mqtt_service = Mock()
        mqtt_service.publish_fire_risk.side_effect = RuntimeError("broker down")

        service = TTFService(
            repo=repo,
            weather_service=weather_service,
            mqtt_service=mqtt_service,
        )

        with self.assertRaises(HTTPException) as context:
            service.get(60.0, 5.0)

        self.assertEqual(503, context.exception.status_code)
        repo.save.assert_called_once()
