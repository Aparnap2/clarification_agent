#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is required but not installed. Please install pip3 and try again."
    exit 1
fi

# Install dependencies if not already installed
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Run the Streamlit app
echo "Starting Clarification Agent..."
streamlit run app.py