"""
Main Flask application for Android Management API
Simplified app.py using blueprints for better organization
"""
from flask import Flask, jsonify
from flask_cors import CORS
import logging

from app.config import Config, validate_config
from app.routes.auth_routes import auth_bp
from app.routes.android_management_routes import (
    enterprise_bp,
    policies_bp,
    devices_bp,
    init_google_client
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory pattern"""
    # Initialize Flask app
    flask_app = Flask(__name__)

    # Configure CORS for frontend development
    CORS(flask_app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        },
        r"/health": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "OPTIONS"]
        }
    })

    # Validate configuration
    validate_config()

    # Initialize Google Android Management client
    init_google_client()

    # Register blueprints
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(enterprise_bp)
    flask_app.register_blueprint(policies_bp)
    flask_app.register_blueprint(devices_bp)

    # Health check endpoint
    @flask_app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'message': 'Android Management API server is running'
        }), 200

    # Error handlers
    @flask_app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'status': 'error',
            'message': 'Endpoint not found'
        }), 404

    @flask_app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

    logger.info("Application initialized successfully")
    return flask_app


