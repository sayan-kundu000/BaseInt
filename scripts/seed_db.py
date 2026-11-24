"""Database seeding command-line script for BaseInt.

Usage:
    python scripts/seed_db.py
"""

from app.database.connection import get_engine
from app.database.seed import seed_database

if __name__ == "__main__":
    engine = get_engine()
    result = seed_database(engine)
    print(result)
