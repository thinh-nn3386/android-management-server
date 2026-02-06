"""
Common decorators for API endpoints
Handles error handling and JWT authentication
"""
from flask import request, jsonify
from functools import wraps
import logging

from app.utils.auth_service import decode_jwt_token
from app.utils.response_helpers import error_response

logger = logging.getLogger(__name__)


def error_handler(message=None):
    """
    Decorator that wraps Flask route functions with error handling

    Args:
        message: Custom error message prefix
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                log_func = getattr(logger, 'error', logger.error)
                prefix = f"{message}: " if message else ""
                log_func(f"{prefix}Error in {f.__name__}: {str(e)}")

                return error_response(
                    f'{prefix}Internal server error: {str(e)}',
                    500
                )

        return decorated_function

    return decorator


def require_jwt(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return error_response('Authorization header is missing', 401)

        try:
            # Expected format: "Bearer <token>"
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        except IndexError:
            return error_response('Invalid authorization header format', 401)

        payload = decode_jwt_token(token)

        if not payload:
            return  error_response( 'Invalid or expired token', 401)

        # Add user email to request context
        setattr(request, 'user_email', payload['email'])

        return f(*args, **kwargs)
    return decorated_function
