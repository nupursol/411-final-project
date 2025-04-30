from dataclasses import dataclass
import logging
import sqlite3
from weather.utils.logger import configure_logger
from weather.utils.api_utils import get_random
from weather.utils.sql_utils import get_db_connection

logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class Weather:
    id: int
    city: str
    temperature: float  # in Celsius
    condition: str
    humidity: int  # percentage
    date_recorded: str  # ISO format

    def __post_init__(self):
        if not (0 <= self.humidity <= 100):
            raise ValueError(f"Humidity must be between 0 and 100, got {self.humidity}")
        if not self.date_recorded:
            raise ValueError("date_recorded cannot be empty")
        if not self.city.strip():
            raise ValueError("City cannot be empty")
        if not self.condition.strip():
            raise ValueError("Condition cannot be empty")

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

def get_weather_by_id(weather_id: int) -> Weather:
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
                return Weather(*row)
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

def get_random_weather_entry() -> Weather:
    try:
        entries = get_all_weather_entries()
        if not entries:
            raise ValueError("No weather data available")
        index = get_random(len(entries))
        selected = entries[index - 1]
        return Weather(
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
