"""
Database connection setup.
Run this file directly to create party_store.db with the tables defined in models.py.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "sqlite:///party_store.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)
    print("Database initialized: party_store.db")


if __name__ == "__main__":
    init_db()
