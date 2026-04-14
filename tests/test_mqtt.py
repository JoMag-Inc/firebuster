import json
import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from app.models.ttf_result import TTFResult
from app.services.mqtt.mqtt_service import MQTTService


class TestMQTTService(unittest.TestCase):
    @patch("app.services.mqtt.mqtt_service.mqtt.Client")
    def test_publish_fire_risk_publishes_json_payload(self, mock_client_class):
        client = Mock()
        mock_client_class.return_value = client

        publish_info = Mock()
        publish_info.rc = 0
        publish_info.wait_for_publish.return_value = None
        client.publish.return_value = publish_info

        service = MQTTService(
            host="mqtt",
            port=1883,
            topic="firebuster/fire-risk",
            client_id="firebuster-api",
        )

        result = TTFResult(
            latitude=60.0,
            longitude=5.0,
            calculated_at=datetime(2026, 4, 14, 12, 0, tzinfo=timezone.utc),
            ttf_points=[{"timestamp": "2026-04-14T12:00:00Z", "ttf": 42.0}],
        )

        service.publish_fire_risk(result)

        client.connect.assert_called_once_with("mqtt", 1883, keepalive=60)
        client.loop_start.assert_called_once()
        client.publish.assert_called_once()
        client.loop_stop.assert_called_once()
        client.disconnect.assert_called_once()

        topic, payload = client.publish.call_args.args[:2]
        self.assertEqual("firebuster/fire-risk", topic)

        payload_data = json.loads(payload)
        self.assertEqual("fire_risk.calculated", payload_data["event_type"])
        self.assertEqual(60.0, payload_data["latitude"])
        self.assertEqual(5.0, payload_data["longitude"])

    @patch("app.services.mqtt.mqtt_service.mqtt.Client")
    def test_publish_fire_risk_raises_on_publish_failure(self, mock_client_class):
        client = Mock()
        mock_client_class.return_value = client

        publish_info = Mock()
        publish_info.rc = 1
        publish_info.wait_for_publish.return_value = None
        client.publish.return_value = publish_info

        service = MQTTService(
            host="mqtt",
            port=1883,
            topic="firebuster/fire-risk",
            client_id="firebuster-api",
        )

        result = TTFResult(
            latitude=60.0,
            longitude=5.0,
            calculated_at=datetime(2026, 4, 14, 12, 0, tzinfo=timezone.utc),
            ttf_points=[{"timestamp": "2026-04-14T12:00:00Z", "ttf": 42.0}],
        )

        with self.assertRaises(RuntimeError):
            service.publish_fire_risk(result)
