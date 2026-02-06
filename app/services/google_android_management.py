"""
Google Cloud authentication utilities
"""
import os
import certifi
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import Config


class GoogleAndroidManagement:
    """Manages Google Android management API clients"""
    
    def __init__(self):
        self.credentials = None
        self.service = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Google credentials from service account JSON"""
        try:
            # Set up SSL certificate handling
            ca_bundle_path = certifi.where()
            os.environ['SSL_CERT_FILE'] = ca_bundle_path
            os.environ['REQUESTS_CA_BUNDLE'] = ca_bundle_path

            service_account_path = Config.SERVICE_ACCOUNT_JSON
            
            if not service_account_path or not os.path.exists(service_account_path):
                raise FileNotFoundError(f"Service account file not found: {service_account_path}")
            
            # Load service account credentials
            self.credentials = service_account.Credentials.from_service_account_file(
                service_account_path,
                scopes=[
                    'https://www.googleapis.com/auth/androidmanagement',
                    'https://www.googleapis.com/auth/cloud-platform'
                ]
            )
            
            # Build Android Management API client with credentials
            self.service = build(
                'androidmanagement',
                'v1',
                credentials=self.credentials,
                static_discovery=False
            )
            
        except FileNotFoundError as e:
            raise Exception(f"Failed to initialize Google Auth: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to initialize Google credentials: {str(e)}")
    
    def check_authentication_status(self):
        """
        Check if service account authentication is valid
        
        Returns:
            dict: Authentication status and details
        """
        try:
            if not self.credentials or not self.service:
                return {
                    'status': 'error',
                    'authenticated': False,
                    'message': 'Credentials not initialized'
                }
            
            # Verify credentials by checking the service account email
            service_account_email = self.credentials.service_account_email
            project_id = self.credentials.project_id
            
            return {
                'status': 'success',
                'authenticated': True,
                'message': 'Service account authenticated successfully',
                'service_account_email': service_account_email,
                'project_id': project_id,
                'details': {
                    'scopes': self.credentials.scopes
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'authenticated': False,
                'message': f'Authentication check failed: {str(e)}',
                'error_type': type(e).__name__
            }
    
    def list_enterprises(self):
        """
        List all enterprises in the project
        
        Returns:
            dict: List of all enterprises
        """
        try:
            if not self.service:
                raise Exception("Service not initialized")
            
            request = self.service.enterprises().list(projectId=Config.CLOUD_PROJECT_ID)
            result = request.execute()
            
            enterprises = result.get('enterprises', [])
            
            if enterprises:
                return {
                    'found': True,
                    'enterprises': [
                        {
                            'name': ent.get('name'),
                            'display_name': ent.get('enterpriseDisplayName'),
                            'enterprise_id': ent.get('name', '').split('/')[-1]
                        }
                        for ent in enterprises
                    ]
                }
            
            return {'found': False, 'enterprises': []}
            
        except Exception as e:
            raise Exception(f"Failed to list enterprises: {str(e)}")
    
    def generate_signup_url(self, callback_url=None):
        """
        Generate enterprise signup URL
        
        Args:
            callback_url: Optional callback URL after signup
            
        Returns:
            dict: Contains 'signup_url' and 'signup_name'
        """
        try:
            if not self.service:
                raise Exception("Service not initialized")
            
            resolved_callback_url = callback_url or f"http://localhost:{Config.PORT}/api/v1/enterprise/callback"
            
            request = self.service.signupUrls().create(
                projectId=Config.CLOUD_PROJECT_ID,
                callbackUrl=resolved_callback_url
            )
            result = request.execute()
            
            return {
                'url': result.get('url', ''),
                'name': result.get('name', '')
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate signup URL: {str(e)}")
    
    def create_enterprise(self, signup_url_name, enterprise_token):
        """
        Create enterprise for organization using signup URL token
        
        Args:
            signup_url_name: The signup URL name (e.g., 'signupUrls/LC...')
            enterprise_token: The token from signup completion
            
        Returns:
            dict: Enterprise information including name and display_name
        """
        try:
            if not self.service:
                raise Exception("Service not initialized")
            
            # Create enterprise using signup URL token
            body = {
                
            }
            
            request = self.service.enterprises().create(
                projectId=Config.CLOUD_PROJECT_ID,
                signupUrlName=signup_url_name,
                enterpriseToken=enterprise_token,
                body=body
            )
            result = request.execute()
            
            return {
                'success': True,
                'enterprise_name': result.get('name', ''),
                'display_name': result.get('enterpriseDisplayName', ''),
                'enterprise_id': result.get('name', '').split('/')[-1]
            }
            
        except Exception as e:
            raise Exception(f"Failed to create enterprise: {str(e)}")

    def create_web_token(self, enterprise_name, parent_frame_url=None, enable_features=None):
        """
        Create a web token for enterprise enrollment UI
        
        Args:
            enterprise_name: Enterprise name (e.g., 'enterprises/LC...')
            parent_frame_url: Optional URL of the parent frame hosting the iframe
            enable_features: Optional list of features to enable.
                           Options: 'PLAY_SEARCH', 'PRIVATE_APPS', 'WEB_APPS', 'STORE_BUILDER'
                           If not specified, all features are enabled by default.
        Returns:
            dict: Web token information with token value and URL
        """
        try:
            if not self.service:
                raise Exception("Service not initialized")
            
            # Build WebToken request body
            request_body = {
                "permissions": [
                    "APPROVE_APPS"
                ],
                "parentFrameUrl": "https://localhost:3000/home/playstore",
                "enabledFeatures": [
                   "FEATURE_UNSPECIFIED"   
                ]
            }
            
            request = self.service.enterprises().webTokens().create(
                parent=enterprise_name,
                body=request_body
            )
            result = request.execute()
            return {
                'success': True,
                'web_token': result
            }
            
        except Exception as e:
            raise Exception(f"Failed to create web token: {str(e)}")
    
    def list_policies(self, enterprise_name):
        """
        List all policies for an enterprise
        
        Args:
            enterprise_name: Enterprise name (e.g., 'enterprises/LC...')
            
        Returns:
            dict: List of policies
        """
        try:
            if not self.service:
                raise Exception("Service not initialized")
            
            request = self.service.enterprises().policies().list(parent=enterprise_name)
            result = request.execute()
            
            policies = result.get('policies', [])
            
            return {
                'success': True,
                'policies': [
                    {
                        'name': policy.get('name', ''),
                        'policy_id': policy.get('name', '').split('/')[-1],
                        'version': policy.get('version', ''),
                        'applications': policy.get('applications', [])
                    }
                    for policy in policies
                ],
                'count': len(policies)
            }
            
        except Exception as e:
            raise Exception(f"Failed to list policies: {str(e)}")
    
    def create_or_update_policy(self, enterprise_name, policy_name, policy_body):
        """
        Create or update a policy
        
        Args:
            enterprise_name: Enterprise name (e.g., 'enterprises/LC...')
            policy_name: Policy name (e.g., 'my-policy')
            policy_body: Policy configuration as dict
            
        Returns:
            dict: Policy information
        """
        try:
            if not self.service:
                raise Exception("Service not initialized")
            
            parent = enterprise_name
            name = f"{enterprise_name}/policies/{policy_name}"
            
            request = self.service.enterprises().policies().patch(
                name=name,
                body=policy_body
            )
            result = request.execute()
            
            return {
                'success': True,
                'policy': {
                    'name': result.get('name', ''),
                    'policy_id': result.get('name', '').split('/')[-1],
                    'version': result.get('version', ''),
                    'applications': result.get('applications', [])
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to create/update policy: {str(e)}")
    
    def delete_policy(self, enterprise_name, policy_name):
        """
        Delete a policy
        
        Args:
            enterprise_name: Enterprise name (e.g., 'enterprises/LC...')
            policy_name: Policy name (e.g., 'my-policy')
            
        Returns:
            dict: Success status
        """
        try:
            if not self.service:
                raise Exception("Service not initialized")
            
            name = f"{enterprise_name}/policies/{policy_name}"
            
            request = self.service.enterprises().policies().delete(name=name)
            request.execute()
            
            
            return {
                'success': True,
                'message': f'Policy {policy_name} deleted successfully'
            }
            
        except Exception as e:
            raise Exception(f"Failed to delete policy: {str(e)}")
    
    def list_devices(self, enterprise_name):
        """
        List all devices for an enterprise
        
        Args:
            enterprise_name: Enterprise name (e.g., 'enterprises/LC...')
            
        Returns:
            dict: List of devices
        """
        try:
            if not self.service:
                raise Exception("Service not initialized")
            
            request = self.service.enterprises().devices().list(parent=enterprise_name)
            result = request.execute()
            
            devices = result.get('devices', [])
            
            return {
                'success': True,
                'devices': [
                    {
                        'name': device.get('name', ''),
                        'device_id': device.get('name', '').split('/')[-1],
                        'state': device.get('state', ''),
                        'appliedPolicyName': device.get('appliedPolicyName', ''),
                        'appliedState': device.get('appliedState', ''),
                        'hardwareInfo': device.get('hardwareInfo', {}),
                        'policyName': device.get('policyName', '')
                    }
                    for device in devices
                ],
                'count': len(devices)
            }
            
        except Exception as e:
            raise Exception(f"Failed to list devices: {str(e)}")
    
    def get_device(self, enterprise_name, device_id):
        """
        Get single device information
        
        Args:
            enterprise_name: Enterprise name (e.g., 'enterprises/LC...')
            device_id: Device ID
            
        Returns:
            dict: Device information
        """
        try:
            if not self.service:
                raise Exception("Service not initialized")
            
            name = f"{enterprise_name}/devices/{device_id}"
            request = self.service.enterprises().devices().get(name=name)
            result = request.execute()
            
            return {
                'success': True,
                'device': {
                    'name': result.get('name', ''),
                    'device_id': result.get('name', '').split('/')[-1],
                    'state': result.get('state', ''),
                    'appliedPolicyName': result.get('appliedPolicyName', ''),
                    'appliedState': result.get('appliedState', ''),
                    'hardwareInfo': result.get('hardwareInfo', {}),
                    'softwareInfo': result.get('softwareInfo', {}),
                    'memoryInfo': result.get('memoryInfo', {}),
                    'networkInfo': result.get('networkInfo', {}),
                    'policyName': result.get('policyName', ''),
                    'enrollmentTime': result.get('enrollmentTime', ''),
                    'lastStatusReportTime': result.get('lastStatusReportTime', '')
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to get device: {str(e)}")
    
    def create_enrollment_token(self, enterprise_name, policy_name):
        """
        Create enrollment token for device provisioning
        
        Args:
            enterprise_name: Enterprise name (e.g., 'enterprises/LC...')
            policy_name: Policy name to apply (e.g., 'my-policy')
            
        Returns:
            dict: Enrollment token information
        """
        try:
            if not self.service:
                raise Exception("Service not initialized")
            
            body = {
                'policyName': f"{enterprise_name}/policies/{policy_name}"
            }
            
            request = self.service.enterprises().enrollmentTokens().create(
                parent=enterprise_name,
                body=body
            )
            result = request.execute()
            
            return {
                'success': True,
                'enrollment_token': {
                    'name': result.get('name', ''),
                    'value': result.get('value', ''),
                    'qrCode': result.get('qrCode', ''),
                    'policyName': result.get('policyName', ''),
                    'expirationTimestamp': result.get('expirationTimestamp', '')
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to create enrollment token: {str(e)}")
    
    def delete_device(self, enterprise_name, device_id):
        """
        Delete a device from enterprise
        
        Args:
            enterprise_name: Enterprise name (e.g., 'enterprises/LC...')
            device_id: Device ID
            
        Returns:
            dict: Success status
        """
        try:
            if not self.service:
                raise Exception("Service not initialized")
            
            name = f"{enterprise_name}/devices/{device_id}"
            request = self.service.enterprises().devices().delete(name=name)
            request.execute()
            
            return {
                'success': True,
                'message': f'Device {device_id} deleted successfully'
            }
            
        except Exception as e:
            raise Exception(f"Failed to delete device: {str(e)}")




