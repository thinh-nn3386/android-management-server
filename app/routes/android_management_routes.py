"""
Google Android Management API Routes
Handles all enterprise, policy, and device management operations
"""
from typing import Optional
from functools import wraps
from flask import Blueprint, request, jsonify
import logging

from app.repositories.enterprise_repository import EnterpriseRepository
from app.api.google_android_management import GoogleAndroidManagement
from app.utils.decorators import (
    error_handler, 
    require_jwt, 
    require_payload, 
    require_query_params
)
from app.utils.response_helpers import (
    error_response, 
    success_response
)

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize repository and Google client
enterprise_repo = EnterpriseRepository()
emm_client: Optional[GoogleAndroidManagement] = None


def init_google_client():
    """Initialize Google Android Management client"""
    global emm_client
    try:
        emm_client = GoogleAndroidManagement()
        logger.info("Google Android Management client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Google client: {str(e)}")
        raise

def require_authenticated_client(f):
    """
    Combined decorator: error_handler -> require_jwt -> require_client -> function
    """

    # Create wrapper for client check
    @wraps(f)
    def check_client(*args, **kwargs):
        if not emm_client:
            return error_response('Application not properly initialized', 503)
        return f(*args, **kwargs)

    # Chain decorators (apply from bottom to top)
    return error_handler(require_jwt(check_client))

# region Enterprise Routes
# Create Blueprint
enterprise_bp = Blueprint('enterprise', __name__, url_prefix='/api/v1/emm-android')

@enterprise_bp.route('', methods=['GET'])
@require_authenticated_client
def get_enterprise():
    """
    Get an enterprise map with the authenticated user's email

    Returns:
        An enterprise object or None
    """
    # Get email from JWT token (set by require_jwt decorator)
    email = getattr(request, 'user_email', None)

    # Check if email is mapped to an enterprise using repository
    enterprise_name = enterprise_repo.get_enterprise_name(email)

    if not enterprise_name:
        return success_response(None)

    # Get enterprise details from Google API
    enterprise = emm_client.get_enterprise(enterprise_name)
    if not enterprise:
        return success_response(None)

    return success_response(enterprise)

@enterprise_bp.route('/signup-url', methods=['POST'])
@require_authenticated_client
@require_payload("callback_url")
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
    data = request.get_json()

    callback_url = data['callback_url'].strip()
    result = emm_client.create_signup_url(callback_url)
    return success_response(result)

@enterprise_bp.route('', methods=['POST'])
@require_authenticated_client
@require_payload("signup_url_name", "enterprise_token")
def create_enterprise():
    """
    Register new enterprise using signup URL token

    Request body:
        {
            "signup_url_name": "signupUrls/LC...",
            "enterprise_token": "token-from-signup",
        }

    Returns:
        Enterprise information and saves email mapping to database
    """
    # Get email from JWT token (set by require_jwt decorator)
    email = getattr(request, 'user_email', None)

    data = request.get_json()
    signup_url_name = data['signup_url_name'].strip()
    enterprise_token = data['enterprise_token'].strip()

    # Create enterprise using signup token
    enterprise = emm_client.create_enterprise(
        signup_url_name=signup_url_name,
        enterprise_token=enterprise_token
    )

    if not enterprise:
        return error_response('Failed to create enterprise', 400)

    # Save email-enterprise mapping to database using repository
    enterprise_repo.upsert_mapping(email, enterprise.get('enterprise_name'))

    return success_response({
        'enterprise': enterprise
    })

@enterprise_bp.route('/<enterprise_name>', methods=['DELETE'])
@require_authenticated_client
def delete_enterprise(enterprise_name):
    """
    Delete an enterprise using enterprise name
    """
    emm_client.delete_enterprise(
        enterprise_name,
    )
    return success_response(None)

@enterprise_bp.route('/<enterprise_name>/web-token', methods=['POST'])
@require_authenticated_client
@require_payload("parent_frame_url")
def create_web_token(enterprise_name):
    """
    Create enterprise web token

    Request body (WebToken):
        {
            "parent_frame_url": "https://your-domain.com" ,
        }

    Returns:
        Web token information with value and URL
    """
    data = request.get_json()
    parent_frame_url = data.get('parent_frame_url').strip()

    result = emm_client.create_web_token(
        enterprise_name=enterprise_name,
        parent_frame_url=parent_frame_url
    )
    return success_response(result)

@enterprise_bp.route('/<enterprise_name>/enrollment-token', methods=['POST'])
@require_authenticated_client
@require_payload( "body_enrollment")
def create_enrollment_token(enterprise_name):
    data = request.get_json()
    body_enrollment = data.get('body_enrollment')

    result = emm_client.create_enrollment_token(
        enterprise_name=enterprise_name,
        body_enrollment=body_enrollment
    )
    return success_response(result)


# endregion


# region Policy Routes
# Create Blueprint for policies
policies_bp = Blueprint('policies', __name__, url_prefix='/api/v1/emm-android/<enterprise_name>/policies')

@policies_bp.route('', methods=['GET'])
@require_authenticated_client
def list_policies(enterprise_name):
    """
    List all policies for an enterprise
    """
    page_size = request.args.get('pageSize', default=20, type=int)
    page_token = request.args.get('pageToken', default=None)

    result = emm_client.list_policies(enterprise_name, page_size, page_token)
    return success_response(result)

@policies_bp.route('/<policy_id>', methods=['GET'])
@require_authenticated_client
def get_policy(enterprise_name, policy_id):
    """
    Delete a policy
    """
    policy = emm_client.get_policy(
        enterprise_name=enterprise_name,
        policy_id=policy_id
    )
    return success_response(policy)

@policies_bp.route('/<policy_id>', methods=['PATCH'])
@require_authenticated_client
@require_payload("policy_body")
def update_policy(enterprise_name, policy_id):
    """
    Create or update a policy
    """
    data = request.get_json()
    policy_body = data['policy_body']

    policy = emm_client.update_policy(
        enterprise_name=enterprise_name,
        policy_id=policy_id,
        policy_body=policy_body
    )

    return success_response(policy)


@policies_bp.route('/<policy_id>', methods=['DELETE'])
@require_authenticated_client
def delete_policy(enterprise_name, policy_id):
    emm_client.delete_policy(
        enterprise_name=enterprise_name,
        policy_id=policy_id
    )
    return success_response(None)


@policies_bp.route('/<policy_id>:modifyPolicyApplications', methods=['POST'])
@require_authenticated_client
@require_payload("modify_body")
def modify_policy_applications(enterprise_name, policy_id):
    data = request.get_json()
    modify_body = data['modify_body']

    emm_client.modify_policy_applications(
        enterprise_name=enterprise_name,
        policy_id=policy_id,
        modify_body=modify_body
    )
    return success_response(None)

@policies_bp.route('/<policy_id>:removePolicyApplications', methods=['POST'])
@require_authenticated_client
@require_payload("remove_body")
def remove_policy_applications(enterprise_name, policy_id):
    data = request.get_json()
    remove_body = data['remove_body']

    emm_client.remove_policy_applications(
        enterprise_name=enterprise_name,
        policy_id=policy_id,
        remove_body=remove_body
    )
    return success_response(None)

# endregion

# Create Blueprint for devices
devices_bp = Blueprint('devices', __name__, url_prefix='/api/v1/emm-android/<enterprise_name>/devices')

@devices_bp.route('', methods=['GET'])
@require_authenticated_client
def list_devices(enterprise_name):
    """
    List all devices for an enterprise
    """
    page_size = request.args.get('pageSize', default=20, type=int)
    page_token = request.args.get('pageToken', default=None)

    result = emm_client.list_devices(enterprise_name, page_size, page_token)

    return success_response(result)


@devices_bp.route('/<device_id>', methods=['GET'])
@require_authenticated_client
def get_device(enterprise_name, device_id):
    """
    Get single device information
    """
    result = emm_client.get_device(enterprise_name, device_id)
    return success_response(result)

@devices_bp.route('/<device_id>', methods=['DELETE'])
@require_authenticated_client
def delete_device(enterprise_name, device_id):
    emm_client.delete_device(
        enterprise_name=enterprise_name,
        device_id=device_id
    )
    return success_response(None)


