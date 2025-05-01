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
    
2. Number 2
2. 
