import sqlite3
from contextlib import contextmanager
from config import Config
from .base import DatabaseInterface

class LocalDatabase(DatabaseInterface):
    """SQLite-backed storage for email-enterprise mapping"""

    def __init__(self, db_path=None):
        self.db_path = db_path or Config.SQLITE_DB_PATH
        self._init_db()

    @contextmanager
    def _get_connection(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _init_db(self):
        with self._get_connection(self) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS email_enterprise (
                    email TEXT PRIMARY KEY,
                    enterprise_name TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def get_enterprise_name(self, email):
        with self._get_connection(self) as connection:
            cursor = connection.execute(
                "SELECT enterprise_name FROM email_enterprise WHERE email = ?",
                (email.lower(),)
            )
            row = cursor.fetchone()
            return row["enterprise_name"] if row else None

    def upsert_mapping(self, email, enterprise_name):
        with self._get_connection(self) as connection:
            connection.execute(
                "INSERT OR REPLACE INTO email_enterprise (email, enterprise_name) VALUES (?, ?)",
                (email.lower(), enterprise_name)
            )

    def list_mappings(self):
        with self._get_connection(self) as connection:
            cursor = connection.execute(
                "SELECT email, enterprise_name FROM email_enterprise ORDER BY email "
            )
            return [
                {"email": row["email"], "enterprise_name": row["enterprise_name"]}
                for row in cursor.fetchall()
            ]

    def create_user(self, email, password_hash):
        with self._get_connection(self) as connection:
            try:
                connection.execute(
                    "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                    (email.lower(), password_hash)
                )
                return True
            except sqlite3.IntegrityError:
                return False

    def get_user(self, email):
        with self._get_connection(self) as connection:
            cursor = connection.execute(
                "SELECT id, email, password_hash, created_at FROM users WHERE email = ?",
                (email.lower(),)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "id": row["id"],
                    "email": row["email"],
                    "password_hash": row["password_hash"],
                    "created_at": row["created_at"]
                }
            return None