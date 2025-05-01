from flask import Flask, request, jsonify, session, make_response
from flask_sqlalchemy import SQLAlchemy
from weather.models.user_model import db, User
from weather.models.weather_model import WeatherModel, WeatherEntry
from datetime import timedelta
import os
import logging
from sqlalchemy import text

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///db/weather.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Initialize database and weather model
db.init_app(app)
weather_model = WeatherModel()

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
    """Health check route to verify the service is running."""
    logger.info("Health check endpoint hit")
    return jsonify({"status": "success"}), 200

@app.route('/db-check', methods=['GET'])
def db_check():
    """Database check route to verify the database connection."""
    try:
        # Try to query the database using proper SQLAlchemy text()
        db.session.execute(text('SELECT 1'))
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/create-account', methods=['POST'])
def create_account():
    """Create a new user account."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "Username already exists"}), 400
    
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"status": "success", "message": "Account created"}), 201

@app.route('/login', methods=['POST'])
def login():
    """Log in a user and create a session."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401

    session.permanent = True
    session['user_id'] = user.id
    return jsonify({"status": "success", "message": "Logged in successfully"}), 200

@app.route('/logout', methods=['POST'])
def logout():
    """Log out the current user."""
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully."}), 200

@app.route('/update-password', methods=['PUT'])
def update_password():
    """Update a user's password."""
    data = request.get_json()
    username = data.get("username")
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not all([username, old_password, new_password]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(old_password):
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401

    user.set_password(new_password)
    db.session.commit()
    return jsonify({"status": "success", "message": "Password updated"}), 200

##################################################
# Weather Routes
##################################################

@app.route('/weather', methods=['GET'])
def get_weather_entries():
    """Get all weather entries."""
    try:
        entries = weather_model.get_all_weather_entries()
        return jsonify({
            "status": "success",
            "data": [{
                "id": entry.id,
                "city": entry.city,
                "temperature": entry.temperature,
                "condition": entry.condition,
                "humidity": entry.humidity,
                "date_recorded": entry.date_recorded
            } for entry in entries]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/weather/<string:city>', methods=['GET'])
def get_weather_by_city(city):
    """Get weather for a specific city."""
    try:
        entries = weather_model.get_weather_entries_by_city(city)
        if not entries:
            return jsonify({"status": "error", "message": "City not found"}), 404
        
        return jsonify({
            "status": "success",
            "data": [{
                "id": entry.id,
                "city": entry.city,
                "temperature": entry.temperature,
                "condition": entry.condition,
                "humidity": entry.humidity,
                "date_recorded": entry.date_recorded
            } for entry in entries]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/weather', methods=['POST'])
def add_weather_entry():
    """Add a new weather entry."""
    data = request.get_json()
    try:
        entry = weather_model.add_weather_entry(
            city=data.get("city"),
            temperature=data.get("temperature"),
            condition=data.get("condition"),
            humidity=data.get("humidity")
        )
        return jsonify({
            "status": "success",
            "data": {
                "id": entry.id,
                "city": entry.city,
                "temperature": entry.temperature,
                "condition": entry.condition,
                "humidity": entry.humidity,
                "date_recorded": entry.date_recorded
            }
        }), 201
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/weather/<string:city>', methods=['DELETE'])
def delete_weather_entry(city):
    """Delete weather entries for a city."""
    try:
        weather_model.remove_weather_entries_by_city(city)
        return jsonify({"status": "success", "message": "Weather entries deleted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
