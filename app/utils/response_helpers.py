from flask import jsonify


def error_response(message, code=500, details=None):
    """Create standardized error response"""
    response = {
        'status': 'error',
        'error': {
            'code': code,
            'message': message
        }
    }
    if details:
        response['error']['details'] = details
    return jsonify(response), code


def success_response(data):
    """Create standardized error response"""
    response = {
        'status': 'error',
        'data': data
    }
    return jsonify(response), 200