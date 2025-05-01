import requests
import logging
from datetime import datetime

class WeatherAPIClient:
    """Client for getting basic weather data from OpenWeather API."""
    
    API_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
    
    def get_weather_data(self, city):
        """
        Get current weather data for a city.
        
        Args:
            city (str): The name of the city to get weather for.
            
        Returns:
            dict: Weather data including temperature, condition, and humidity.
            
        Raises:
            ValueError: If the API request fails or returns invalid data.
        """
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"  # Use metric units for temperature
            }
            
            self.logger.info(f"Getting weather for city: {city}")
            response = requests.get(self.API_URL, params=params)
            
            if response.status_code != 200:
                self.logger.error(f"API request failed with status {response.status_code}: {response.text}")
                raise ValueError(f"Failed to get weather data: {response.text}")
            
            data = response.json()
            
            # Extract relevant weather data
            weather_data = {
                "city": data["name"],
                "temperature": data["main"]["temp"],
                "condition": data["weather"][0]["main"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "date_recorded": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Successfully got weather data for {city}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise ValueError(f"Failed to fetch weather data: {str(e)}")
        except (KeyError, IndexError) as e:
            self.logger.error(f"Invalid API response format: {str(e)}")
            raise ValueError(f"Invalid weather data format: {str(e)}")
