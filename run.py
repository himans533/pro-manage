#!/usr/bin/env python
"""
Main entry point for running the Pro-Manage application
Ensures all dependencies and database are initialized
"""

import os
import sys
from pathlib import Path

# Add AdminLoginPanel to path
admin_panel_path = Path(__file__).parent / "AdminLoginPanel"
sys.path.insert(0, str(admin_panel_path))

# Change to AdminLoginPanel directory
os.chdir(admin_panel_path)

# Import and run the Flask app
from app import app, DB_PATH, get_db_connection

def initialize_database():
    """Initialize database if it doesn't exist"""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}, initializing...")
        try:
            conn = get_db_connection()
            conn.close()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Initialize database
    initialize_database()
    
    # Run Flask app
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Pro-Manage on http://0.0.0.0:{port}")
    print(f"Press Ctrl+C to quit")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
        use_reloader=True
    )
