import unittest
from app.main import get_health

class TestHealth(unittest.TestCase):
    def test_get_health(self):
        health = get_health()
        self.assertEqual({"status": "ok"}, health)
