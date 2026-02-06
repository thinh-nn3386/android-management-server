"""
Google Android Management utilities
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

    # region Enterprises

    def list_enterprises(self, page_size=20, page_token=None):
        """List all enterprises in the project"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            return self.service.enterprises().list(
                projectId=Config.CLOUD_PROJECT_ID,
                pageSize=page_size,
                pageToken=page_token,
                view="BASIC"
            ).execute()

        except Exception as e:
            raise Exception(f"Failed to list enterprises: {str(e)}")

    def get_enterprise(self, enterprise_name):
        """Get enterprise details by name"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            return self.service.enterprises().get(name=enterprise_name).execute()
        except Exception as e:
            raise Exception(f"Failed to get enterprise info: {str(e)}")

    def delete_enterprise(self, enterprise_name):
        """Delete an enterprise"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            return self.service.enterprises().delete(name=enterprise_name).execute()
        except Exception as e:
            raise Exception(f"Failed to delete enterprise: {str(e)}")

    def create_signup_url(self, callback_url):
        """Generate enterprise signup URL"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            return self.service.signupUrls().create(
                projectId=Config.CLOUD_PROJECT_ID,
                callbackUrl=callback_url
            ).execute()

        except Exception as e:
            raise Exception(f"Failed to generate signup URL: {str(e)}")

    def create_enterprise(self, signup_url_name, enterprise_token):
        """Create a new enterprise"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            body = {}
            return self.service.enterprises().create(
                projectId=Config.CLOUD_PROJECT_ID,
                signupUrlName=signup_url_name,
                enterpriseToken=enterprise_token,
                body=body
            ).execute()

        except Exception as e:
            raise Exception(f"Failed to create enterprise: {str(e)}")

    # endregion

    # region Web token

    def create_web_token(self, enterprise_name, parent_frame_url):
        """Create a web token for enterprise management"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            request_body = {
                "parentFrameUrl": parent_frame_url,
                "enabledFeatures": [
                   "FEATURE_UNSPECIFIED"
                ]
            }
            return self.service.enterprises().webTokens().create(
                parent=enterprise_name,
                body=request_body
            ).execute()

        except Exception as e:
            raise Exception(f"Failed to create web token: {str(e)}")

    # endregion

    # region Policies

    def list_policies(self, enterprise_name, page_size=20, page_token=None):
        """List all policies for an enterprise"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            return self.service.enterprises().policies().list(
                parent=enterprise_name,
                pageSize=page_size,
                pageToken=page_token
            ).execute()

        except Exception as e:
            raise Exception(f"Failed to list policies: {str(e)}")

    def get_policy(self, enterprise_name, policy_name):
        """Get policy details"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            name = f"{enterprise_name}/policies/{policy_name}"
            return self.service.enterprises().policies().get(name=name).execute()

        except Exception as e:
            raise Exception(f"Failed to get policy: {str(e)}")

    def update_policy(self, enterprise_name, policy_name, policy_body):
        """Update an existing policy"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            name = f"{enterprise_name}/policies/{policy_name}"
            return self.service.enterprises().policies().patch(
                name=name,
                body=policy_body
            ).execute()

        except Exception as e:
            raise Exception(f"Failed to update policy: {str(e)}")

    def delete_policy(self, enterprise_name, policy_name):
        """Delete a policy"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            name = f"{enterprise_name}/policies/{policy_name}"
            return self.service.enterprises().policies().delete(name=name).execute()

        except Exception as e:
            raise Exception(f"Failed to delete policy: {str(e)}")

    def add_policy_applications(self, enterprise_name, policy_name, modify_body):
        """Add applications to a policy"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            name = f"{enterprise_name}/policies/{policy_name}"
            return self.service.enterprises().policies().modifyPolicyApplications(
                name=name,
                body=modify_body
            ).execute()

        except Exception as e:
            raise Exception(f"Failed to add policy applications: {str(e)}")

    def remove_policy_applications(self, enterprise_name, policy_name, remove_body):
        """Remove applications from a policy"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            name = f"{enterprise_name}/policies/{policy_name}"
            return self.service.enterprises().policies().removePolicyApplications(
                name=name,
                body=remove_body
            ).execute()

        except Exception as e:
            raise Exception(f"Failed to remove policy applications: {str(e)}")

    # endregion

    # region Applications

    def get_application(self, enterprise_name, package_name):
        """Get application details by package name"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            name = f"{enterprise_name}/applications/{package_name}"
            return self.service.enterprises().applications().get(name=name).execute()

        except Exception as e:
            raise Exception(f"Failed to get application: {str(e)}")

    # endregion

    # region Devices

    def list_devices(self, enterprise_name):
        """List all devices for an enterprise"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            return self.service.enterprises().devices().list(parent=enterprise_name).execute()

        except Exception as e:
            raise Exception(f"Failed to list devices: {str(e)}")

    def get_device(self, enterprise_name, device_id):
        """Get device details by ID"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            name = f"{enterprise_name}/devices/{device_id}"
            return self.service.enterprises().devices().get(name=name).execute()

        except Exception as e:
            raise Exception(f"Failed to get device: {str(e)}")

    def update_device(self, enterprise_name, device_id, patch_body):
        """Update device configuration"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            name = f"{enterprise_name}/devices/{device_id}"
            return self.service.enterprises().devices().patch(
                name=name,
                body=patch_body
            ).execute()

        except Exception as e:
            raise Exception(f"Failed to update device: {str(e)}")

    def delete_device(self, enterprise_name, device_id):
        """Delete a device"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            name = f"{enterprise_name}/devices/{device_id}"
            return self.service.enterprises().devices().delete(name=name).execute()

        except Exception as e:
            raise Exception(f"Failed to delete device: {str(e)}")

    def issue_device_command(self, enterprise_name, device_id, command_body):
        """Issue a command to a device"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            name = f"{enterprise_name}/devices/{device_id}"
            return self.service.enterprises().devices().issueCommand(
                name=name,
                body=command_body
            ).execute()

        except Exception as e:
            raise Exception(f"Failed to issue device command: {str(e)}")

    # endregion

    # region Enrollment Tokens

    def list_enrollment_tokens(self, enterprise_name):
        """List all enrollment tokens for an enterprise"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            return self.service.enterprises().enrollmentTokens().list(
                parent=enterprise_name
            ).execute()

        except Exception as e:
            raise Exception(f"Failed to list enrollment tokens: {str(e)}")

    def get_enrollment_token(self, enterprise_name, enrollment_token_id):
        """Get enrollment token details"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            name = f"{enterprise_name}/enrollmentTokens/{enrollment_token_id}"
            return self.service.enterprises().enrollmentTokens().get(
                name=name
            ).execute()

        except Exception as e:
            raise Exception(f"Failed to get enrollment token: {str(e)}")

    def create_enrollment_token(self, enterprise_name, body_enrollment):
        """Create a new enrollment token"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            return self.service.enterprises().enrollmentTokens().create(
                parent=enterprise_name,
                body=body_enrollment
            ).execute()

        except Exception as e:
            raise Exception(f"Failed to create enrollment token: {str(e)}")

    def delete_enrollment_token(self, enterprise_name, enrollment_token_id):
        """Delete an enrollment token"""
        try:
            if not self.service:
                raise Exception("Service not initialized")

            name = f"{enterprise_name}/enrollmentTokens/{enrollment_token_id}"
            return self.service.enterprises().enrollmentTokens().delete(
                name=name
            ).execute()

        except Exception as e:
            raise Exception(f"Failed to delete enrollment token: {str(e)}")

    # endregion