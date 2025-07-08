#!/bin/bash

# Enhanced Clarification Agent - Simple launcher
echo "Starting Enhanced Clarification Agent..."
echo "Features: Animations, Process Tracking, Web Search Integration"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Create .env with: OPENROUTER_API_KEY=your_key_here"
fi

# Run the enhanced app
streamlit run enhanced_app.py --server.port 8502