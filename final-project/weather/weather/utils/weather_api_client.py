import requests
import logging

logger = logging.getLogger(__name__)

class WeatherAPIClient:
    """
    A client for fetching weather data from the OpenWeatherMap API.
    """

    API_URL = "https://api.openweathermap.org/data/2.5/weather"
    API_KEY = "bb347d0180e29ce8b5a6fbd2d4fd2349"

    @staticmethod
    def get_weather_data(city: str) -> dict:
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
            "appid": WeatherAPIClient.API_KEY,
            "units": "metric"
        }

        try:
            response = requests.get(WeatherAPIClient.API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            temperature = data["main"]["temp"]
            condition = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]

            return {
                "temperature": temperature,
                "condition": condition,
                "humidity": humidity
            }

        except requests.RequestException as e:
            logger.error(f"Error fetching weather data for {city}: {e}")
            return None
        except (KeyError, TypeError) as e:
            logger.error(f"Malformed data received for {city}: {e}")
            return None
