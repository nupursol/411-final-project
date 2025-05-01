-- Drop existing tables if they exist
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS weather_entries;

-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL
);

-- Create weather_entries table
CREATE TABLE weather_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    temperature REAL NOT NULL,
    condition TEXT NOT NULL,
    humidity INTEGER NOT NULL CHECK(humidity >= 0 AND humidity <= 100),
    date_recorded TEXT NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX idx_weather_entries_city ON weather_entries(city);
CREATE INDEX idx_weather_entries_date ON weather_entries(date_recorded);