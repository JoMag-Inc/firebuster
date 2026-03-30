from abc import ABC, abstractmethod


class WeatherRepository(ABC):
    @abstractmethod
    def get_by_location(self, longitude, latitude):
        pass

    @abstractmethod
    def add(self, weather_data):
        pass
