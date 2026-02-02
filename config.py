"""
Configuration module for the Android Management API server
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    CLOUD_PROJECT_ID = os.getenv('CLOUD_PROJECT_ID')
    SERVICE_ACCOUNT_JSON = os.getenv('SERVICE_ACCOUNT_JSON')
    SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'local.db')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', False)
    PORT = int(os.getenv('PORT', 8088))


def validate_config():
    """Validate that all required environment variables are set"""
    required_vars = ['CLOUD_PROJECT_ID', 'SERVICE_ACCOUNT_JSON']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
