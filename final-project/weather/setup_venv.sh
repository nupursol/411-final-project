#!/bin/bash

# Set the name of the virtual environment directory and requirements file
VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"

# Check if the virtual environment already exists
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR" || { echo "❌ Failed to create venv"; exit 1; }

  echo "Activating virtual environment..."
  source "$VENV_DIR/bin/activate" || { echo "❌ Failed to activate venv"; exit 1; }

  # Install dependencies from requirements.txt if it exists
  if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS_FILE"
    pip install pytest pytest-mock
  else
    echo "Error: $REQUIREMENTS_FILE not found."
    exit 1
  fi

else
  echo "Virtual environment already exists."
  echo "To activate it, run: source $VENV_DIR/bin/activate"
fi

  echo "Virtual environment already exists. Activated."
fi
