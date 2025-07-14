#!/usr/bin/env python3
"""
Comprehensive JWT verification test for backend integration
"""
import requests
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

def test_jwt_verification():
    """Test JWT verification with different scenarios"""
    print("🔐 Comprehensive JWT Verification Test")
    print("=" * 50)
    
    # Get JWT secret
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    
    # Test scenarios
    test_cases = [
        {
            "name": "Valid Supabase Token",
            "payload": {
                "sub": "test-user-123",
                "email": "test@example.com",
                "role": "authenticated", 
                "aud": "authenticated",
                "iss": "supabase",
                "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
                "iat": int(datetime.utcnow().timestamp())
            }
        },
        {
            "name": "Expired Token",
            "payload": {
                "sub": "test-user-123", 
                "email": "test@example.com",
                "role": "authenticated",
                "aud": "authenticated", 
                "iss": "supabase",
                "exp": int((datetime.utcnow() - timedelta(hours=1)).timestamp()),
                "iat": int(datetime.utcnow().timestamp())
            }
        },
        {
            "name": "Missing Required Claims",
            "payload": {
                "sub": "test-user-123",
                "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
                "iat": int(datetime.utcnow().timestamp())
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Testing: {test_case['name']}")
        print("-" * 30)
        
        try:
            # Generate token
            token = jwt.encode(test_case["payload"], jwt_secret, algorithm="HS256")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test protected endpoint
            response = requests.get(f"{BASE_URL}/api/protected/test", headers=headers, timeout=5)
            print(f"   Protected endpoint: {response.status_code}")
            if response.status_code != 200:
                print(f"   Error: {response.json()}")
            else:
                print(f"   Success: {response.json()}")
            
            # Test token validation
            response = requests.post(f"{BASE_URL}/api/auth/token/validate", headers=headers, timeout=5)
            print(f"   Token validation: {response.status_code}")
            validation_result = response.json()
            print(f"   Valid: {validation_result.get('valid')}")
            if validation_result.get('error'):
                print(f"   Error: {validation_result['error']}")
                
        except Exception as e:
            print(f"   Exception: {e}")
    
    # Test token introspection
    print(f"\n🔍 Testing Token Introspection")
    print("-" * 30)
    try:
        # Valid token
        payload = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "role": "authenticated",
            "aud": "authenticated", 
            "iss": "supabase",
            "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
            "iat": int(datetime.utcnow().timestamp())
        }
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(f"{BASE_URL}/api/auth/token/introspect", headers=headers, timeout=5)
        print(f"   Introspect status: {response.status_code}")
        print(f"   Introspect result: {response.json()}")
        
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_jwt_verification()
