"""
Database Setup
DS 3500 - MP3

Creates SQLite connections and the movies table.

Each connection returns rows that can be read by column name,
and the database's parent folder is created if it does not exist.
"""

import sqlite3
from pathlib import Path


def get_connection(db_path):
    """Return a fresh connection with rows accessible by column name."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database(db_path):
    """Create the movie table if it does not exist."""
    conn = get_connection(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY,
                title TEXT,
                release_year INTEGER,
                genre TEXT,
                rating REAL
            )
        """)
        conn.commit()
    finally:
        conn.close()
