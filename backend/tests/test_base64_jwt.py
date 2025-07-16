#!/usr/bin/env python3
"""
Test JWT with base64 decoded secret
"""
import requests
import jwt
import os
import base64
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

def test_with_decoded_secret():
    """Test JWT with properly decoded base64 secret"""
    print("🔐 Testing JWT with Base64 Decoded Secret")
    print("=" * 50)
    
    # Get and decode the JWT secret
    jwt_secret_raw = os.getenv("SUPABASE_JWT_SECRET")
    jwt_secret = base64.b64decode(jwt_secret_raw)
    
    print(f"Raw secret length: {len(jwt_secret_raw)}")
    print(f"Decoded secret length: {len(jwt_secret)}")
    
    # Create a valid token
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
    print(f"Generated token: {token[:50]}...")
    
    # Test local decode first
    try:
        decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"], audience="authenticated")
        print("✅ Local decode successful")
        print(f"   User: {decoded['email']}")
    except Exception as e:
        print(f"❌ Local decode failed: {e}")
        return
    
    # Test server endpoints
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧪 Testing Server Endpoints")
    print("-" * 30)
    
    # Test token validation
    response = requests.post(f"{BASE_URL}/api/auth/token/validate", headers=headers, timeout=5)
    result = response.json()
    print(f"Token validation: {result.get('valid')}")
    if result.get('error'):
        print(f"Error: {result['error']}")
    else:
        print(f"User: {result.get('user', {}).get('email')}")
    
    # Test protected endpoint
    response = requests.get(f"{BASE_URL}/api/protected/test", headers=headers, timeout=5)
    print(f"Protected endpoint: {response.status_code}")
    if response.status_code == 200:
        print(f"Success: {response.json()}")
    else:
        print(f"Error: {response.json()}")
    
    # Test introspection
    response = requests.post(f"{BASE_URL}/api/auth/token/introspect", headers=headers, timeout=5)
    result = response.json()
    print(f"Token introspection active: {result.get('active')}")
    if result.get('active'):
        print(f"Token type: {result.get('token_type')}")
        print(f"Subject: {result.get('sub')}")

if __name__ == "__main__":
    test_with_decoded_secret()
