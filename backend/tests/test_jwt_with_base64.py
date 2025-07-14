#!/usr/bin/env python3
"""
Test JWT verification with corrected base64 secret handling
"""
import requests
import jwt
import os
import base64
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

def test_jwt_with_base64_secret():
    """Test JWT verification with properly decoded base64 secret"""
    print("🔐 Testing JWT with Base64 Secret Fix")
    print("=" * 45)
    
    # Get the JWT secret and decode it properly
    jwt_secret_raw = os.getenv("SUPABASE_JWT_SECRET")
    if not jwt_secret_raw:
        print("❌ SUPABASE_JWT_SECRET not found")
        return
    
    try:
        jwt_secret = base64.b64decode(jwt_secret_raw)
        print(f"✅ Successfully decoded JWT secret (length: {len(jwt_secret)})")
    except Exception as e:
        print(f"❌ Failed to decode JWT secret: {e}")
        return
    
    # Test 1: Create and validate token locally
    print(f"\n1. Local JWT Token Test")
    print("-" * 25)
    
    payload = {
        "sub": "test-user-123",
        "email": "test@example.com",
        "role": "authenticated",
        "aud": "authenticated",
        "iss": "supabase",
        "exp": int((datetime.utcnow() + timedelta(hours=24)).timestamp()),  # 24 hours to avoid clock skew
        "iat": int((datetime.utcnow() - timedelta(minutes=5)).timestamp())   # 5 minutes ago to avoid clock skew
    }
    
    try:
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")
        print(f"   Generated token: {token[:50]}...")
        
        # Decode locally to verify
        decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"], audience="authenticated")
        print(f"   ✅ Local decode successful: {decoded['email']}")
        
    except Exception as e:
        print(f"   ❌ Local JWT test failed: {e}")
        return
    
    # Test 2: Test with server
    print(f"\n2. Server JWT Validation Test")
    print("-" * 30)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test token validation endpoint
    try:
        response = requests.post(f"{BASE_URL}/api/auth/token/validate", headers=headers, timeout=5)
        result = response.json()
        print(f"   Token validation status: {response.status_code}")
        print(f"   Valid: {result.get('valid')}")
        if result.get('error'):
            print(f"   Error: {result['error']}")
        else:
            print(f"   User: {result.get('user', {}).get('email')}")
            
    except Exception as e:
        print(f"   ❌ Server validation failed: {e}")
    
    # Test 3: Test protected endpoint
    print(f"\n3. Protected Endpoint Test")
    print("-" * 26)
    
    try:
        response = requests.get(f"{BASE_URL}/api/protected/test", headers=headers, timeout=5)
        print(f"   Protected endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Protected endpoint accessible")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Protected endpoint failed: {response.json()}")
            
    except Exception as e:
        print(f"   ❌ Protected endpoint test failed: {e}")
    
    # Test 4: Token introspection
    print(f"\n4. Token Introspection Test")
    print("-" * 27)
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/token/introspect", headers=headers, timeout=5)
        result = response.json()
        print(f"   Introspection status: {response.status_code}")
        print(f"   Active: {result.get('active')}")
        if result.get('active'):
            print(f"   Token type: {result.get('token_type')}")
            print(f"   Subject: {result.get('sub')}")
            print(f"   Email: {result.get('email')}")
        else:
            print(f"   Error: {result.get('error')}")
            
    except Exception as e:
        print(f"   ❌ Introspection test failed: {e}")

if __name__ == "__main__":
    test_jwt_with_base64_secret()
