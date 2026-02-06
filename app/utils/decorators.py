"""
Common decorators for API endpoints
Handles error handling and JWT authentication
"""
from flask import request, jsonify
from functools import wraps
import logging

from app.utils.auth_service import decode_jwt_token

logger = logging.getLogger(__name__)


def error_handler(f):
    """Decorator to handle errors in API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e),
                'error_type': type(e).__name__
            }), 500
    return decorated_function


def require_jwt(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({
                'status': 'error',
                'message': 'Authorization header is missing'
            }), 401

        try:
            # Expected format: "Bearer <token>"
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        except IndexError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid authorization header format'
            }), 401

        payload = decode_jwt_token(token)

        if not payload:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired token'
            }), 401

        # Add user email to request context
        setattr(request, 'user_email', payload['email'])

        return f(*args, **kwargs)
    return decorated_function
