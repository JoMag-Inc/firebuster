import csv
from dataclasses import dataclass
from io import StringIO

from frcm import WeatherData, WeatherDataPoint, compute


@dataclass(frozen=True)
class TTFResult:
    weather_point: WeatherDataPoint
    ttf: float

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
    def calculate_from_points(data_points: list[WeatherDataPoint]) -> list[TTFResult]:
        """
        Calculate TTF from a list of WeatherDataPoint objects
        Args:
            data_points: List of WeatherDataPoint objects (minimum 2 points required)
        Returns: List of TTFResult objects with weather context
        Note: The frcm library requires at least 2 data points for gap detection
        """
        if len(data_points) < 2:
            raise ValueError("At least 2 data points are required for TTF calculation")
        
        weather_data = WeatherData(data=data_points)
        results = compute(weather_data)

        ttf_values = [risk.ttf for risk in results.firerisks]
        count = min(len(data_points), len(ttf_values))
        return [
            TTFResult(weather_point=data_points[index], ttf=float(ttf_values[index]))
            for index in range(count)
        ]
    
    @staticmethod
    def calculate_from_csv(csv_content: str) -> list[TTFResult]:
        """
        Calculate TTF from CSV data
        Expected columns: timestamp, temperature, humidity, wind_speed
        Returns: List of TTFResult objects with weather context
        Raises:
            ValueError: If CSV is empty, missing required columns, or has invalid data types
        """
        if not csv_content or not csv_content.strip():
            raise ValueError("CSV content cannot be empty")
        
        data_points = []
        reader = csv.DictReader(StringIO(csv_content))
        
        required_columns = {'timestamp', 'temperature', 'humidity', 'wind_speed'}
        
        for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
            # Check for missing columns on first row
            if row_num == 2:
                missing_columns = required_columns - set(row.keys())
                if missing_columns:
                    raise ValueError(f"Missing required columns: {', '.join(sorted(missing_columns))}")
            
            try:
                point = TTFCalculator.create_weather_point(
                    timestamp=row['timestamp'],
                    temperature=float(row['temperature']),
                    humidity=float(row['humidity']),
                    wind_speed=float(row['wind_speed'])
                )
                data_points.append(point)
            except KeyError as e:
                raise ValueError(f"Missing required column: {e}")
            except ValueError as e:
                raise ValueError(f"Invalid data at row {row_num}: {e}")
        
        if not data_points:
            raise ValueError("CSV contains no data rows")
        
        return TTFCalculator.calculate_from_points(data_points)