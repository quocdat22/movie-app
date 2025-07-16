#!/usr/bin/env python3
"""
Final test to verify JWT verification fixes and API path corrections
"""
import requests
import jwt
import os
import base64
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

def test_fixed_jwt_and_api_paths():
    """Test that JWT verification and API paths are working correctly"""
    print("🎯 Final JWT & API Path Verification Test")
    print("=" * 45)
    
    # Test 1: Check API paths are correct (no double /api)
    print("\n1. Testing API Path Structure")
    print("-" * 30)
    
    endpoints_to_test = [
        ("/api/health", "Health endpoint"),
        ("/api/auth/session", "Auth session endpoint"),
        ("/debug/env", "Debug environment endpoint")
    ]
    
    for endpoint, description in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code in [200, 401]:  # 401 is OK for protected endpoints
                print(f"   ✅ {description}: {response.status_code}")
            else:
                print(f"   ❌ {description}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {description}: Error - {e}")
    
    # Test 2: JWT Verification with corrected base64 secret
    print("\n2. Testing JWT Verification")
    print("-" * 28)
    
    try:
        # Get and decode JWT secret
        jwt_secret_raw = os.getenv("SUPABASE_JWT_SECRET")
        jwt_secret = base64.b64decode(jwt_secret_raw)
        
        # Create valid test token
        payload = {
            "sub": "final-test-user",
            "email": "final@test.com",
            "role": "authenticated",
            "aud": "authenticated",
            "iss": "supabase",
            "exp": int((datetime.utcnow() + timedelta(hours=24)).timestamp()),
            "iat": int((datetime.utcnow() - timedelta(minutes=5)).timestamp()),
            "app_metadata": {},
            "user_metadata": {}
        }
        
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test token validation endpoint
        response = requests.post(f"{BASE_URL}/api/auth/token/validate", headers=headers, timeout=5)
        result = response.json()
        
        if result.get('valid'):
            print(f"   ✅ JWT Validation: WORKING")
            print(f"   ✅ User email: {result.get('user', {}).get('email')}")
        else:
            print(f"   ❌ JWT Validation: FAILED")
            print(f"   ❌ Error: {result.get('error')}")
        
        # Test protected endpoint
        response = requests.get(f"{BASE_URL}/api/protected/test", headers=headers, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Protected endpoint: ACCESSIBLE")
        else:
            print(f"   ❌ Protected endpoint: FAILED ({response.status_code})")
            print(f"       Error: {response.json().get('detail')}")
            
    except Exception as e:
        print(f"   ❌ JWT Test failed: {e}")
    
    # Test 3: Verify server environment variables
    print("\n3. Testing Server Configuration")
    print("-" * 32)
    
    try:
        response = requests.get(f"{BASE_URL}/debug/env", timeout=5)
        env_info = response.json()
        
        print(f"   JWT Secret loaded: {env_info.get('supabase_jwt_secret_loaded')}")
        print(f"   Base64 decode success: {env_info.get('base64_decode_success')}")
        print(f"   Decoded secret length: {env_info.get('supabase_jwt_secret_decoded_length')}")
        
        if (env_info.get('supabase_jwt_secret_loaded') and 
            env_info.get('base64_decode_success') and 
            env_info.get('supabase_jwt_secret_decoded_length') == 64):
            print(f"   ✅ Server configuration: CORRECT")
        else:
            print(f"   ❌ Server configuration: ISSUES DETECTED")
            
    except Exception as e:
        print(f"   ❌ Server config test failed: {e}")
    
    print(f"\n🏁 Test Complete!")
    print("=" * 45)

if __name__ == "__main__":
    test_fixed_jwt_and_api_paths()
