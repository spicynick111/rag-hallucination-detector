"""Run this once to create the database tables."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database.connection import init_db, check_db_connection

if __name__ == "__main__":
    if check_db_connection():
        init_db()
        print("Database tables created successfully.")
    else:
        print("Cannot connect to database. Check your DATABASE_URL in .env")
        print("If PostgreSQL is not running, the app still works in demo mode (no persistence).")
