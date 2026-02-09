"""
Authentication and Authorization Routes
Handles user registration, login, and JWT authentication
"""
from flask import Blueprint, request
import logging

from app.repositories.user_repository import UserRepository
from app.utils.auth_helpers import hash_password, verify_password, generate_jwt_token
from app.utils.decorators import error_handler, require_payload
from app.utils.response_helpers import error_response, success_response

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize repository
user_repo = UserRepository()

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1')

@auth_bp.route('/register', methods=['POST'])
@error_handler('register')
@require_payload("email", "password")
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

    email = data['email'].strip()
    password = data['password'].strip()

    if len(password) < 6:
        return error_response('Password must be at least 6 characters', 400)

    # Hash password
    password_hash = hash_password(password)
    # Create user in database using repository
    success = user_repo.create_user(email, password_hash)

    if not success:
        return error_response('User already exists', 409)

    return success_response(None)


@auth_bp.route('/login', methods=['POST'])
@error_handler("login")
@require_payload("email", "password")
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
    email = data['email'].strip()
    password = data['password'].strip()

    # Get user from database using repository
    user = user_repo.get_user(email)

    if not user or not verify_password(password, user['password_hash']):
        return error_response('Invalid email or password', 401)

    # Generate JWT token
    token = generate_jwt_token(email)

    return  success_response({
        'token': token,
        'email': email
    })
