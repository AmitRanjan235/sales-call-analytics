import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/sales_analytics.db")

# SQLite-specific configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False
        },  # Allow SQLite to be used with multiple threads
    )
else:
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
