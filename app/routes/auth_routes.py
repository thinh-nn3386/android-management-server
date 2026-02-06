"""
Authentication and Authorization Routes
Handles user registration, login, and JWT authentication
"""
from flask import Blueprint, request, jsonify
import logging

from app.repositories.user_repository import UserRepository
from app.utils.auth_service import hash_password, verify_password, generate_jwt_token
from app.utils.decorators import error_handler, require_jwt

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize repository
user_repo = UserRepository()

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1')

@auth_bp.route('/register', methods=['POST'])
@error_handler
def register():
    """
    Register a new user

    Request body:
        {
            "email": "user@example.com",
            "password": "password123"
        }
    """
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Email and password are required'
        }), 400

    email = data['email'].strip()
    password = data['password']

    if not email or not password:
        return jsonify({
            'status': 'error',
            'message': 'Email and password cannot be empty'
        }), 400

    if len(password) < 6:
        return jsonify({
            'status': 'error',
            'message': 'Password must be at least 6 characters'
        }), 400

    try:
        # Hash password
        password_hash = hash_password(password)

        # Create user in database using repository
        success = user_repo.create_user(email, password_hash)

        if not success:
            return jsonify({
                'status': 'error',
                'message': 'User already exists'
            }), 409

        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'email': email
        }), 201

    except Exception as e:
        logger.error(f"Error in register endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Registration failed: {str(e)}'
        }), 500


@auth_bp.route('/login', methods=['POST'])
@error_handler
def login():
    """
    Login with email and password, returns JWT token

    Request body:
        {
            "email": "user@example.com",
            "password": "password123"
        }
    """
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Email and password are required'
        }), 400

    email = data['email'].strip()
    password = data['password']

    if not email or not password:
        return jsonify({
            'status': 'error',
            'message': 'Email and password cannot be empty'
        }), 400

    try:
        # Get user from database using repository
        user = user_repo.get_user(email)

        if not user:
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401

        # Verify password
        if not verify_password(password, user['password_hash']):
            return jsonify({
                'status': 'error',
                'message': 'Invalid email or password'
            }), 401

        # Generate JWT token
        token = generate_jwt_token(email)

        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'token': token,
            'email': email
        }), 200

    except Exception as e:
        logger.error(f"Error in login endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Login failed: {str(e)}'
        }), 500


@auth_bp.route('/status', methods=['GET'])
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'service': 'Android Management API'
    }), 200
