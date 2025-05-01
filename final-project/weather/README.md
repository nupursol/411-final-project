# Weather API Application #

### Overview ###
This application provides a simple RESTful API for retrieving, storing, and managing weather data for various cities. It supports mock data for testing and integrates with the OpenWeatherMap API for real-time weather data in production mode.

### API Routes ###
1. Add a City
    1. Path: /weather
    2. Request Type: POST
    3. Purpose: Add a city and fetch its current weather.
    4. Request Format (JSON body):
  
     ```json
    {
      "city": "New York"
    }
    ``` 
   5. Response Format:

    ```json
    {
      "city": "New York",
      "temperature": 20.5,
      "condition": "Clouds",
      "humidity": 65,
      "wind_speed": 3.2,
      "date_recorded": "2025-05-01T15:23:10.123456"
    }
    ```

    6. Example cURL:

    ```json
    curl -X POST http://localhost:5000/weather -H "Content-Type: application/json" -d '{"city": "New York"}'
    ```
    
2. Get Weather for a City
    1. Path: /weather/<city>
    2. Request Type: GET
    3. Purpose: Retrieve weather data for a specific city.
    4. Request Format: URL path parameter
    5. Response Format:

    ```json
    {
      "city": "London",
      "temperature": 15.8,
      "condition": "Rain",
      "humidity": 75,
      "wind_speed": 4.1,
      "date_recorded": "2025-05-01T15:24:15.123456"
    }
    ```

    6. Example cURL:

    ```json
    curl http://localhost:5000/weather/London
    ```
3. Get All Weather Entries
    1. Path: /weather
    2. Request Type: GET
    3. Purpose: Retrieve weather data for all stored cities.
    4. Request Format: None
    5. Response Format:

    ```json
    [
      {
        "city": "New York",
        "temperature": 20.5,
        "condition": "Clouds",
        "humidity": 65,
        "wind_speed": 3.2,
        "date_recorded": "2025-05-01T15:23:10.123456"
      },
      {
        "city": "London",
        "temperature": 15.8,
        "condition": "Rain",
        "humidity": 75,
        "wind_speed": 4.1,
        "date_recorded": "2025-05-01T15:24:15.123456"
      }
    ]

    ```

    6. Example cURL:

    ```json
    curl http://localhost:5000/weather
    ```
4. Remove a City
    1. Path: /weather/<city>
    2. Request Type: DELETE
    3. Purpose: Remove a city and its weather data from storage.
    4. Request Format: URL path parameter
    5. Response Format:

    ```json
    {
      "message": "City london removed successfully"
    }

    ```

    6. Example cURL:

    ```json
    curl -X DELETE http://localhost:5000/weather/London
    ```

