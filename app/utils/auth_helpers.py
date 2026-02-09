"""
Authentication utilities for password hashing and JWT token management
"""
import bcrypt
import jwt
from datetime import datetime, timedelta
from app.config import Config


def hash_password(password):
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password, password_hash):
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password
        password_hash: Hashed password from database
        
    Returns:
        bool: True if password matches
    """
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_jwt_token(user_email):
    """
    Generate JWT token for authenticated user
    
    Args:
        user_email: User's email address
        
    Returns:
        str: JWT token
    """
    expiration = datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    
    payload = {
        'email': user_email,
        'exp': expiration,
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    return token


def decode_jwt_token(token):
    """
    Decode and verify JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
