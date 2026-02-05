from config import Config
from .local_sqlite_db import LocalDatabase

def get_database():
    """Factory function to get appropriate database implementation"""
    if Config.DATABASE_TYPE == "sqlite":
        return LocalDatabase()
    elif Config.DATABASE_TYPE == "cloud":
        from .cloud_db import CloudDatabase
        return CloudDatabase()
    else:
        raise ValueError(f"Unknown database type: {Config.DATABASE_TYPE}")
