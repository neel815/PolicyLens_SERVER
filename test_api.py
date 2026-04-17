#!/usr/bin/env python3
"""
Test script to verify backend API endpoints are working.
Tests auth and policy endpoints.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("\n🔍 Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_register():
    """Test user registration."""
    print("\n🔍 Testing /auth/register endpoint...")
    user_data = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=user_data
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Registration successful!")
        print(f"   User ID: {data['user']['id']}")
        print(f"   Token: {data['access_token'][:20]}...")
        return data['access_token'], data['user']['id']
    else:
        print(f"❌ Registration failed: {response.text}")
        return None, None

def test_policies(token):
    """Test GET /api/policies endpoint."""
    print("\n🔍 Testing /api/policies endpoint...")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/policies",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    if response.ok:
        data = response.json()
        print(f"✅ Policies fetched successfully!")
        print(f"   Count: {len(data)}")
        print(f"   Data: {json.dumps(data, indent=2)}")
        return True
    else:
        print(f"❌ Failed to fetch policies: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_without_auth():
    """Test /api/policies without auth."""
    print("\n🔍 Testing /api/policies WITHOUT auth (should fail)...")
    response = requests.get(f"{BASE_URL}/api/policies")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 403:
        print(f"✅ Correctly rejected unauthenticated request")
        return True
    else:
        print(f"⚠️  Expected 403, got {response.status_code}")
        return False

if __name__ == "__main__":
    print("🚀 Starting API tests...")
    print(f"Base URL: {BASE_URL}")
    
    # Test health
    if not test_health():
        print("❌ Health check failed! Backend may not be running.")
        exit(1)
    
    # Test registration
    token, user_id = test_register()
    if not token:
        print("❌ Registration failed!")
        exit(1)
    
    # Test without auth
    test_without_auth()
    
    # Test policies with auth
    if test_policies(token):
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Policy fetch test failed!")
        exit(1)
