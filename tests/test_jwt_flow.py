#!/usr/bin/env python3
"""
Test script for JWT authentication flow
"""
import requests
import json

BASE_URL = "http://localhost:8088"

def test_auth_flow():
    print("=" * 60)
    print("Testing JWT Authentication Flow")
    print("=" * 60)
    
    # Test data
    test_email = "test@example.com"
    test_password = "testpassword123"
    
    # 1. Register user
    print("\n1. Registering new user...")
    register_payload = {
        "email": test_email,
        "password": test_password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/register",
            json=register_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ User registered successfully")
        elif response.status_code == 400 and "already exists" in response.json().get("message", ""):
            print("ℹ️  User already exists, continuing with login")
        else:
            print("❌ Registration failed")
            return
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return
    
    # 2. Login to get JWT token
    print("\n2. Logging in to get JWT token...")
    login_payload = {
        "email": test_email,
        "password": test_password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/login",
            json=login_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code != 200:
            print("❌ Login failed")
            return
        
        token = response_data.get("token")
        if not token:
            print("❌ No token received")
            return
        
        print(f"✅ Login successful. Token: {token[:50]}...")
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return
    
    # 3. Test protected endpoint with JWT
    print("\n3. Testing protected endpoint with JWT token...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test /api/v1/auth/status
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/status",
            headers=headers
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Protected endpoint accessed successfully")
        else:
            print("❌ Failed to access protected endpoint")
    except Exception as e:
        print(f"❌ Error accessing protected endpoint: {e}")
        return
    
    # 4. Test protected endpoint WITHOUT JWT (should fail)
    print("\n4. Testing protected endpoint WITHOUT JWT token...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected request without JWT")
        else:
            print("❌ Should have rejected request without JWT")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 5. Test enterprise login with JWT
    print("\n5. Testing enterprise login with JWT token...")
    enterprise_payload = {
        "callback_url": "https://test.example.com/callback"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/enterprise/login",
            json=enterprise_payload,
            headers=headers
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code in [200, 404]:  # 404 is expected if no enterprise found
            print("✅ Enterprise login endpoint working with JWT")
        else:
            print("❌ Enterprise login failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("JWT Authentication Flow Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    print("\nMake sure the server is running on http://localhost:8088")
    print("Press Ctrl+C to cancel, or Enter to continue...")
    try:
        input()
        test_auth_flow()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
