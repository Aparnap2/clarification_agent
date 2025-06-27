#!/bin/bash

# Initialize the database if it doesn't exist
if [ ! -f .clarity/conversations.db ]; then
    echo "Initializing database..."
    python init_db.py
fi

# Run the enhanced UI
echo "Starting Enhanced Clarification Agent..."
streamlit run app.py