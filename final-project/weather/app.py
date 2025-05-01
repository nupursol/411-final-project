from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from weather.models.user_model import db, User
from weather.models.weather_model import WeatherModel
from datetime import timedelta
import os
import logging
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///db/weather.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')  # Default to 'dev' only in development
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Initialize database and models
db = SQLAlchemy(app)
weather_model = WeatherModel(use_mock_data=os.environ.get('USE_MOCK_DATA', 'false').lower() == 'true')

# Create database tables
with app.app_context():
    db.create_all()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password are required"}), 400
            
        if User.query.filter_by(username=username).first():
            return jsonify({"status": "error", "message": "Username already exists"}), 400
            
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"status": "success"}), 201
    except Exception as e:
        logger.error(f"Error creating account: {str(e)}")
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
        
        weather_data = weather_model.add_city(city)
        return jsonify({"status": "success", "data": weather_data}), 201
    except Exception as e:
        logger.error(f"Error adding city: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/weather/<city>', methods=['GET'])
def get_weather_by_city(city):
    """Get current weather for a city."""
    try:
        weather_data = weather_model.get_city_weather(city)
        return jsonify({"status": "success", "data": weather_data}), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting weather: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/weather', methods=['GET'])
def get_weather_entries():
    """Get current weather for all cities."""
    try:
        weather_data = weather_model.get_all_weather()
        return jsonify({"status": "success", "data": weather_data}), 200
    except Exception as e:
        logger.error(f"Error getting all weather: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/weather/<city>', methods=['DELETE'])
def delete_weather_entry(city):
    """Remove a city."""
    try:
        weather_model.remove_city(city)
        return jsonify({"status": "success", "message": f"{city} removed"}), 200
    except ValueError as e:
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
