import unittest
from app.services.ttf_calculator import TTFCalculator

class TestTTFCalculator(unittest.TestCase):
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