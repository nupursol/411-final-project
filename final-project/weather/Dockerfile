# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Set environment variables
ENV CREATE_DB=true
ENV DB_PATH=/app/db/weather.db
ENV SECRET_KEY=dev
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV SQLALCHEMY_DATABASE_URI=sqlite:////app/db/weather.db
ENV OPENWEATHER_API_KEY=7b43adca34f4beb8351a7da85a3afc7e

# Install any needed packages specified in requirements.txt
# In production, you would want to ensure that any re-compiled packages
# With the same version number are re-downloaded
RUN pip install --no-cache-dir -r requirements.txt

# Install SQLite3 and other system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Add a shell script that loads the .env file and handles database creation
COPY sql/create_db.sh /app/sql/create_db.sh
COPY sql/init_db.sql /app/sql/init_db.sql

# Make scripts executable
RUN chmod +x /app/entrypoint.sh && \
    chmod +x /app/sql/create_db.sh

# Create and set permissions for the db directory
RUN mkdir -p /app/db && \
    chmod 777 /app/db && \
    touch /app/db/weather.db && \
    chmod 666 /app/db/weather.db

# Define a volume for persisting the database
VOLUME ["/app/db"]

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Run the entrypoint script when the container launches
CMD ["/app/entrypoint.sh"]
