"""Simple MQTT messaging service for publishing fire risk updates."""

import json
import logging

import paho.mqtt.publish as publish


logger = logging.getLogger(__name__)


class MQTTService:
    """Small helper for publishing fire risk payloads to an MQTT topic."""

    def __init__(
        self,
        enabled: bool,
        host: str,
        port: int,
        topic: str,
        qos: int = 0,
        keepalive: int = 60,
        username: str | None = None,
        password: str | None = None,
    ):
        self.enabled = enabled
        self.host = host
        self.port = port
        self.topic = topic
        self.qos = qos
        self.keepalive = keepalive
        self.username = username
        self.password = password

    def publish_fire_risk(self, ttf_result, source: str) -> bool:
        """Publish a fire risk update to MQTT.

        Returns True when a message was published, otherwise False.
        """
        if not self.enabled:
            return False

        payload = {
            "event": "fire_risk_update",
            "source": source,
            "latitude": ttf_result.latitude,
            "longitude": ttf_result.longitude,
            "calculated_at": ttf_result.calculated_at.isoformat(),
            "ttf_points": ttf_result.ttf_points,
        }

        auth = None
        if self.username:
            auth = {"username": self.username, "password": self.password}

        try:
            publish.single(
                topic=self.topic,
                payload=json.dumps(payload),
                hostname=self.host,
                port=self.port,
                qos=self.qos,
                keepalive=self.keepalive,
                auth=auth,
            )
            return True
        except Exception:
            logger.warning("MQTT publish failed", exc_info=True)
            return False
