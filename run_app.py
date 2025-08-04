#!/usr/bin/env python3
"""
Startup script for AI Strategy Assistant Streamlit application.

This script provides a simple way to launch the application with proper
configuration and error handling.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'streamlit',
        'langgraph', 
        'crawl4ai',
        'pydantic',
        'plotly',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Install missing packages with: pip install -r requirements.txt")
        return False
    
    return True


def check_environment():
    """Check environment configuration."""
    warnings = []
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        warnings.append("OPENAI_API_KEY environment variable not set")
    
    # Check if running in virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        warnings.append("Not running in a virtual environment (recommended)")
    
    if warnings:
        logger.warning("Environment warnings:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
        logger.info("You can still run the app, but consider addressing these warnings.")
    
    return True


def main():
    """Main startup function."""
    logger.info("Starting AI Strategy Assistant...")
    
    # Check current directory
    if not Path("app.py").exists():
        logger.error("app.py not found in current directory")
        logger.info("Please run this script from the project root directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    check_environment()
    
    # Set environment variables for better Streamlit experience
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
    os.environ.setdefault("STREAMLIT_SERVER_ENABLE_CORS", "false")
    os.environ.setdefault("STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION", "false")
    
    # Launch Streamlit app
    try:
        logger.info("Launching Streamlit application...")
        logger.info("The app will open in your default browser")
        logger.info("Press Ctrl+C to stop the application")
        
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Streamlit: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()