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

# Create .clarity directory if it doesn't exist
mkdir -p .clarity

# Install dependencies if not already installed
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Ask user which interface to use
echo "Choose an interface:"
echo "1) Web UI (Streamlit)"
echo "2) Command Line Interface"
read -p "Enter your choice (1/2): " choice

if [ "$choice" = "1" ]; then
    # Run the Streamlit app
    echo "Starting Clarification Agent Web UI..."
    streamlit run app_conversation.py
else
    # Run the CLI app
    echo "Starting Clarification Agent CLI..."
    python3 cli_conversation.py
fi