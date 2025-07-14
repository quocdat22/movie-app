#!/usr/bin/env python3
"""
Simple test script for JWT verification issues
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Test the JWT verification fixes"""
    print("🔧 Testing JWT Verification Fixes")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/api/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Auth session endpoint
    print("\n2. Testing auth session endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/session", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Protected endpoint without token
    print("\n3. Testing protected endpoint without token...")
    try:
        response = requests.get(f"{BASE_URL}/api/protected/test", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Protected endpoint with invalid token
    print("\n4. Testing protected endpoint with invalid token...")
    try:
        headers = {"Authorization": "Bearer invalid_token_12345"}
        response = requests.get(f"{BASE_URL}/api/protected/test", headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Token validation endpoint
    print("\n5. Testing token validation endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/token/validate", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 6: Test with a valid JWT token structure (for testing purposes)
    print("\n6. Testing with valid JWT token structure...")
    try:
        # Create a test token with proper structure (this is just for testing the parser)
        import jwt
        import os
        from datetime import datetime, timedelta
        
        # Use the secret from the environment file
        secret = "UGwZyXlazBlFeAHDhlIEdFUWPrgqEAgQzEoTP1NFavPUoJ9DRhN9DziQEaCEMK4D8IQRAwYoLaUiql8jMHQBrA=="
        
        # Create a test payload
        payload = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "role": "authenticated",
            "aud": "authenticated",
            "iss": "supabase",
            "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
            "iat": int(datetime.utcnow().timestamp())
        }
        
        test_token = jwt.encode(payload, secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {test_token}"}
        
        # Test protected endpoint with valid token
        response = requests.get(f"{BASE_URL}/api/protected/test", headers=headers, timeout=5)
        print(f"   Protected endpoint status: {response.status_code}")
        print(f"   Protected endpoint response: {response.json()}")
        
        # Test token validation with valid token
        response = requests.post(f"{BASE_URL}/api/auth/token/validate", headers=headers, timeout=5)
        print(f"   Token validation status: {response.status_code}")
        print(f"   Token validation response: {response.json()}")
        
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_endpoints()
