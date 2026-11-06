"""
Movie Storage
DS 3500 - MP3

Manages persistent storage of one movie collection in SQLite.

Replaces the stored collection on each upload, retrieves movies
as a DataFrame, selects and filters records with SQL queries,
and counts the stored movies.
"""

import logging
import sqlite3

import pandas as pd

from .database import get_connection, initialize_database

logger = logging.getLogger(__name__)
MOVIE_COLUMNS = ["title", "release_year", "rating", "genre"]


class MovieStorage:
    """SQLite-backed storage for one movie collection."""
    def __init__(self, db_path="data/movies.db"):
        self.db_path = db_path
        initialize_database(self.db_path)

    def save(self, df):
        """Replace all movie rows in one transaction."""
        # Convert missing values to Python None for SQL NULL.
        # DELETE the old rows, then INSERT all rows from df.
        # Commit only after all inserts succeed; roll back on SQLite errors.
        # Close the connection in finally. Log the saved row count at DEBUG.
        # Convert to Python None for SQL NULL
        clean = df[MOVIE_COLUMNS].astype(object)
        clean = clean.where(pd.notnull(clean), None)
        rows = list(clean.itertuples(index=False, name=None))

        conn = get_connection(self.db_path)
        try: 
            conn.execute("DELETE FROM movies")
            conn.executemany(
                "INSERT OR REPLACE INTO movies (title, release_year, rating, genre) "
                "VALUES (?, ?, ?, ?)",
                rows
            )
            conn.commit()
            logger.debug(f"Stored dataset: rows={len(df)}")
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Failed to save movies; rolled back. Error: {e}")
            raise
        finally:
            conn.close()

    def get(self):
        """Return the four movie columns as a DataFrame, ordered by id."""
        # TODO: SELECT the four fields, fetch rows, and create the DataFrame.
        # Return a DataFrame with columns=MOVIE_COLUMNS,
        # so the column names are preserved even when the query returns no rows.
        conn = get_connection(self.db_path)
        try:
            select_statement = "SELECT title, release_year, rating, genre FROM movies ORDER BY id"
            rows = conn.execute(select_statement).fetchall()
            df = pd.DataFrame(rows, columns=MOVIE_COLUMNS)
            return df
        finally:
            conn.close()

    def select_columns(self, columns, limit=5):
        """Return id plus the requested movie columns, ordered by id."""
        if not columns:
            logger.error("Select at least one column")
            raise ValueError("Select at least one column")

        for column in columns:
            if column not in MOVIE_COLUMNS:
                logger.error(f"Unsupported column: {column}")
                raise ValueError(f"Unsupported column: {column}")

        selected_columns = ", ".join(["id"] + columns)
        connection = get_connection(self.db_path)
        try:
            # SELECT selected_columns from movies, ordered by id.
            # Use a placeholder for limit; fetch the rows.
            # Return a list of dictionaries and log at DEBUG.
            select_statement = f"SELECT {selected_columns} FROM movies ORDER BY id LIMIT ?"
            rows = connection.execute(select_statement, (limit,)).fetchall()
            result = [dict(row) for row in rows]
            logger.debug(f"Selected columns: {columns}, rows returned: {len(result)}")
            return result
        except sqlite3.Error as e:
            logger.error(f"Failed to select columns; Error: {e}")
            raise
        finally:
            connection.close()
    
    def count_movies(self):
        """Return the number of stored movies using SQL COUNT(*)."""
        conn = get_connection(self.db_path)
        try:
            count = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
            return count
        finally:
            conn.close()

    def query_movies(self, columns, min_rating, limit):
        """Return selected fields from matching movies using SQL."""
        # TODO: validate columns as in select_columns().
        # SELECT id plus those columns and filter by minimum rating.
        # Sort by rating DESC then id ASC, and apply limit.
        # Return dictionaries and log the selected columns and row count at DEBUG.
        if not columns:
            logger.error("Select at least one column")
            raise ValueError("Select at least one column")
       
        for column in columns:
            if column not in MOVIE_COLUMNS:
                logger.error(f"Unsupported column: {column}")
                raise ValueError(f"Unsupported column: {column}")

            
        select_statement = f"SELECT id, {', '.join(columns)} FROM movies WHERE rating >= ? ORDER BY rating DESC, id ASC LIMIT ?"
        conn = get_connection(self.db_path)

        try:
            rows = conn.execute(select_statement, (min_rating, limit)).fetchall()
            result = [dict(row) for row in rows]
            logger.debug(f"Selected columns: {columns}, rows returned: {len(result)}")
            return result
        except sqlite3.Error as e:
            logger.error(f"Failed to query movies; Error: {e}")
            raise
        finally:
            conn.close()