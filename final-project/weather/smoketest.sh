#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/healthcheck" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##########################################################
#
# User Management
#
##########################################################

create_user() {
  username=$1
  password=$2

  echo "Creating user ($username)..."
  response=$(curl -s -X POST "$BASE_URL/create-account" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"password\":\"$password\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "User created successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "User JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to create user."
    exit 1
  fi
}

login_user() {
  username=$1
  password=$2

  echo "Logging in user ($username)..."
  response=$(curl -s -X POST "$BASE_URL/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"password\":\"$password\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "User logged in successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Login JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to login user."
    exit 1
  fi
}

update_password() {
  username=$1
  old_password=$2
  new_password=$3

  echo "Updating password for user ($username)..."
  response=$(curl -s -X PUT "$BASE_URL/update-password" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"old_password\":\"$old_password\", \"new_password\":\"$new_password\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Password updated successfully."
  else
    echo "Failed to update password."
    exit 1
  fi
}

##########################################################
#
# Weather Management
#
##########################################################

add_weather_entry() {
  city=$1
  temperature=$2
  condition=$3
  humidity=$4

  echo "Adding weather entry for $city..."
  response=$(curl -s -X POST "$BASE_URL/weather" \
    -H "Content-Type: application/json" \
    -d "{\"city\":\"$city\", \"temperature\":$temperature, \"condition\":\"$condition\", \"humidity\":$humidity}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Weather entry added successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Weather JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add weather entry."
    exit 1
  fi
}

get_weather_entries() {
  echo "Getting all weather entries..."
  response=$(curl -s -X GET "$BASE_URL/weather")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Weather entries retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Weather JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get weather entries."
    exit 1
  fi
}

get_weather_by_city() {
  city=$1

  echo "Getting weather for $city..."
  response=$(curl -s -X GET "$BASE_URL/weather/$city")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Weather retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Weather JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get weather."
    exit 1
  fi
}

delete_weather_entry() {
  city=$1

  echo "Deleting weather entry for $city..."
  response=$(curl -s -X DELETE "$BASE_URL/weather/$city")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Weather entry deleted successfully."
  else
    echo "Failed to delete weather entry."
    exit 1
  fi
}

# Main test sequence
echo "Starting smoke test for Weather Application..."

# Health checks
check_health
check_db

# User management tests
create_user "testuser" "testpass"
login_user "testuser" "testpass"
update_password "testuser" "testpass" "newpass"
login_user "testuser" "newpass"

# Weather entry tests
add_weather_entry "New York" 20 "sunny" 50
add_weather_entry "London" 15 "cloudy" 60
get_weather_entries
get_weather_by_city "New York"
delete_weather_entry "New York"
get_weather_entries

echo "All smoke tests passed successfully!"
