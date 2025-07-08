#!/bin/bash

# Enhanced Clarification Agent with Beautiful Activity Logs
# Run script for the fully enhanced version with beautiful UI

echo "🎨 Starting Enhanced Clarification Agent with Beautiful Activity Logs..."
echo "=================================================================="

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

# Run tests first (optional)
echo "Running activity logging tests..."
python test_beautiful_activities.py

echo ""
echo "🚀 Launching Enhanced Clarification Agent with Beautiful Activity Logs..."
echo "Features:"
echo "  ✨ Beautiful real-time activity tracking"
echo "  🔍 Web search with detailed logging"
echo "  🎨 Animated activity cards"
echo "  📊 Detailed tool call visualization"
echo "  🤖 Agent thinking process transparency"
echo ""
echo "Access the app at: http://localhost:8501"
echo "=================================================================="

# Run the enhanced app with beautiful activity logs
streamlit run enhanced_web_search_app.py --server.port 8501 --server.address 0.0.0.0