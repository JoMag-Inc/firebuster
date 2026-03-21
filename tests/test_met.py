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

        #convert json to csv
        csv_output = process_weather_data(json_data)

        #check process_weather_data actually returned a csv string
        self.assertIsInstance(csv_output, str)
        #check if string is empty
        self.assertTrue(csv_output.strip())

        #io.StringIO(csv_output) to treat like file, use pandas to read into dataframe
        df = pd.read_csv(io.StringIO(csv_output))

        #check columns and names
        expected_columns = ['timestamp', 'temperature', 'humidity', 'wind_speed']
        self.assertListEqual(list(df.columns), expected_columns)

        #check columns if any missing value, if yes, print 
        self.assertFalse(df.isnull().any().any(), "CSV contains missing values")
        #check timestamp. convert to string, check string length, makes sure >0, for all tstmp
        self.assertTrue(df['timestamp'].astype(str).str.len().gt(0).all())
        #check type
        self.assertTrue(is_numeric_dtype(df['temperature']))
        self.assertTrue(is_numeric_dtype(df['humidity']))
        self.assertTrue(is_numeric_dtype(df['wind_speed']))
        