#!/bin/bash

# Enhanced Clarification Agent with Web Search
# Run script for the web search enabled version

echo "🧠 Starting Enhanced Clarification Agent with Web Search..."
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p .clarity
mkdir -p logs

# Set environment variables for crawl4ai
export CRAWL4AI_HEADLESS=true
export CRAWL4AI_CACHE_MODE=bypass

# Run the enhanced web search app
echo "🚀 Launching Enhanced Clarification Agent..."
echo "Access the app at: http://localhost:8501"
echo "=================================================="

streamlit run web_search_app.py --server.port 8501 --server.address 0.0.0.0