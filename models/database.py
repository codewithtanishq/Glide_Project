"""
models/database.py
------------------
DatabaseManager class — wraps all SQLite operations in one place.

This demonstrates ENCAPSULATION: every database detail (connection,
cursors, SQL statements) is hidden behind clean method names like
save_user(), save_search(), get_history().
"""
import sqlite3
import os
from datetime import datetime


class DatabaseManager:
    """Single point of contact for all database work."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        # Make sure the database/ folder exists before opening a connection.
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_tables()

    # ---------- internal helpers ----------
    def _connect(self):
        """Open a new connection. We open/close per call to keep it simple."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # rows behave like dictionaries
        return conn

    def _create_tables(self):
        """Create tables on first run if they don't exist."""
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    google_id    TEXT UNIQUE,
                    name         TEXT,
                    email        TEXT UNIQUE,
                    picture      TEXT,
                    created_at   TEXT
                );

                CREATE TABLE IF NOT EXISTS searches (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id       INTEGER,
                    pickup        TEXT,
                    destination   TEXT,
                    pickup_lat    REAL,
                    pickup_lng    REAL,
                    dest_lat      REAL,
                    dest_lng      REAL,
                    distance_km   REAL,
                    created_at    TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                """
            )

    # ---------- user methods ----------
    def save_user(self, google_id: str, name: str, email: str, picture: str) -> int:
        """Insert user if new, otherwise return existing id."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE google_id = ?", (google_id,))
            row = cur.fetchone()
            if row:
                return row["id"]

            cur.execute(
                """INSERT INTO users (google_id, name, email, picture, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (google_id, name, email, picture, datetime.utcnow().isoformat()),
            )
            return cur.lastrowid

    def get_user(self, user_id: int):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            return dict(row) if row else None

    # ---------- search-history methods ----------
    def save_search(self, user_id, pickup, destination,
                    pickup_lat, pickup_lng, dest_lat, dest_lng, distance_km):
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO searches
                   (user_id, pickup, destination,
                    pickup_lat, pickup_lng, dest_lat, dest_lng,
                    distance_km, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id, pickup, destination,
                    pickup_lat, pickup_lng, dest_lat, dest_lng,
                    distance_km, datetime.utcnow().isoformat(),
                ),
            )

    def get_history(self, user_id: int, limit: int = 20):
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT pickup, destination, distance_km, created_at
                   FROM searches
                   WHERE user_id = ?
                   ORDER BY id DESC
                   LIMIT ?""",
                (user_id, limit),
            ).fetchall()
            return [dict(r) for r in rows]
