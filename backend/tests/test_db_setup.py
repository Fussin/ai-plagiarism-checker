# Helper for test database setup
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import settings
from backend.database import Base # Import Base from your main database.py
# Import all your models here so Base knows about them for create_all
from backend.models import UserDB, ScanHistoryDB

# Use a separate test database if desired, or ensure main test.db is cleaned.
# For this example, we'll use the configured test.db and ensure it's clean for tests.
TEST_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False} if TEST_DATABASE_URL.startswith("sqlite") else {})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_test_db():
    # Drop all tables and recreate them
    # This ensures a clean state for each test session if run globally
    # or can be called selectively.
    # Be CAREFUL with this on a real DB.
    if os.path.exists(TEST_DATABASE_URL.split(":///")[1]) and TEST_DATABASE_URL.startswith("sqlite"):
         # print(f"Recreating test database: {TEST_DATABASE_URL}")
         Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# If running this file directly, initialize the test DB
if __name__ == "__main__":
    print(f"Initializing test database at: {TEST_DATABASE_URL}")
    init_test_db()
    print("Test database initialized.")
