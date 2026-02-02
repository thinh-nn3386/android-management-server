"""
Google Cloud authentication utilities
"""
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import Config


class GoogleAuthClient:
    """Manages Google Cloud authentication and API clients"""
    
    def __init__(self):
        self.credentials = None
        self.service = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Google credentials from service account JSON"""
        try:
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
            
            # Build Android Management API client
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
    
    def get_service(self):
        """Get the Android Management API service"""
        return self.service
    
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
                'displayName': 'Enterprise'
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
                'display_name': result.get('displayName', ''),
                'enterprise_id': result.get('name', '').split('/')[-1]
            }
            
        except Exception as e:
            raise Exception(f"Failed to create enterprise: {str(e)}")

