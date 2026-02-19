import unittest
from app.main import app 
from fastapi.testclient import TestClient


class TestHealth(unittest.TestCase):
    def test_get_health(self):
        client = TestClient(app)
        response = client.get("/api/health")
        self.assertEqual(200, response.status_code)
        self.assertEqual({"status": "ok"}, response.json())
