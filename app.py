"""
Main Flask application for Android Management API
"""
from flask import Flask, jsonify, request
from functools import wraps
import logging
from config import Config, validate_config
from auth import GoogleAuthClient

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global auth client
google_auth_client = None


def init_app():
    """Initialize the application"""
    global google_auth_client
    
    try:
        # Validate configuration
        validate_config()
        
        # Initialize Google Auth Client
        google_auth_client = GoogleAuthClient()
        logger.info("Application initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise


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


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Android Management API server is running'
    }), 200


@app.route('/api/v1/auth/status', methods=['GET'])
@error_handler
def check_auth_status():
    """
    Check service account authentication status
    
    Returns:
        JSON response with authentication status and details
    """
    if not google_auth_client:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
    auth_status = google_auth_client.check_authentication_status()
    
    if auth_status['status'] == 'success':
        return jsonify(auth_status), 200
    else:
        return jsonify(auth_status), 401


@app.route('/api/v1/status', methods=['GET'])
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'service': 'Android Management API'
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500


if __name__ == '__main__':
    try:
        init_app()
        app.run(
            host='0.0.0.0',
            port=Config.PORT,
            debug=Config.FLASK_ENV == 'development'
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        exit(1)
