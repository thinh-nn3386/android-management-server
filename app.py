"""
Main Flask application for Android Management API
"""
from flask import Flask, jsonify, request
from functools import wraps
import logging
from config import Config, validate_config
from auth import GoogleAuthClient
from db import LocalDatabase

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global auth client
google_auth_client = None
local_db = None


def init_app():
    """Initialize the application"""
    global google_auth_client, local_db
    
    try:
        # Validate configuration
        validate_config()
        
        # Initialize Google Auth Client
        google_auth_client = GoogleAuthClient()
        local_db = LocalDatabase()
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


@app.route('/api/v1/login', methods=['POST'])
@error_handler
def login():
    """
    Login endpoint - check if email has registered enterprise
    
    Request body:
        {
            "email": "user@example.com",
            "callback_url": "https://your-domain.com/callback"
        }
    
    Returns:
        - If enterprise found: enterprise information
        - If not found: signup URL
    """
    if not google_auth_client or not local_db:
        return jsonify({
            'status': 'error',
            'message': 'Application not properly initialized'
        }), 503
    
    # Get email from request body
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Email is required in request body'
        }), 400
    
    email = data['email'].strip()
    callback_url = data.get('callback_url')
    
    if not email:
        return jsonify({
            'status': 'error',
            'message': 'Email cannot be empty'
        }), 400
    
    if not callback_url:
        return jsonify({
            'status': 'error',
            'message': 'Callback URL cannot be empty'
        }), 400
    
    try:
        enterprise_name = local_db.get_enterprise_name(email)
        
        if not enterprise_name:
            signup_result = google_auth_client.generate_signup_url(callback_url=callback_url)
            return jsonify({
                'status': 'success',
                'enterprise_found': False,
                'message': 'Email not registered. Please sign up.',
                'email': email,
                'signup_url': signup_result['url'],
                'signup_name': signup_result['name']
            }), 200
        
        enterprise_result = google_auth_client.list_enterprises()
        enterprises = enterprise_result.get('enterprises', [])
        
        if enterprises:
            for enterprise in enterprises:
                if enterprise['name'] == enterprise_name:
                    return jsonify({
                        'status': 'success',
                        'enterprise_found': True,
                        'message': 'Enterprise found for this email',
                        'email': email,
                        'enterprise': enterprise
                    }), 200
        
        signup_result = google_auth_client.generate_signup_url(callback_url=callback_url)
        return jsonify({
            'status': 'success',
            'enterprise_found': False,
            'message': 'Enterprise not found. Please sign up.',
            'email': email,
            'signup_url': signup_result['url'],
            'signup_name': signup_result['name']
        }), 200
            
    except Exception as e:
        logger.error(f"Error in login endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Login check failed: {str(e)}'
        }), 500


@app.route('/api/v1/enterprise/map', methods=['POST'])
@error_handler
def map_email_to_enterprise():
    """
    Map an email to a specific enterprise
    
    Request body:
        {
            "email": "user@example.com",
            "enterprise_name": "enterprises/LC037onrpk"
        }
    """
    if not local_db:
        return jsonify({
            'status': 'error',
            'message': 'Database not initialized'
        }), 503
    
    data = request.get_json()
    
    if not data or 'email' not in data or 'enterprise_name' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Email and enterprise_name are required'
        }), 400
    
    email = data['email'].strip()
    enterprise_name = data['enterprise_name'].strip()
    
    if not email or not enterprise_name:
        return jsonify({
            'status': 'error',
            'message': 'Email and enterprise_name cannot be empty'
        }), 400
    
    local_db.upsert_mapping(email, enterprise_name)
    
    return jsonify({
        'status': 'success',
        'message': 'Email mapped to enterprise successfully',
        'email': email,
        'enterprise_name': enterprise_name
    }), 200


@app.route('/api/v1/enterprise/mappings', methods=['GET'])
@error_handler
def get_all_mappings():
    """Get all email-enterprise mappings"""
    if not local_db:
        return jsonify({
            'status': 'error',
            'message': 'Database not initialized'
        }), 503
    
    mappings = local_db.list_mappings()
    
    return jsonify({
        'status': 'success',
        'mappings': mappings,
        'count': len(mappings)
    }), 200


@app.route('/api/v1/enterprise/register', methods=['POST'])
@error_handler
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
    if not google_auth_client or not local_db:
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
        local_db.upsert_mapping(email, enterprise_name)
        
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
