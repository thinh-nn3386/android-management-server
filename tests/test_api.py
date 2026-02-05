#!/usr/bin/env python3
"""
Test script for Android Management API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8088"

def test_auth_status():
    """Test authentication status endpoint"""
    print("\n=== Testing Auth Status ===")
    response = requests.get(f"{BASE_URL}/api/v1/auth/status")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_login(email):
    """Test login endpoint"""
    print(f"\n=== Testing Login with email: {email} ===")
    response = requests.post(
        f"{BASE_URL}/api/v1/login",
        json={"email": email},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_health():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("Android Management API - Test Suite")
    print("=" * 50)
    
    # Test health check
    test_health()
    
    # Test auth status
    test_auth_status()
    
    # Test login with sample email
    test_login("test@example.com")
    
    # Test login with another email
    test_login("admin@company.com")
    
    print("\n" + "=" * 50)
    print("Tests completed!")
