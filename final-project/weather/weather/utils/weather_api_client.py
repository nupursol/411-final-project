import requests
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class WeatherAPIClient:
    """Interacting with the OpenWeatherMap API.
    
    This class handles all communication with the OpenWeatherMap API,
    including fetching current weather data and handling API errors.
    """
    
    def __init__(self, api_key: str):
        """Initialize the Weather API client.
        
        Args:
            api_key (str): The OpenWeatherMap API key.
        """
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_current_weather(self, city: str) -> Dict:
        """Get current weather data for a city.
        
        Args:
            city (str): The name of the city to get weather for.
            
        Returns:
            Dict: A dictionary containing the weather data with the following structure:
                {
                    "city": str,
                    "temperature": float,  # in Celsius
                    "condition": str,
                    "humidity": int,  # percentage
                    "date_recorded": str  # ISO format timestamp
                }
                
        Raises:
            ValueError: If the city is not found or the API request fails.
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"  
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            weather_data = {
                "city": data["name"],
                "temperature": data["main"]["temp"],
                "condition": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "date_recorded": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Successfully fetched weather data for {city}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data for {city}: {str(e)}")
            raise ValueError(f"Failed to fetch weather data: {str(e)}")
            
    def get_forecast(self, city: str, days: int = 5) -> Dict:
        """Get weather forecast for a city.
        
        Args:
            city (str): The name of the city to get forecast for.
            days (int): Number of days to forecast (max 5).
            
        Returns:
            Dict: A dictionary containing the forecast data.
            
        Raises:
            ValueError: If the city is not found or the API request fails.
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8 
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            forecast = []
            for item in data["list"]:
                forecast.append({
                    "date": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "condition": item["weather"][0]["description"],
                    "humidity": item["main"]["humidity"]
                })
            
            logger.info(f"Successfully fetched {days}-day forecast for {city}")
            return {
                "city": data["city"]["name"],
                "forecast": forecast
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching forecast for {city}: {str(e)}")
            raise ValueError(f"Failed to fetch forecast: {str(e)}") 
