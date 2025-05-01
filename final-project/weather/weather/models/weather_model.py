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
        """ Add a city and retrieve its current weather data.
        Args:
            city (str): The name of the city to add.
        Returns:
            dict: Weather data for the added city including temperature, condition, etc.
        Raises:
            ValueError: If weather data cannot be retrieved or city is invalid."""
        try:
            city_lower = city.lower()
            logger.info(f"Adding city: {city_lower}")
            logger.info(f"Using mock data: {self.use_mock_data}")
            logger.info(f"Current weather data cities: {list(self.weather_data.keys())}")
            
            if self.use_mock_data:
                # Use mock data for testing
                if city_lower in self.mock_data:
                    weather_data = self.mock_data[city_lower]
                    self.weather_data[city_lower] = weather_data
                    logger.info(f"Added mock data for {city_lower}: {weather_data}")
                    return weather_data
                raise ValueError(f"Mock data not available for {city}")
            else:
                # Use real API for production
                weather_data = self.api_client.get_weather_data(city)
                self.weather_data[city_lower] = weather_data
                logger.info(f"Added API data for {city_lower}: {weather_data}")
                return weather_data
        except Exception as e:
            logger.error(f"Failed to add city: {str(e)}")
            raise ValueError(f"Could not get weather for {city}: {str(e)}")

    def get_city_weather(self, city: str) -> Dict:
        """Retrieve current weather data for a specific city.
        Args:
            city (str): The name of the city to get weather for.
        Returns:
            dict: Weather data including temperature, condition, and humidity.
        Raises:
            ValueError: If weather data is not available or API call fails."""
        city = city.lower()
        logger.info(f"Getting weather for city: {city}")
        logger.info(f"Using mock data: {self.use_mock_data}")
        logger.info(f"Mock data cities: {list(self.mock_data.keys())}")
        logger.info(f"Weather data cities: {list(self.weather_data.keys())}")
        logger.info(f"Mock data for {city}: {self.mock_data.get(city)}")
        logger.info(f"Weather data for {city}: {self.weather_data.get(city)}")
        
        # First check if we have the city in weather_data
        if city in self.weather_data:
            logger.info(f"Found city {city} in weather data")
            return self.weather_data[city]
            
        if self.use_mock_data:
            # If not in weather_data, check mock data
            if city in self.mock_data:
                logger.info(f"Found city {city} in mock data")
                return self.mock_data[city]
            logger.error(f"City {city} not found in mock data or weather data")
            raise ValueError(f"Mock data not available for {city}")
        else:
            # In production, try to get fresh data
            try:
                weather_data = self.api_client.get_weather_data(city)
                self.weather_data[city] = weather_data
                return weather_data
            except Exception as e:
                logger.error(f"Failed to get fresh weather for {city}: {str(e)}")
                raise ValueError(f"Could not get weather for {city}: {str(e)}")

    def get_all_cities(self) -> List[str]:
        """Get a list of all stored city names.
        Returns:
            list: A list of city names (str) currently stored in memory."""
        return list(self.weather_data.keys())

    def get_all_weather(self) -> List[Dict]:
        """Get current weather data for all stored cities.
        Returns:
            list: A list of weather data dictionaries for each stored city.
        Raises:
            ValueError: If API calls fail while refreshing weather data in production mode."""
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
        """Remove a city and its weather data from the model.
        Args:
            city (str): The name of the city to remove.
        Raises:
            ValueError: If the city is not found in stored weather data"""
        city = city.lower()
        logger.info(f"Removing city: {city}")
        logger.info(f"Current weather data cities: {list(self.weather_data.keys())}")
        
        if city not in self.weather_data:
            logger.error(f"City {city} not found in weather data")
            raise ValueError(f"{city} not found")
            
        logger.info(f"Removing city {city} from weather data")
        del self.weather_data[city]
        logger.info(f"Successfully removed city {city}")
