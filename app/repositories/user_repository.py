from app.database import get_database

class UserRepository:
    """Handles all user-related database operations"""

    def __init__(self):
        self.db = get_database()

    def create_user(self, email, password_hash):
        """Create a new user"""
        return self.db.create_user(email, password_hash)

    def get_user(self, email):
        """Retrieve user by email"""
        return self.db.get_user(email)

    def user_exists(self, email):
        """Check if user exists"""
        return self.db.get_user(email) is not None
