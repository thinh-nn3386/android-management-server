"""
Common decorators for API endpoints
Handles error handling and JWT authentication
"""
from flask import request, jsonify
from functools import wraps
import logging

from app.utils.auth_helpers import decode_jwt_token
from app.utils.response_helpers import error_response

logger = logging.getLogger(__name__)


def error_handler(f):
    """Decorator that wraps Flask route functions with error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            log_func = getattr(logger, 'error', logger.error)
            log_func(f"Error in {f.__name__}: {str(e)}")

            return error_response(
                f'Internal server error: {str(e)}',
                500
            )

    return decorated_function


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

def require_payload(*required_fields):
    """
    Decorator to require multiple fields in payload

    Args:
        *required_fields: Field names to check (e.g., 'enterprise_name', 'callback_url')

    Usage:
        @require_payload('enterprise_name', 'policy_name')
        def my_endpoint():
            pass
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()

            # Check if payload exists
            if not data:
                return error_response('Request payload is required', 400)

            # Check each required field
            for field_name in required_fields:
                # Check if field exists in payload
                if field_name not in data:
                    return error_response(f'{field_name} is required', 400)

                # Check if field value is not empty (handles None, empty string, empty list)
                field_value = data[field_name]

                # Handle string values
                if isinstance(field_value, str):
                    if not field_value.strip():
                        return error_response(f'{field_name} cannot be empty', 400)
                # Handle None values
                elif field_value is None:
                    return error_response(f'{field_name} cannot be null', 400)
                # Handle empty lists/dicts
                elif isinstance(field_value, (list, dict)) and not field_value:
                    return error_response(f'{field_name} cannot be empty', 400)

            return f(*args, **kwargs)

        return decorated_function

    return decorator

def require_query_params(*required_params):
    """
    Decorator to require query parameters

    Args:
        *required_params: Query parameter names to check (e.g., 'enterprise_name', 'policy_name')

    Usage:
        @require_query_params('enterprise_name')
        def my_endpoint():
            pass
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check each required query parameter
            for param_name in required_params:
                param_value = request.args.get(param_name)

                # Check if parameter exists
                if not param_value:
                    return error_response(
                        f'{param_name} query parameter is required',
                        400
                    )

                # Check if parameter is not empty (after strip)
                if not param_value.strip():
                    return error_response(
                        f'{param_name} query parameter cannot be empty',
                        400
                    )

            return f(*args, **kwargs)

        return decorated_function

    return decorator