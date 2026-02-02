"""
Google Cloud authentication utilities
"""
import json
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
            
            if not os.path.exists(service_account_path):
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
            if not self.credentials:
                return {
                    'status': 'error',
                    'authenticated': False,
                    'message': 'Credentials not initialized'
                }
            
            # Verify credentials by checking the service account email
            service_account_email = self.credentials.service_account_email
            project_id = self.credentials.project_id
            
            # Try to make a simple API call to verify authentication
            request = self.service.enterprises().list(projectId=Config.CLOUD_PROJECT_ID)
            result = request.execute()
            
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
