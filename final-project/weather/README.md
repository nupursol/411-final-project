# Weather API Application #
Completed by: Prashant Gangesar, Wesley Park, Nupur Solanki

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
5. Get all cities
    1. Path: /cities
    2. Request Type: GET
    3. Purpose: Retrieve a list of all cities currently stored.
    4. Request Format: None
    5. Response Format:

    ```json
    {
      "status": "success",
      "data": ["New York", "London"]
    }

    ```

    6. Example cURL:

    ```json
    curl http://localhost:5000/cities
    ```
6. Create Account
    1. Path: /create-account
    2. Request Type: POST
    3. Purpose: Register a new user account.
    4. Request Format (JSON body):
  
     ```json
    {
      "username": "alice",
      "password": "secret123"
    }

    ``` 
    5. Response Format:

    ```json
    {
      "status": "success"
    }


    ```

    6. Example cURL:

    ```json
    curl -X POST http://localhost:5000/create-account -H "Content-Type: application/json" -d '{"username": "alice", "password": "secret123"}'
    ```
7. Login
    1. Path: /login
    2. Request Type: POST
    3. Purpose: Authenticate a user and start a session.
    4. Request Format (JSON body):
  
     ```json
    {
      "username": "alice",
      "password": "secret123"
    }

    ``` 
    5. Response Format:

    ```json
    {
      "status": "success"
    }

    ```

    6. Example cURL:

    ```json
    curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d '{"username": "alice", "password": "secret123"}'
    ```
8. Logout
    1. Path: /logout
    2. Request Type: POST
    3. Purpose: Log out the current user and clear the session.
    4. Request Format: None
    5. Response Format:

    ```json
    {
      "status": "success"
    }

    ```

    6. Example cURL:

    ```json
    curl -X POST http://localhost:5000/logout
    ```
9. Update Password
    1. Path: /update-password
    2. Request Type: PUT
    3. Purpose: Change an existing user's password.
    4. Request Format (JSON body):
  
     ```json
    {
      "username": "alice",
      "old_password": "secret123",
      "new_password": "newpass456"
    }

    ``` 
    5. Response Format:

    ```json
    {
      "status": "success"
    }

    ```

    6. Example cURL:

    ```json
    curl -X PUT http://localhost:5000/update-password -H "Content-Type: application/json" -d '{"username": "alice", "old_password": "secret123", "new_password": "newpass456"}'
    ```
10. Delete Account
    1. Path: /delete-account
    2. Request Type: POST
    3. Purpose: Delete a user account.
    4. Request Format (JSON body):
  
     ```json
    {
      "username": "alice",
      "password": "secret123"
    }

    ``` 
    5. Response Format:

    ```json
    {
      "status": "success"
    }

    ```

    6. Example cURL:

    ```json
    curl -X POST http://localhost:5000/delete-account -H "Content-Type: application/json" -d '{"username": "alice", "password": "secret123"}'
    ```
11. Cleanup Database
    1. Path: /cleanup-db
    2. Request Type: POST
    3. Purpose: Drop and recreate all database tables (development use only).
    4. Request Format: None
    5. Response Format:

    ```json
    {
      "status": "success"
    }

    ```

    6. Example cURL:

    ```json
    curl -X POST http://localhost:5000/cleanup-db
    ```
12. Health Check
    1. Path: /healthcheck
    2. Request Type: GET
    3. Purpose: Check if the server is running.
    4. Request Format: None
    5. Response Format:

    ```json
    {
      "status": "success"
    }

    ```

    6. Example cURL:

    ```json
    curl http://localhost:5000/healthcheck
    ```
13. Database Check
    1. Path: /db-check
    2. Request Type: GET
    3. Purpose: Check if the database connection is working.
    4. Request Format: None
    5. Response Format:

    ```json
    {
      "status": "success"
    }

    ```

    6. Example cURL:

    ```json
    curl http://localhost:5000/db-check
    ```
