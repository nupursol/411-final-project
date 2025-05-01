from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from models.user_model import db, User
from models.weather_model import WeatherModel
from datetime import timedelta
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

db.init_app(app)
weather_model = WeatherModel()

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "ok"}), 200

@app.route('/create-account', methods=['POST'])
def create_account():
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
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route('/update-password', methods=['PUT'])
def update_password():
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
    entries = weather_model.get_all_weather_entries()
    return jsonify([entry.__dict__ for entry in entries]), 200

@app.route('/weather/<int:weather_id>', methods=['GET'])
def get_weather_by_id(weather_id):
    try:
        entry = weather_model.get_weather_entry_by_id(weather_id)
        return jsonify(entry.__dict__), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route('/weather/<int:weather_id>', methods=['PUT'])
def update_weather(weather_id):
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
    try:
        weather_model.remove_weather_entry(weather_id)
        return jsonify({"message": f"Weather entry {weather_id} deleted"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
