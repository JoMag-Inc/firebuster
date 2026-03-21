import pandas as pd
from pandas.api.types import is_numeric_dtype
import io
import json
import unittest
from app.services.weather.weather_get import process_weather_data

class TestMetClient(unittest.TestCase):
    def test_json_to_csv(self):
        with open('tests/data/json_reference.json', 'r') as f:
            json_data = json.load(f)

        csv_output = process_weather_data(json_data)

        # Function contract: returns CSV string
        self.assertIsInstance(csv_output, str)
        self.assertTrue(csv_output.strip())

        # Parse CSV string for structural validation
        df = pd.read_csv(io.StringIO(csv_output))

        expected_columns = ['timestamp', 'temperature', 'humidity', 'wind_speed']
        self.assertListEqual(list(df.columns), expected_columns)

        self.assertFalse(df.isnull().any().any(), "CSV contains missing values")
        self.assertTrue(df['timestamp'].astype(str).str.len().gt(0).all())
        self.assertTrue(is_numeric_dtype(df['temperature']))
        self.assertTrue(is_numeric_dtype(df['humidity']))
        self.assertTrue(is_numeric_dtype(df['wind_speed']))
        