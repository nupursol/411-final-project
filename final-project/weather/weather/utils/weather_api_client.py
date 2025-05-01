import requests
import logging
from datetime import datetime
from weather.models.weather_model import WeatherEntry

logger = logging.getLogger(__name__)

class WeatherAPIClient:
    """
    A client for fetching weather data from the OpenWeatherMap API.
    """

    API_URL = "https://api.openweathermap.org/data/2.5/weather"
    API_KEY = "bb347d0180e29ce8b5a6fbd2d4fd2349"

    @classmethod
    def get_weather_data(cls, city: str) -> WeatherEntry:
        """
        Fetches current weather data for the specified city.

        Args:
            city (str): The name of the city.

        Returns:
            dict: A dictionary containing temperature, condition, and humidity.

        Raises:
            ValueError: If the API request fails or returns invalid data.
        """
        params = {
            "q": city,
            "appid": cls.API_KEY,
            "units": "metric"
        }

        response = requests.get(cls.BASE_URL, params=params)

        if response.status_code != 200:
            logger.error(f"Failed to fetch weather data: {response.text}")
            raise ValueError(f"Could not fetch weather data for city: {city}")

        data = response.json()
        logger.debug(f"Weather API response: {data}")

        return WeatherEntry(
            id=0,  
            city=data["name"],
            temperature=data["main"]["temp"],
            condition=data["weather"][0]["main"],
            humidity=data["main"]["humidity"],
            date_recorded=str(datetime.utcnow().date())
        )
