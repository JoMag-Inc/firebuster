from frcm import WeatherData, WeatherDataPoint, compute
import csv
from io import StringIO

class TTFCalculator:
    """Calculates TTF from weather data using dynamic-frcm-simple"""
    
    @staticmethod
    def create_weather_point(timestamp: str, temperature: float, humidity: float, wind_speed: float) -> WeatherDataPoint:
        """
        Create a single WeatherDataPoint
        Args:
            timestamp: Data point timestamp
            temperature: Temperature value
            humidity: Humidity value
            wind_speed: Wind speed value
        Returns: WeatherDataPoint object
        """
        return WeatherDataPoint(
            timestamp=timestamp,
            temperature=temperature,
            humidity=humidity,
            wind_speed=wind_speed
        )
    
    @staticmethod
    def calculate_from_points(data_points: list):
        """
        Calculate TTF from a list of WeatherDataPoint objects
        Args:
            data_points: List of WeatherDataPoint objects (minimum 2 points required)
        Returns: FireRisk object with TTF results
        Note: The frcm library requires at least 2 data points for gap detection
        """
        if len(data_points) < 2:
            raise ValueError("At least 2 data points are required for TTF calculation")
        
        weather_data = WeatherData(data=data_points)
        results = compute(weather_data)
        return results
    
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
            point = TTFCalculator.create_weather_point(
                timestamp=row['timestamp'],
                temperature=float(row['temperature']),
                humidity=float(row['humidity']),
                wind_speed=float(row['wind_speed'])
            )
            data_points.append(point)
        
        return TTFCalculator.calculate_from_points(data_points)