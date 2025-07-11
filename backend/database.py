from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings

# Define the database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Create a SQLAlchemy engine
# For SQLite, connect_args is needed to allow same-thread usage with FastAPI
# For other databases like PostgreSQL, connect_args might not be needed or different.
engine_args = {}
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)

# Create a SessionLocal class, which will be used to create database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for declarative class definitions (models)
Base = declarative_base()

# Dependency to get a DB session in FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables in the database
# This is usually called once at application startup or handled by migrations (Alembic)
# For a simple setup, you might call this from main.py
# However, with Alembic, this is not strictly necessary as Alembic handles table creation.
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

# If you want to automatically create tables when this module is imported (e.g. for very simple apps without migrations)
# you might call it here, but it's generally better to manage schema with Alembic.
# For now, we will rely on Alembic for table creation.
# if __name__ == "__main__":
#     print(f"Creating database tables for {DATABASE_URL}...")
#     create_db_and_tables()
#     print("Database tables created (if they didn't exist).")
