"""
Local SQLite database for email -> enterprise mapping
"""
import sqlite3
from contextlib import contextmanager
from config import Config


class LocalDatabase:
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
        with self._get_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS email_enterprise (
                    email TEXT PRIMARY KEY,
                    enterprise_name TEXT NOT NULL
                )
                """
            )

    def get_enterprise_name(self, email):
        with self._get_connection() as connection:
            cursor = connection.execute(
                "SELECT enterprise_name FROM email_enterprise WHERE email = ?",
                (email.lower(),)
            )
            row = cursor.fetchone()
            return row["enterprise_name"] if row else None

    def upsert_mapping(self, email, enterprise_name):
        with self._get_connection() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO email_enterprise (email, enterprise_name) VALUES (?, ?)",
                (email.lower(), enterprise_name)
            )

    def list_mappings(self):
        with self._get_connection() as connection:
            cursor = connection.execute(
                "SELECT email, enterprise_name FROM email_enterprise ORDER BY email ASC"
            )
            return [
                {"email": row["email"], "enterprise_name": row["enterprise_name"]}
                for row in cursor.fetchall()
            ]
