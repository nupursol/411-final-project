import pytest
from weather.models.weather_model import WeatherModel

@pytest.fixture
def model():
    """
    Create a WeatherModel instance with mock data enabled.

    Returns:
        WeatherModel: A model instance using mock data for predictable tests.
    """
    return WeatherModel(use_mock_data=True)

def test_add_city_mock(model):
    """
    Test adding a city using mock data returns valid weather info.
    """
    data = model.add_city("New York")
    assert data["city"] == "New York"
    assert "temperature" in data

def test_get_city_weather(model):
    """
    Test retrieving weather for an added city using mock data.
    """
    model.add_city("London")
    data = model.get_city_weather("London")
    assert data["condition"] == "Rain"

def test_get_all_cities(model):
    """
    Test retrieving all added cities returns correct list.
    """
    model.add_city("New York")
    model.add_city("London")
    cities = model.get_all_cities()
    assert set(cities) == {"new york", "london"}

def test_get_all_weather(model):
    """
    Test retrieving weather for all added cities returns expected results.
    """
    model.add_city("New York")
    model.add_city("London")
    all_weather = model.get_all_weather()
    assert len(all_weather) == 2
    assert any(w["city"] == "New York" for w in all_weather)

def test_remove_city(model):
    """
    Test removing an existing city works correctly.
    """
    model.add_city("London")
    model.remove_city("London")
    assert "london" not in model.get_all_cities()

def test_remove_nonexistent_city(model):
    """
    Test removing a city that doesn't exist raises ValueError.
    """
    with pytest.raises(ValueError, match="not found"):
        model.remove_city("FakeCity")

def test_city_not_in_mock_data(model):
    """
    Test adding a city not present in mock data raises ValueError.
    """
    with pytest.raises(ValueError, match="Mock data not available"):
        model.add_city("Tokyo")