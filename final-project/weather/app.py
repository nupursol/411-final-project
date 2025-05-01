from flask import Flask, request, jsonify, session
from datetime import timedelta
import os
import logging
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///../db/weather.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev') 
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

from weather.models.user_model import db
db.init_app(app)

from weather.models.user_model import User
from weather.models.weather_model import WeatherModel

weather_model = WeatherModel(use_mock_data=os.environ.get('USE_MOCK_DATA', 'false').lower() == 'true')

with app.app_context():
    db.create_all()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

weather_logger = logging.getLogger('weather.models.weather_model')
weather_logger.setLevel(logging.INFO)
weather_logger.addHandler(handler)

##################################################
# Authentication Routes
##################################################

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """Health check route."""
    return jsonify({"status": "success"}), 200

@app.route('/db-check', methods=['GET'])
def db_check():
    """Database check route."""
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/create-account', methods=['POST'])
def create_account():
    """Create a new user account."""
    try:
        data = request.get_json()
        logger.info(f"Received create account request with data: {data}")
        
        if not data:
            logger.error("No JSON data received")
            return jsonify({"status": "error", "message": "No data received"}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        logger.info(f"Extracted username: {username}, password: {'*' * len(password) if password else 'None'}")
        
        if not username or not password:
            logger.error(f"Missing username or password. Username: {username}, Password: {'*' * len(password) if password else 'None'}")
            return jsonify({"status": "error", "message": "Username and password are required"}), 400
            
        logger.info(f"Checking if user {username} exists")
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            logger.error(f"User {username} already exists with id {existing_user.id}")
            return jsonify({"status": "error", "message": "Username already exists"}), 400
            
        logger.info(f"Creating new user {username}")
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        logger.info("Attempting to commit to database")
        db.session.commit()
        logger.info(f"Successfully created user {username}")
        return jsonify({"status": "success"}), 201
    except Exception as e:
        logger.error(f"Error creating account: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """Login a user."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password are required"}), 400
            
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({"status": "error", "message": "Invalid username or password"}), 401
            
        session.permanent = True
        session['user_id'] = user.id
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """Log out the current user."""
    session.pop('user_id', None)
    return jsonify({"status": "success"}), 200

@app.route('/update-password', methods=['PUT'])
def update_password():
    """Update a user's password."""
    try:
        data = request.get_json()
        username = data.get('username')
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not all([username, old_password, new_password]):
            return jsonify({"status": "error", "message": "All fields are required"}), 400
            
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(old_password):
            return jsonify({"status": "error", "message": "Invalid username or password"}), 401
            
        user.set_password(new_password)
        db.session.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Error updating password: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete-account', methods=['POST'])
def delete_account():
    """Delete a user account."""
    try:
        data = request.get_json()
        logger.info(f"Received delete account request with data: {data}")
        
        if not data:
            logger.error("No JSON data received")
            return jsonify({"status": "error", "message": "No data received"}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            logger.error(f"Missing username or password. Username: {username}, Password: {'*' * len(password) if password else 'None'}")
            return jsonify({"status": "error", "message": "Username and password are required"}), 400
            
        logger.info(f"Checking if user {username} exists")
        user = User.query.filter_by(username=username).first()
        if not user:
            logger.error(f"User {username} does not exist")
            return jsonify({"status": "error", "message": "User does not exist"}), 404
            
        if not user.check_password(password):
            logger.error(f"Invalid password for user {username}")
            return jsonify({"status": "error", "message": "Invalid password"}), 401
            
        logger.info(f"Deleting user {username}")
        db.session.delete(user)
        db.session.commit()
        logger.info(f"Successfully deleted user {username}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/cleanup-db', methods=['POST'])
def cleanup_db():
    """Clean up the database by dropping all tables and recreating them."""
    try:
        logger.info("Cleaning up database...")
        db.drop_all()
        db.create_all()
        logger.info("Database cleaned up successfully")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Error cleaning up database: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

##################################################
# Weather Routes
##################################################

@app.route('/weather', methods=['POST'])
def add_weather_entry():
    """Add a city and get its current weather."""
    try:
        data = request.get_json()
        city = data.get('city')
        if not city:
            return jsonify({"status": "error", "message": "City name is required"}), 400
        
        logger.info(f"Adding weather entry for city: {city}")
        weather_data = weather_model.add_city(city)
        logger.info(f"Successfully added weather data: {weather_data}")
        return jsonify({"status": "success", "data": weather_data}), 201
    except Exception as e:
        logger.error(f"Error adding city: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/weather/<city>', methods=['GET'])
def get_weather_by_city(city):
    """Get current weather for a city."""
    try:
        logger.info(f"Getting weather for city: {city}")
        weather_data = weather_model.get_city_weather(city)
        logger.info(f"Successfully retrieved weather data: {weather_data}")
        return jsonify({"status": "success", "data": weather_data}), 200
    except ValueError as e:
        logger.error(f"City not found: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting weather: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/weather', methods=['GET'])
def get_weather_entries():
    """Get current weather for all cities."""
    try:
        logger.info("Getting all weather entries")
        weather_data = weather_model.get_all_weather()
        logger.info(f"Successfully retrieved all weather data: {weather_data}")
        return jsonify({"status": "success", "data": weather_data}), 200
    except Exception as e:
        logger.error(f"Error getting all weather: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/weather/<city>', methods=['DELETE'])
def delete_weather_entry(city):
    """Remove a city."""
    try:
        logger.info(f"Deleting weather entry for city: {city}")
        weather_model.remove_city(city)
        logger.info(f"Successfully deleted weather entry for {city}")
        return jsonify({"status": "success", "message": f"{city} removed"}), 200
    except ValueError as e:
        logger.error(f"City not found: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error removing city: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/cities', methods=['GET'])
def get_cities():
    """Get list of all cities."""
    try:
        cities = weather_model.get_all_cities()
        return jsonify({"status": "success", "data": cities}), 200
    except Exception as e:
        logger.error(f"Error getting cities: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
