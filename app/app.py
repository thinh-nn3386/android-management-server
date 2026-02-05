"""
Main Flask application for Android Management API
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import wraps
import logging

from app.repositories.enterprise_repository import EnterpriseRepository
from app.repositories.user_repository import UserRepository
from config import Config, validate_config
from auth import GoogleAuthClient
from app.database import get_database
from auth_utils import hash_password, verify_password, generate_jwt_token, decode_jwt_token

# Initialize Flask app
app = Flask(__name__)

# Configure CORS for frontend development
CORS(app, resources={
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global auth client
google_auth_client = None
user_repo = UserRepository()
enterprise_repo = EnterpriseRepository()

def init_app():
    """Initialize the application"""
    global google_auth_client, db
    
    try:
        # Validate configuration
        validate_config()
        
        # Initialize Google Auth Client
        google_auth_client = GoogleAuthClient()
        db = get_database()
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


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Android Management API server is running'
    }), 200


@app.route('/api/v1/register', methods=['POST'])
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
    if not db:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
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
        
        # Create user in database
        success = db.create_user(email, password_hash)
        
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


@app.route('/api/v1/login', methods=['POST'])
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
    if not db:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
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
        # Get user from database
        user = db.get_user(email)
        
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


@app.route('/api/v1/enterprise/login', methods=['POST'])
@error_handler
@require_jwt
def enterprise_login():
    """
    Check if user has a registered enterprise
    
    Email is extracted from JWT token in Authorization header.
    No request body required.
    
    Returns:
        - If found: enterprise_found=true with enterprise info
        - If not found: enterprise_found=false
    """
    if not google_auth_client or not db:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
    # Get email from JWT token (set by require_jwt decorator)
    email = getattr(request, 'user_email', None)
    
    if not email:
        return jsonify({
            'status': 'error',
            'message': 'Unable to extract email from token'
        }), 401
    
    try:
        # Check if email is mapped to an enterprise
        enterprise_name = db.get_enterprise_name(email)
        
        if not enterprise_name:
            return jsonify({
                'status': 'success',
                'enterprise_found': False,
                'message': 'No enterprise found for this email',
                'email': email
            }), 200
        
        # Get enterprise details from Google Cloud
        enterprise_result = google_auth_client.list_enterprises()
        enterprises = enterprise_result.get('enterprises', [])
        
        for enterprise in enterprises:
            if enterprise['name'] == enterprise_name:
                return jsonify({
                    'status': 'success',
                    'enterprise_found': True,
                    'message': 'Enterprise found for this email',
                    'email': email,
                    'enterprise': enterprise
                }), 200
        
        # Enterprise name exists in DB but not in Google Cloud
        return jsonify({
            'status': 'success',
            'enterprise_found': False,
            'message': 'Enterprise mapping exists but enterprise not found in Google Cloud',
            'email': email
        }), 200
            
    except Exception as e:
        logger.error(f"Error in enterprise login: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Enterprise check failed: {str(e)}'
        }), 500


@app.route('/api/v1/enterprise/signup-url', methods=['POST'])
@error_handler
@require_jwt
def create_signup_url():
    """
    Generate a signup URL for enterprise registration
    
    Request body:
        {
            "callback_url": "https://your-domain.com/callback"
        }
    
    Returns:
        Signup URL and signup name
    """
    if not google_auth_client:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
    data = request.get_json()
    if not data or 'callback_url' not in data:
        return jsonify({
            'status': 'error',
            'message': 'callback_url is required'
        }), 400
    
    callback_url = data['callback_url'].strip()
    
    if not callback_url:
        return jsonify({
            'status': 'error',
            'message': 'callback_url cannot be empty'
        }), 400
    
    try:
        signup_result = google_auth_client.generate_signup_url(callback_url=callback_url)
        
        return jsonify({
            'status': 'success',
            'message': 'Signup URL generated successfully',
            'signup_url': signup_result['url'],
            'signup_name': signup_result['name']
        }), 200
            
    except Exception as e:
        logger.error(f"Error generating signup URL: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to generate signup URL: {str(e)}'
        }), 500


@app.route('/api/v1/enterprise/webtoken', methods=['POST'])
@error_handler
@require_jwt
def create_enterprise_webtoken():
    """
    Create enterprise web token
    
    Request body (WebToken):
        {
            "enterprise_name": "enterprises/LC...",
            "parent_frame_url": "https://your-domain.com" (optional),
            "enable_features": ["PLAY_SEARCH", "PRIVATE_APPS", "WEB_APPS", "STORE_BUILDER"] (optional)
        }
    
    Returns:
        Web token information with value and URL
    """
    if not google_auth_client:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
    data = request.get_json()
    if not data or 'enterprise_name' not in data:
        return jsonify({
            'status': 'error',
            'message': 'enterprise_name is required'
        }), 400
    
    enterprise_name = data['enterprise_name'].strip()
    if not enterprise_name:
        return jsonify({
            'status': 'error',
            'message': 'enterprise_name cannot be empty'
        }), 400
    
    # Optional WebToken parameters
    parent_frame_url = data.get('parent_frame_url')
    enable_features = data.get('enable_features')
    
    try:
        result = google_auth_client.create_web_token(
            enterprise_name=enterprise_name,
            parent_frame_url=parent_frame_url,
            enable_features=enable_features
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Web token created successfully',
            'web_token': result.get('web_token', {})
        }), 200
            
    except Exception as e:
        logger.error(f"Error creating web token: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to create web token: {str(e)}'
        }), 500


@app.route('/api/v1/enterprise/register', methods=['POST'])
@error_handler
@require_jwt
def register_enterprise():
    """
    Register new enterprise using signup URL token
    
    Request body:
        {
            "signup_url_name": "signupUrls/LC...",
            "enterprise_token": "token-from-signup",
            "email": "user@example.com"
        }
    
    Returns:
        Enterprise information and saves email mapping to database
    """
    if not google_auth_client or not db:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
    data = request.get_json()
    
    if not data or 'signup_url_name' not in data or 'enterprise_token' not in data or 'email' not in data:
        return jsonify({
            'status': 'error',
            'message': 'signup_url_name, enterprise_token, and email are required'
        }), 400
    
    signup_url_name = data['signup_url_name'].strip()
    enterprise_token = data['enterprise_token'].strip()
    email = data['email'].strip()
    
    if not signup_url_name or not enterprise_token or not email:
        return jsonify({
            'status': 'error',
            'message': 'signup_url_name, enterprise_token, and email cannot be empty'
        }), 400
    
    try:
        # Create enterprise using signup token
        enterprise_result = google_auth_client.create_enterprise(
            signup_url_name=signup_url_name,
            enterprise_token=enterprise_token
        )
        
        if not enterprise_result['success']:
            return jsonify({
                'status': 'error',
                'message': 'Failed to create enterprise'
            }), 400
        
        enterprise_name = enterprise_result['enterprise_name']
        
        # Save email-enterprise mapping to database
        db.upsert_mapping(email, enterprise_name)
        
        return jsonify({
            'status': 'success',
            'message': 'Enterprise registered successfully',
            'email': email,
            'enterprise_name': enterprise_name,
            'enterprise': {
                'name': enterprise_name,
                'display_name': enterprise_result['display_name'],
                'enterprise_id': enterprise_result['enterprise_id']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in register enterprise endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Enterprise registration failed: {str(e)}'
        }), 500


@app.route('/api/v1/policies', methods=['GET'])
@error_handler
@require_jwt
def list_policies():
    """
    List all policies for an enterprise
    
    Query params:
        enterprise_name: Enterprise name (e.g., 'enterprises/LC...')
    """
    if not google_auth_client:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
    enterprise_name = request.args.get('enterprise_name')
    
    if not enterprise_name:
        return jsonify({
            'status': 'error',
            'message': 'enterprise_name query parameter is required'
        }), 400
    
    try:
        result = google_auth_client.list_policies(enterprise_name)
        
        return jsonify({
            'status': 'success',
            'message': 'Policies retrieved successfully',
            'enterprise_name': enterprise_name,
            'policies': result['policies'],
            'count': result['count']
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing policies: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to list policies: {str(e)}'
        }), 500


@app.route('/api/v1/policies', methods=['POST'])
@error_handler
@require_jwt
def create_or_update_policy():
    """
    Create or update a policy
    
    Request body:
        {
            "enterprise_name": "enterprises/LC...",
            "policy_name": "my-policy",
            "policy_body": { ... policy configuration ... }
        }
    """
    if not google_auth_client:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
    data = request.get_json()
    
    if not data or 'enterprise_name' not in data or 'policy_name' not in data or 'policy_body' not in data:
        return jsonify({
            'status': 'error',
            'message': 'enterprise_name, policy_name, and policy_body are required'
        }), 400
    
    enterprise_name = data['enterprise_name'].strip()
    policy_name = data['policy_name'].strip()
    policy_body = data['policy_body']
    
    if not enterprise_name or not policy_name:
        return jsonify({
            'status': 'error',
            'message': 'enterprise_name and policy_name cannot be empty'
        }), 400
    
    try:
        result = google_auth_client.create_or_update_policy(
            enterprise_name=enterprise_name,
            policy_name=policy_name,
            policy_body=policy_body
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Policy created/updated successfully',
            'policy': result['policy']
        }), 200
        
    except Exception as e:
        logger.error(f"Error creating/updating policy: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to create/update policy: {str(e)}'
        }), 500


@app.route('/api/v1/policies', methods=['DELETE'])
@error_handler
@require_jwt
def delete_policy():
    """
    Delete a policy
    
    Query params:
        enterprise_name: Enterprise name (e.g., 'enterprises/LC...')
        policy_name: Policy name (e.g., 'my-policy')
    """
    if not google_auth_client:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
    enterprise_name = request.args.get('enterprise_name')
    policy_name = request.args.get('policy_name')
    
    if not enterprise_name or not policy_name:
        return jsonify({
            'status': 'error',
            'message': 'enterprise_name and policy_name query parameters are required'
        }), 400
    
    try:
        result = google_auth_client.delete_policy(
            enterprise_name=enterprise_name,
            policy_name=policy_name
        )
        
        return jsonify({
            'status': 'success',
            'message': result['message']
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting policy: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to delete policy: {str(e)}'
        }), 500


@app.route('/api/v1/devices', methods=['GET'])
@error_handler
@require_jwt
def list_devices():
    """
    List all devices for an enterprise
    
    Query params:
        enterprise_name: Enterprise name (e.g., 'enterprises/LC...')
    """
    if not google_auth_client:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
    enterprise_name = request.args.get('enterprise_name')
    
    if not enterprise_name:
        return jsonify({
            'status': 'error',
            'message': 'enterprise_name query parameter is required'
        }), 400
    
    try:
        result = google_auth_client.list_devices(enterprise_name)
        
        return jsonify({
            'status': 'success',
            'message': 'Devices retrieved successfully',
            'enterprise_name': enterprise_name,
            'devices': result['devices'],
            'count': result['count']
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing devices: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to list devices: {str(e)}'
        }), 500


@app.route('/api/v1/devices/<device_id>', methods=['GET'])
@error_handler
@require_jwt
def get_device(device_id):
    """
    Get single device information
    
    Query params:
        enterprise_name: Enterprise name (e.g., 'enterprises/LC...')
    Path params:
        device_id: Device ID
    """
    if not google_auth_client:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
    enterprise_name = request.args.get('enterprise_name')
    
    if not enterprise_name:
        return jsonify({
            'status': 'error',
            'message': 'enterprise_name query parameter is required'
        }), 400
    
    try:
        result = google_auth_client.get_device(enterprise_name, device_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Device retrieved successfully',
            'device': result['device']
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting device: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get device: {str(e)}'
        }), 500


@app.route('/api/v1/devices/enrollment-token', methods=['POST'])
@error_handler
@require_jwt
def create_enrollment_token():
    """
    Create enrollment token for device provisioning
    
    Request body:
        {
            "enterprise_name": "enterprises/LC...",
            "policy_name": "my-policy"
        }
    """
    if not google_auth_client:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
    data = request.get_json()
    
    if not data or 'enterprise_name' not in data or 'policy_name' not in data:
        return jsonify({
            'status': 'error',
            'message': 'enterprise_name and policy_name are required'
        }), 400
    
    enterprise_name = data['enterprise_name'].strip()
    policy_name = data['policy_name'].strip()
    
    if not enterprise_name or not policy_name:
        return jsonify({
            'status': 'error',
            'message': 'enterprise_name and policy_name cannot be empty'
        }), 400
    
    try:
        result = google_auth_client.create_enrollment_token(
            enterprise_name=enterprise_name,
            policy_name=policy_name
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Enrollment token created successfully',
            'enrollment_token': result['enrollment_token']
        }), 200
        
    except Exception as e:
        logger.error(f"Error creating enrollment token: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to create enrollment token: {str(e)}'
        }), 500


@app.route('/api/v1/devices/<device_id>', methods=['DELETE'])
@error_handler
@require_jwt
def delete_device(device_id):
    """
    Delete a device
    
    Query params:
        enterprise_name: Enterprise name (e.g., 'enterprises/LC...')
    Path params:
        device_id: Device ID
    """
    if not google_auth_client:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
    enterprise_name = request.args.get('enterprise_name')
    
    if not enterprise_name:
        return jsonify({
            'status': 'error',
            'message': 'enterprise_name query parameter is required'
        }), 400
    
    try:
        result = google_auth_client.delete_device(
            enterprise_name=enterprise_name,
            device_id=device_id
        )
        
        return jsonify({
            'status': 'success',
            'message': result['message']
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting device: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to delete device: {str(e)}'
        }), 500


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
