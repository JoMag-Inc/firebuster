import unittest
from app.main import app
from app.services.weather.weather_get_data_v2 import process_weather_data
from fastapi.testclient import TestClient

class TestMet(unittest.TestCase):
    def test_get_met(self):
        self.assertEqual()