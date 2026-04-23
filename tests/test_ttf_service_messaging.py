import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from app.models.ttf_result import TTFResult
from app.services.messaging.mqtt_service import MQTTService
from app.services.ttf.ttf_service import TTFService


class TestMQTTService(unittest.TestCase):
    def test_publish_is_noop_when_disabled(self):
        service = MQTTService(
            enabled=False,
            host="localhost",
            port=1883,
            topic="firebuster/fire-risk",
        )

        result = TTFResult(
            latitude=61.45,
            longitude=5.85,
            calculated_at=datetime.now(timezone.utc),
            ttf_points=[{"ttf": 1.23}],
        )

        self.assertFalse(service.publish_fire_risk(result, source="fresh"))

    @patch("app.services.messaging.mqtt_service.publish.single")
    def test_publish_sends_payload(self, mock_publish_single):
        service = MQTTService(
            enabled=True,
            host="localhost",
            port=1883,
            topic="firebuster/fire-risk",
            qos=0,
            keepalive=60,
        )

        result = TTFResult(
            latitude=61.45,
            longitude=5.85,
            calculated_at=datetime.now(timezone.utc),
            ttf_points=[{"ttf": 1.23}],
        )

        published = service.publish_fire_risk(result, source="fresh")

        self.assertTrue(published)
        mock_publish_single.assert_called_once()


class TestTTFServiceMessaging(unittest.TestCase):
    def test_publishes_cached_result(self):
        cached = TTFResult(
            latitude=61.45,
            longitude=5.85,
            calculated_at=datetime.now(timezone.utc),
            ttf_points=[{"ttf": 2.34}],
        )

        repo = Mock()
        repo.get.return_value = cached

        weather_service = Mock()
        mqtt_service = Mock()

        service = TTFService(
            repo=repo,
            weather_service=weather_service,
            messaging_service=mqtt_service,
        )

        result = service.get(61.45, 5.85)

        self.assertEqual(cached, result)
        mqtt_service.publish_fire_risk.assert_called_once_with(cached, source="cache")

    @patch("app.services.ttf.ttf_service.TTFCalculator.calculate_from_csv")
    def test_publishes_fresh_result(self, mock_calculate):
        repo = Mock()
        repo.get.return_value = None

        weather_service = Mock()
        weather_service.get_weather_at_location.return_value = "csv"

        mock_point = Mock()
        mock_point.model_dump.return_value = {"ttf": 1.11}
        mock_calculate.return_value = [mock_point]

        mqtt_service = Mock()

        service = TTFService(
            repo=repo,
            weather_service=weather_service,
            messaging_service=mqtt_service,
        )

        result = service.get(61.45, 5.85)

        self.assertEqual(61.45, result.latitude)
        self.assertEqual(5.85, result.longitude)
        mqtt_service.publish_fire_risk.assert_called_once_with(result, source="fresh")


if __name__ == "__main__":
    unittest.main()
