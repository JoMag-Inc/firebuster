import unittest
from app.main import app
from fastapi.testclient import TestClient

class TestMet(unittest.TestCase):
    def test_get_met():
        print("hi from met test")