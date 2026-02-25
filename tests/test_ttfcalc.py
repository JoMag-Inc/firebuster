import unittest

from app.services.ttf_calculator import TTFCalculator, TTFResult
from frcm import WeatherDataPoint

class TestTTFCalculator(unittest.TestCase):
    def test_create_weather_point(self):
        """Test creating a single weather data point"""
        point = TTFCalculator.create_weather_point(
            timestamp="2026-01-07T00:00:00+00:00",
            temperature=10.5,
            humidity=65,
            wind_speed=5.2
        )
        
        self.assertIsNotNone(point)
        self.assertEqual(point.temperature, 10.5)
        self.assertEqual(point.humidity, 65)
        self.assertEqual(point.wind_speed, 5.2)
    
    def test_calculate_from_points(self):
        """Test TTF calculation from a list of data points"""
        points = [
            TTFCalculator.create_weather_point("2026-01-07T00:00:00+00:00", 10.5, 65, 5.2),
            TTFCalculator.create_weather_point("2026-01-07T01:00:00+00:00", 11.0, 63, 5.5)
        ]
        
        results = TTFCalculator.calculate_from_points(points)
        
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], TTFResult)
        self.assertIsInstance(results[0].weather_point, WeatherDataPoint)
        self.assertEqual(results[0].weather_point.temperature, 10.5)
        self.assertEqual(results[0].weather_point.humidity, 65)
        self.assertEqual(results[0].weather_point.wind_speed, 5.2)
        self.assertIsInstance(results[0].ttf, float)
    
    def test_calculate_from_csv(self):
        """Test TTF calculation from CSV data"""
        csv_data = """timestamp,temperature,humidity,wind_speed
2026-01-07T00:00:00+00:00,10.5,65,5.2
2026-01-07T01:00:00+00:00,11.0,63,5.5"""
        
        results = TTFCalculator.calculate_from_csv(csv_data)
        
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], TTFResult)
        self.assertIsInstance(results[0].weather_point, WeatherDataPoint)
        self.assertEqual(results[0].weather_point.temperature, 10.5)
        self.assertEqual(results[0].weather_point.humidity, 65)
        self.assertEqual(results[0].weather_point.wind_speed, 5.2)
        self.assertIsInstance(results[0].ttf, float)

if __name__ == '__main__':
    unittest.main()