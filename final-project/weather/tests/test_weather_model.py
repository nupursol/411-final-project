import pytest
from weather.models.weather_model import WeatherModel, WeatherEntry 

@pytest.fixture()
def weather_model():
    """Provides a fresh instance of WeatherModel for each test."""
    return WeatherModel()

@pytest.fixture
def sample_weather_entry1():
    return WeatherEntry(id=1, city="SomeCity", temperature=22.5, condition="Sunny", humidity=50, date_recorded="2025-04-30")

@pytest.fixture
def sample_weather_entry2():
    return WeatherEntry(id=2, city="SomeCity2", temperature=18.0, condition="Rainy", humidity=30, date_recorded="2025-05-01")

@pytest.fixture
def sample_weather_list(sample_weather_entry1, sample_weather_entry2):
    return [sample_weather_entry1, sample_weather_entry2]

##################################################
# Add / Remove Test Cases
##################################################

def test_add_weather_entry(weather_model, sample_weather_entry1):
    weather_model.add_entry(sample_weather_entry1)
    assert len(weather_model.entries) == 1
    assert weather_model.entries[0].condition == "Sunny"

def test_add_duplicate_entry(weather_model, sample_weather_entry1):
    weather_model.add_entry(sample_weather_entry1)
    with pytest.raises(ValueError, match="Entry for 2025-04-30 already exists"):
        weather_model.add_entry(sample_weather_entry1)

def test_remove_entry_by_date(weather_model, sample_weather_list):
    for entry in sample_weather_list:
        weather_model.add_entry(entry)
    weather_model.remove_entry_by_date("2025-04-30")
    assert len(weather_model.entries) == 1
    assert weather_model.entries[0].date_recorded == "2025-05-01"

def test_clear_weather_data(weather_model, sample_weather_entry1):
    weather_model.add_entry(sample_weather_entry1)
    weather_model.clear_entries()
    assert len(weather_model.entries) == 0

##################################################
# Retrieval Test Cases
##################################################

def test_get_entry_by_date(weather_model, sample_weather_entry1):
    weather_model.add_entry(sample_weather_entry1)
    entry = weather_model.get_entry_by_date("2025-04-30")
    assert entry.temperature == 22.5

def test_get_all_entries(weather_model, sample_weather_list):
    for entry in sample_weather_list:
        weather_model.add_entry(entry)
    entries = weather_model.get_all_entries()
    assert len(entries) == 2

def test_entry_not_found(weather_model):
    with pytest.raises(ValueError, match="No entry found for 2025-04-30"):
        weather_model.get_entry_by_date("2025-04-30")

##################################################
# Validation and Utility Tests
##################################################

def test_check_if_empty(weather_model):
    with pytest.raises(ValueError, match="Weather data is empty"):
        weather_model.check_if_empty()

def test_not_empty_check(weather_model, sample_weather_entry1):
    weather_model.add_entry(sample_weather_entry1)
    try:
        weather_model.check_if_empty()
    except ValueError:
        pytest.fail("Raised ValueError unexpectedly")

def test_update_weather_entry(weather_model, sample_weather_entry1):
    weather_model.add_entry(sample_weather_entry1)
    updated = WeatherEntry(id=1, city="SomeCity", temperature=22.5, condition="Sunny", humidity=50, date_recorded="2025-04-30")
    weather_model.update_entry("2025-04-30", updated)
    assert weather_model.get_entry_by_date("2025-04-30").temperature == 25.0
