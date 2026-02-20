from frcm import WeatherData, WeatherDataPoint, compute
import csv
from io import StringIO
from datetime import datetime

class TTFCalculator:
    """Calculates TTF from weather data using dynamic-frcm-simple"""
    
    @staticmethod
    def calculate_from_csv(csv_content: str):
        """
        Calculate TTF from CSV data
        Expected columns: timestamp, temperature, humidity, wind_speed
        Returns: FireRisk object with TTF results
        """
        data_points = []
        reader = csv.DictReader(StringIO(csv_content))
        
        for row in reader:
            point = WeatherDataPoint(
                timestamp=row['timestamp'],
                temperature=float(row['temperature']),
                humidity=float(row['humidity']),
                wind_speed=float(row['wind_speed'])
            )
            data_points.append(point)
        
        weather_data = WeatherData(data=data_points)
        results = compute(weather_data)
        return results