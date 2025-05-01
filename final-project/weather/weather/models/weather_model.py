import logging
from typing import Dict, List
from datetime import datetime
import os

from weather.utils.weather_api_client import WeatherAPIClient

logger = logging.getLogger(__name__)

class WeatherModel:
    """Simple in-memory model for storing weather data."""
    
    def __init__(self, use_mock_data=False):
        self.api_client = WeatherAPIClient(os.environ.get("OPENWEATHER_API_KEY"))
        self.weather_data: Dict[str, Dict] = {}  # city -> weather data
        self.use_mock_data = use_mock_data
        self.mock_data = {
            "new york": {
                "city": "New York",
                "temperature": 20.5,
                "condition": "Clouds",
                "humidity": 65,
                "wind_speed": 3.2,
                "date_recorded": datetime.utcnow().isoformat()
            },
            "london": {
                "city": "London",
                "temperature": 15.8,
                "condition": "Rain",
                "humidity": 75,
                "wind_speed": 4.1,
                "date_recorded": datetime.utcnow().isoformat()
            }
        }
    
    def add_city(self, city: str) -> Dict:
        """Add a city and get its current weather."""
        try:
            if self.use_mock_data:
                # Use mock data for testing
                city_lower = city.lower()
                if city_lower in self.mock_data:
                    weather_data = self.mock_data[city_lower]
                    self.weather_data[city_lower] = weather_data
                    return weather_data
                raise ValueError(f"Mock data not available for {city}")
            else:
                # Use real API for production
                weather_data = self.api_client.get_weather_data(city)
                self.weather_data[city.lower()] = weather_data
                return weather_data
        except Exception as e:
            logger.error(f"Failed to add city: {str(e)}")
            raise ValueError(f"Could not get weather for {city}: {str(e)}")
    
    def get_city_weather(self, city: str) -> Dict:
        """Get current weather for a city."""
        city = city.lower()
        if city in self.weather_data:
            if self.use_mock_data:
                return self.weather_data[city]
            else:
                # In production, always get fresh data
                try:
                    weather_data = self.api_client.get_weather_data(city)
                    self.weather_data[city] = weather_data
                    return weather_data
                except Exception as e:
                    logger.error(f"Failed to get fresh weather for {city}: {str(e)}")
                    # Fall back to cached data if API call fails
                    return self.weather_data[city]
        raise ValueError(f"{city} not found")
    
    def get_all_cities(self) -> List[str]:
        """Get list of all cities."""
        return list(self.weather_data.keys())
    
    def get_all_weather(self) -> List[Dict]:
        """Get current weather for all cities."""
        if self.use_mock_data:
            return list(self.weather_data.values())
        else:
            # In production, get fresh data for all cities
            results = []
            for city in self.weather_data.keys():
                try:
                    weather_data = self.get_city_weather(city)
                    results.append(weather_data)
                except Exception as e:
                    logger.error(f"Failed to get weather for {city}: {str(e)}")
                    continue
            return results
    
    def remove_city(self, city: str) -> None:
        """Remove a city."""
        city = city.lower()
        if city not in self.weather_data:
            raise ValueError(f"{city} not found")
        del self.weather_data[city]
