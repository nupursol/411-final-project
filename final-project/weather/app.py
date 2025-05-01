from flask import Flask, request, jsonify, session, make_response
from flask_sqlalchemy import SQLAlchemy
from models.user_model import db, User
from models.weather_model import WeatherModel, WeatherEntry
from datetime import timedelta
import os
import logging

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Initialize database and weather model
db.init_app(app)
weather_model = WeatherModel()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

##################################################
# Authentication Routes
##################################################

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """Health check route to verify the service is running."""
    logger.info("Health check endpoint hit")
    return jsonify({"status": "ok"}), 200

@app.route('/create-account', methods=['POST'])
def create_account():
    """Create a new user account."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Account created"}), 201

@app.route('/login', methods=['POST'])
def login():
    """Log in a user and create a session."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required."}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password."}), 401

    session.permanent = True
    session['user_id'] = user.id
    return jsonify({"message": "Logged in successfully."}), 200


@app.route('/logout', methods=['POST'])
def logout():
    """Log out the current user."""
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully."}), 200


@app.route('/update-password', methods=['PUT'])
def update_password():
    """Update the current user's password."""
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in."}), 401

    data = request.get_json()
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"error": "Current and new password required."}), 400

    user = User.query.get(session['user_id'])
    if not user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect."}), 401

    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Password updated successfully."}), 200

##################################################
# Weather Routes
##################################################

@app.route('/weather', methods=['GET'])
def list_weather_entries():
    """Get all weather entries.
    
    Returns:
        JSON: List of weather entries with their details.
    """
    logger.info("Getting all weather entries")
    try:
        entries = weather_model.get_all_weather_entries()
        return jsonify([{
            "id": entry.id,
            "city": entry.city,
            "temperature": entry.temperature,
            "condition": entry.condition,
            "humidity": entry.humidity,
            "date_recorded": entry.date_recorded
        } for entry in entries]), 200
    except Exception as e:
        logger.error(f"Error getting weather entries: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/weather/<int:weather_id>', methods=['GET'])
def get_weather(weather_id):
    """Get a specific weather entry by ID.
    
    Args:
        weather_id (int): The ID of the weather entry to retrieve.
        
    Returns:
        JSON: Weather entry details.
    """
    logger.info(f"Getting weather entry with ID: {weather_id}")
    try:
        entry = weather_model.get_weather_entry_by_id(weather_id)
        return jsonify({
            "id": entry.id,
            "city": entry.city,
            "temperature": entry.temperature,
            "condition": entry.condition,
            "humidity": entry.humidity,
            "date_recorded": entry.date_recorded
        }), 200
    except ValueError as e:
        logger.error(f"Error getting weather entry: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting weather entry: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/weather', methods=['POST'])
def add_weather_entry():
    """Add a new weather entry.
    
    Returns:
        JSON: The newly created weather entry details.
    """
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in."}), 401

    data = request.get_json()
    try:
        entry = weather_model.add_weather_entry(
            city=data.get("city"),
            temperature=data.get("temperature"),
            condition=data.get("condition"),
            humidity=data.get("humidity")
        )
        return jsonify({
            "id": entry.id,
            "city": entry.city,
            "temperature": entry.temperature,
            "condition": entry.condition,
            "humidity": entry.humidity,
            "date_recorded": entry.date_recorded
        }), 201
    except ValueError as e:
        logger.error(f"Error adding weather entry: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding weather entry: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/weather/<int:weather_id>', methods=['PUT'])
def update_weather(weather_id):
    """Update an existing weather entry.
    
    Args:
        weather_id (int): The ID of the weather entry to update.
        
    Returns:
        JSON: The updated weather entry details.
    """
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in."}), 401

    data = request.get_json()
    try:
        entry = weather_model.update_weather_entry(
            weather_id=weather_id,
            city=data.get("city"),
            temperature=data.get("temperature"),
            condition=data.get("condition"),
            humidity=data.get("humidity")
        )
        return jsonify({
            "id": entry.id,
            "city": entry.city,
            "temperature": entry.temperature,
            "condition": entry.condition,
            "humidity": entry.humidity,
            "date_recorded": entry.date_recorded
        }), 200
    except ValueError as e:
        logger.error(f"Error updating weather entry: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error updating weather entry: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/weather/<int:weather_id>', methods=['DELETE'])
def delete_weather(weather_id):
    """Delete a weather entry.
    
    Args:
        weather_id (int): The ID of the weather entry to delete.
        
    Returns:
        JSON: Success message.
    """
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in."}), 401

    try:
        weather_model.remove_weather_entry(weather_id)
        return jsonify({"message": "Weather entry deleted successfully."}), 200
    except ValueError as e:
        logger.error(f"Error deleting weather entry: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting weather entry: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/weather/city/<string:city>', methods=['GET'])
def get_weather_by_city(city):
    """Get all weather entries for a specific city.
    
    Args:
        city (str): The city name to search for.
        
    Returns:
        JSON: List of weather entries for the specified city.
    """
    logger.info(f"Getting weather entries for city: {city}")
    try:
        entries = weather_model.get_weather_entries_by_city(city)
        return jsonify([{
            "id": entry.id,
            "city": entry.city,
            "temperature": entry.temperature,
            "condition": entry.condition,
            "humidity": entry.humidity,
            "date_recorded": entry.date_recorded
        } for entry in entries]), 200
    except Exception as e:
        logger.error(f"Error getting weather entries by city: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/weather/latest', methods=['GET'])
def get_latest_weather():
    """Get the most recent weather entry.
    
    Returns:
        JSON: The most recent weather entry details.
    """
    logger.info("Getting latest weather entry")
    try:
        entry = weather_model.get_latest_weather_entry()
        return jsonify({
            "id": entry.id,
            "city": entry.city,
            "temperature": entry.temperature,
            "condition": entry.condition,
            "humidity": entry.humidity,
            "date_recorded": entry.date_recorded
        }), 200
    except ValueError as e:
        logger.error(f"Error getting latest weather entry: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting latest weather entry: {e}")
        return jsonify({"error": str(e)}), 500


@app.before_first_request
def create_tables():
    """Create database tables if they don't exist."""
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
