import unittest
from app.services.ttf_calculator import TTFCalculator

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
        print(f"\nResults from points: {results}")
        for risk in results.firerisks:
            print(f"  {risk.timestamp}: TTF = {risk.ttf}")
        
        self.assertIsNotNone(results)
        self.assertEqual(len(results.firerisks), 2)
    
    def test_calculate_from_csv(self):
        """Test TTF calculation from CSV data"""
        csv_data = """timestamp,temperature,humidity,wind_speed
2026-01-07T00:00:00+00:00,10.5,65,5.2
2026-01-07T01:00:00+00:00,11.0,63,5.5"""
        
        results = TTFCalculator.calculate_from_csv(csv_data)
        print(f"\nResults: {results}")
        for risk in results.firerisks:
            print(f"  {risk.timestamp}: TTF = {risk.ttf}")
        
        self.assertIsNotNone(results)
        self.assertGreater(len(results.firerisks), 0)

if __name__ == '__main__':
    unittest.main()