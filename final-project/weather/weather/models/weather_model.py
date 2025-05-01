from dataclasses import dataclass
import logging
import random
from typing import List
from datetime import datetime

from weather.utils.logger import configure_logger
from weather.utils.weather_api import WeatherAPIClient  

def get_random(n: int) -> int:
    """Returns a random number between 1 and n (inclusive)."""
    return random.randint(1, n)

logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class WeatherEntry:
    """
    A class to represent a weather entry.

    Attributes:
        id (int): The unique identifier for the weather entry.
        city (str): The city name.
        temperature (float): The temperature in Celsius.
        condition (str): The weather condition (e.g., "sunny", "rainy").
        humidity (int): The humidity percentage.
        date_recorded (str): The date when the weather was recorded in ISO format.
    """
    id: int
    city: str
    temperature: float
    condition: str
    humidity: int
    date_recorded: str

    def __post_init__(self):
        """Validates the weather entry data after initialization."""
        if not (0 <= self.humidity <= 100):
            raise ValueError(f"Humidity must be between 0 and 100, got {self.humidity}")
        if not self.date_recorded:
            raise ValueError("date_recorded cannot be empty")
        if not self.city.strip():
            raise ValueError("City cannot be empty")
        if not self.condition.strip():
            raise ValueError("Condition cannot be empty")

class WeatherModel:
    """
    A class to manage a collection of weather entries.

    Attributes:
        weather_entries (List[WeatherEntry]): The list of weather entries.
        current_id (int): The next available ID for new weather entries.
    """

    def __init__(self):
        """Initializes the WeatherModel with an empty list of weather entries."""
        self.weather_entries: List[WeatherEntry] = []
        self.current_id = 1

    ##################################################
    # Weather Entry Management Functions
    ##################################################

    def add_weather_entry(self, city: str) -> WeatherEntry:
        """Fetches weather data for the given city and adds a new weather entry.

        Args:
            city (str): The city name.

        Returns:
            WeatherEntry: The newly created weather entry.

        Raises:
            ValueError: If the weather data cannot be fetched.
        """
        logger.info(f"Fetching weather data for: {city}")

        # Fetch weather data from the API
        weather_data = WeatherAPIClient.get_weather_data(city)

        if not weather_data:
            raise ValueError(f"Unable to fetch weather data for {city}")

        temperature = weather_data["temperature"]
        condition = weather_data["condition"]
        humidity = weather_data["humidity"]

        weather_entry = WeatherEntry(
            id=self.current_id,
            city=city,
            temperature=temperature,
            condition=condition,
            humidity=humidity,
            date_recorded=datetime.now().isoformat()
        )

        self.weather_entries.append(weather_entry)
        self.current_id += 1
        return weather_entry

    def remove_weather_entry(self, weather_id: int) -> None:
        """Removes a weather entry by its ID.

        Args:
            weather_id (int): The ID of the weather entry to remove.

        Raises:
            ValueError: If no weather entry with the given ID exists.
        """
        logger.info(f"Removing weather entry with ID: {weather_id}")

        for i, entry in enumerate(self.weather_entries):
            if entry.id == weather_id:
                self.weather_entries.pop(i)
                return

        raise ValueError(f"No weather entry found with ID: {weather_id}")

    def get_all_weather_entries(self) -> List[WeatherEntry]:
        """Returns all weather entries.

        Returns:
            List[WeatherEntry]: A list of all weather entries.
        """
        logger.info("Getting all weather entries")
        return self.weather_entries

    def get_weather_entry_by_id(self, weather_id: int) -> WeatherEntry:
        """Returns a weather entry by its ID.

        Args:
            weather_id (int): The ID of the weather entry to retrieve.

        Returns:
            WeatherEntry: The weather entry with the given ID.

        Raises:
            ValueError: If no weather entry with the given ID exists.
        """
        logger.info(f"Getting weather entry with ID: {weather_id}")

        for entry in self.weather_entries:
            if entry.id == weather_id:
                return entry

        raise ValueError(f"No weather entry found with ID: {weather_id}")

    def update_weather_entry(self, weather_id: int, city: str = None, temperature: float = None,
                           condition: str = None, humidity: int = None) -> WeatherEntry:
        """Updates a weather entry with new values.

        Args:
            weather_id (int): The ID of the weather entry to update.
            city (str, optional): The new city name.
            temperature (float, optional): The new temperature.
            condition (str, optional): The new weather condition.
            humidity (int, optional): The new humidity percentage.

        Returns:
            WeatherEntry: The updated weather entry.

        Raises:
            ValueError: If no weather entry with the given ID exists or if any of the new values are invalid.
        """
        logger.info(f"Updating weather entry with ID: {weather_id}")

        for i, entry in enumerate(self.weather_entries):
            if entry.id == weather_id:
                if city is not None:
                    if not city.strip():
                        raise ValueError("City must be a non-empty string")
                    entry.city = city
                if temperature is not None:
                    if not isinstance(temperature, (int, float)):
                        raise ValueError("Temperature must be a number")
                    entry.temperature = temperature
                if condition is not None:
                    if not condition.strip():
                        raise ValueError("Condition must be a non-empty string")
                    entry.condition = condition
                if humidity is not None:
                    if not (0 <= humidity <= 100):
                        raise ValueError("Humidity must be between 0 and 100")
                    entry.humidity = humidity

                entry.date_recorded = datetime.now().isoformat()
                return entry

        raise ValueError(f"No weather entry found with ID: {weather_id}")

    def get_weather_entries_by_city(self, city: str) -> List[WeatherEntry]:
        """Returns all weather entries for a given city.

        Args:
            city (str): The city name to search for.

        Returns:
            List[WeatherEntry]: A list of weather entries for the given city.
        """
        logger.info(f"Getting weather entries for city: {city}")
        return [entry for entry in self.weather_entries if entry.city.lower() == city.lower()]

    def get_latest_weather_entry(self) -> WeatherEntry:
        """Returns the most recent weather entry.

        Returns:
            WeatherEntry: The most recent weather entry.

        Raises:
            ValueError: If there are no weather entries.
        """
        logger.info("Getting latest weather entry")

        if not self.weather_entries:
            raise ValueError("No weather entries available")

        return max(self.weather_entries, key=lambda x: x.date_recorded)

    def clear_all_entries(self) -> None:
        """Removes all weather entries."""
        logger.info("Clearing all weather entries")
        self.weather_entries = []
        self.current_id = 1

def create_weather_entry(city: str, temperature: float, condition: str, humidity: int, date_recorded: str) -> None:
    logger.info(f"Creating weather entry: {city}, {temperature}°C, {condition}, {humidity}%, {date_recorded}")
    if not city.strip():
        raise ValueError("City must be a non-empty string")
    if not condition.strip():
        raise ValueError("Condition must be a non-empty string")
    if not isinstance(temperature, (int, float)):
        raise ValueError("Temperature must be a number")
    if not (0 <= humidity <= 100):
        raise ValueError("Humidity must be between 0 and 100")
    if not date_recorded.strip():
        raise ValueError("Date must be provided")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO weather (city, temperature, condition, humidity, date_recorded)
                VALUES (?, ?, ?, ?, ?)
            """, (city, temperature, condition, humidity, date_recorded))
            conn.commit()
            logger.info("Weather entry added successfully.")
    except sqlite3.IntegrityError:
        logger.error("Duplicate weather entry")
        raise ValueError("Duplicate weather entry.")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise e

def delete_weather_entry(weather_id: int) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM weather WHERE id = ?", (weather_id,))
            if not cursor.fetchone():
                logger.warning(f"Weather entry ID {weather_id} not found.")
                raise ValueError(f"Weather entry ID {weather_id} not found.")
            cursor.execute("DELETE FROM weather WHERE id = ?", (weather_id,))
            conn.commit()
            logger.info(f"Deleted weather entry ID {weather_id}.")
    except sqlite3.Error as e:
        logger.error(f"Error deleting weather entry: {e}")
        raise e

def get_weather_by_id(weather_id: int) -> WeatherEntry:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, city, temperature, condition, humidity, date_recorded
                FROM weather
                WHERE id = ?
            """, (weather_id,))
            row = cursor.fetchone()
            if row:
                return WeatherEntry(*row)
            else:
                raise ValueError(f"Weather entry ID {weather_id} not found.")
    except sqlite3.Error as e:
        logger.error(f"Error retrieving weather by ID: {e}")
        raise e

def get_all_weather_entries() -> list[dict]:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, city, temperature, condition, humidity, date_recorded
                FROM weather
                ORDER BY date_recorded DESC
            """)
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "city": row[1],
                    "temperature": row[2],
                    "condition": row[3],
                    "humidity": row[4],
                    "date_recorded": row[5],
                }
                for row in rows
            ]
    except sqlite3.Error as e:
        logger.error(f"Error retrieving weather entries: {e}")
        raise e

def get_random_weather_entry() -> WeatherEntry:
    try:
        entries = get_all_weather_entries()
        if not entries:
            raise ValueError("No weather data available")
        index = get_random(len(entries))
        selected = entries[index - 1]
        return WeatherEntry(
            id=selected["id"],
            city=selected["city"],
            temperature=selected["temperature"],
            condition=selected["condition"],
            humidity=selected["humidity"],
            date_recorded=selected["date_recorded"]
        )
    except Exception as e:
        logger.error(f"Error retrieving random weather entry: {e}")
        raise e
