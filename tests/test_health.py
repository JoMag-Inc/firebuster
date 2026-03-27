import unittest
from app.restapi import app
from fastapi.testclient import TestClient

client = TestClient(app)


class TestHealth(unittest.TestCase):
    def test_get_health(self):
        client = TestClient(app)
        response = client.get("/api/health")
        self.assertEqual(200, response.status_code)
        self.assertEqual({"status": "ok"}, response.json())
