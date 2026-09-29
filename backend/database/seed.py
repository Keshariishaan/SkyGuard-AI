"""
Creates all tables. Run once before starting the backend for the first
time (main.py also calls this automatically on startup, so this is
mainly useful for scripted/manual setup and CI).

Run:
    python -m backend.database.seed
"""

from backend.database import models  # noqa: F401 (registers models on Base)
from backend.database.connection import Base, engine


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


if __name__ == "__main__":
    init_db()
