from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    """Abstract database interface"""

    @abstractmethod
    def get_enterprise_name(self, email):
        pass

    @abstractmethod
    def upsert_mapping(self, email, enterprise_name):
        pass

    @abstractmethod
    def list_mappings(self):
        pass

    @abstractmethod
    def create_user(self, email, password_hash):
        pass

    @abstractmethod
    def get_user(self, email):
        pass
