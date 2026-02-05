from app.database import get_database

class EnterpriseRepository:
    """Handles all enterprise-related database operations"""

    def __init__(self):
        self.db = get_database()

    def get_enterprise_name(self, email):
        """Get enterprise name for a user email"""
        return self.db.get_enterprise_name(email)

    def upsert_mapping(self, email, enterprise_name):
        """Create or update email-to-enterprise mapping"""
        return self.db.upsert_mapping(email, enterprise_name)

    def list_mappings(self):
        """List all email-enterprise mappings"""
        return self.db.list_mappings()