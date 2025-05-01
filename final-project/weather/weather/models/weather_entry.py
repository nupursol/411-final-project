from dataclasses import dataclass
from datetime import datetime

@dataclass
class WeatherEntry:
    """A simple data class to store weather information."""
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