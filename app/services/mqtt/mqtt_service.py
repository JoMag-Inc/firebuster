"""Minimal MQTT publisher for fire-risk events."""

from __future__ import annotations

import json
import logging

import paho.mqtt.client as mqtt

from app.models.ttf_result import TTFResult


logger = logging.getLogger(__name__)


class MQTTService:
    def __init__(
        self,
        host: str,
        port: int,
        topic: str,
        client_id: str,
        username: str = "",
        password: str = "",
    ):
        self.host = host
        self.port = port
        self.topic = topic
        self.client_id = client_id
        self.username = username
        self.password = password

    def publish_fire_risk(self, result: TTFResult) -> None:
        client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)

        if self.username:
            client.username_pw_set(self.username, self.password)

        try:
            client.connect(self.host, self.port, keepalive=60)
            client.loop_start()

            payload = {
                "event_type": "fire_risk.calculated",
                **result.model_dump(mode="json"),
            }

            message_info = client.publish(
                self.topic,
                json.dumps(payload),
                qos=1,
            )
            message_info.wait_for_publish()

            if message_info.rc != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError("MQTT publish returned a failure status")
        except Exception as exc:
            raise RuntimeError("Failed to publish fire-risk message") from exc
        finally:
            try:
                client.loop_stop()
            except Exception as exc:
                logger.debug("Ignoring MQTT loop_stop cleanup error: %s", exc, exc_info=True)
            try:
                client.disconnect()
            except Exception as exc:
                logger.debug("Ignoring MQTT disconnect cleanup error: %s", exc, exc_info=True)