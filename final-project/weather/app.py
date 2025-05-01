from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from models.user_model import db, User
from models.weather_model import WeatherModel
from datetime import timedelta
import os

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# Initialize DB and model
db.init_app(app)
weather_model = WeatherModel()

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """
    Healthcheck endpoint.

    Returns:
        JSON: A status message confirming the app is running.
    """
    return jsonify({"status": "ok"}), 200

@app.route('/create-account', methods=['POST'])
def create_account():
    """
    Creates a new user account with a hashed password.

    Expects:
        JSON: { "username": str, "password": str }

    Returns:
        JSON: Success or error message.
    """
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
    """
    Logs a user in by validating credentials.

    Expects:
        JSON: { "username": str, "password": str }

    Returns:
        JSON: Success or error message.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    session['username'] = username
    session.permanent = True
    return jsonify({"message": "Logged in"})

@app.route('/logout', methods=['POST'])
def logout():
    """
    Logs the current user out by clearing the session.

    Returns:
        JSON: Confirmation message.
    """
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route('/update-password', methods=['PUT'])
def update_password():
    """
    Updates the password for the currently logged-in user.

    Expects:
        JSON: { "new_password": str }

    Returns:
        JSON: Success or error message.
    """
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    data = request.get_json()
    new_password = data.get("new_password")
    user = User.query.filter_by(username=session['username']).first()
    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Password updated"})

@app.route('/weather', methods=['POST'])
def add_weather():
    """
    Adds a new weather entry to the in-memory model.

    Expects:
        JSON: { "city": str, "temperature": float, "condition": str, "humidity": int }

    Returns:
        JSON: The newly created weather entry or error message.
    """
    data = request.get_json()
    try:
        entry = weather_model.add_weather_entry(
            city=data['city'],
            temperature=data['temperature'],
            condition=data['condition'],
            humidity=data['humidity']
        )
        return jsonify(entry.__dict__), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/weather', methods=['GET'])
def get_all_weather():
    """
    Retrieves all weather entries in memory.

    Returns:
        JSON: List of weather entries.
    """
    entries = weather_model.get_all_weather_entries()
    return jsonify([entry.__dict__ for entry in entries]), 200

@app.route('/weather/<int:weather_id>', methods=['GET'])
def get_weather_by_id(weather_id):
    """
    Retrieves a specific weather entry by ID.

    Args:
        weather_id (int): The ID of the weather entry.

    Returns:
        JSON: The weather entry or error message.
    """
    try:
        entry = weather_model.get_weather_entry_by_id(weather_id)
        return jsonify(entry.__dict__), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route('/weather/<int:weather_id>', methods=['PUT'])
def update_weather(weather_id):
    """
    Updates a specific weather entry by ID.

    Expects:
        JSON with optional fields:
            { "city": str, "temperature": float, "condition": str, "humidity": int }

    Returns:
        JSON: The updated weather entry or error message.
    """
    data = request.get_json()
    try:
        entry = weather_model.update_weather_entry(
            weather_id,
            city=data.get('city'),
            temperature=data.get('temperature'),
            condition=data.get('condition'),
            humidity=data.get('humidity')
        )
        return jsonify(entry.__dict__), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/weather/<int:weather_id>', methods=['DELETE'])
def delete_weather(weather_id):
    """
    Deletes a weather entry by ID.

    Args:
        weather_id (int): The ID of the weather entry to delete.

    Returns:
        JSON: Success or error message.
    """
    try:
        weather_model.remove_weather_entry(weather_id)
        return jsonify({"message": f"Weather entry {weather_id} deleted"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.before_first_request
def create_tables():
    """
    Creates the database tables before the first request if they don't exist.
    """
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
