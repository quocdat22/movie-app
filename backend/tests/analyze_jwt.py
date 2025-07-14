#!/usr/bin/env python3
"""
Decode JWT without verification to see contents
"""
import jwt
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()

def decode_jwt_no_verify():
    """Decode JWT without verification to see what's inside"""
    print("🔍 JWT Token Analysis")
    print("=" * 25)
    
    # Get a real Supabase token format
    jwt_secret_raw = os.getenv("SUPABASE_JWT_SECRET")
    jwt_secret_decoded = base64.b64decode(jwt_secret_raw)
    
    # Create our test token
    from datetime import datetime, timedelta
    payload = {
        "sub": "test-user-direct",
        "email": "direct@example.com",
        "role": "authenticated",
        "aud": "authenticated",
        "iss": "supabase",
        "exp": int((datetime.utcnow() + timedelta(hours=24)).timestamp()),
        "iat": int((datetime.utcnow() - timedelta(minutes=5)).timestamp()),
        "app_metadata": {},
        "user_metadata": {}
    }
    
    test_token = jwt.encode(payload, jwt_secret_decoded, algorithm="HS256")
    print(f"Test token: {test_token}")
    
    # Decode without verification to see contents
    try:
        unverified = jwt.decode(test_token, options={"verify_signature": False})
        print(f"\nUnverified token contents:")
        for key, value in unverified.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"❌ Unverified decode failed: {e}")
    
    # Test different audience values
    audiences_to_try = [None, "authenticated", "supabase", ["authenticated"], ["supabase"]]
    
    for aud in audiences_to_try:
        try:
            if aud is None:
                decoded = jwt.decode(
                    test_token,
                    jwt_secret_decoded,
                    algorithms=["HS256"],
                    options={"verify_aud": False}  # Disable audience verification
                )
                print(f"✅ Decode successful with verify_aud=False")
                break
            else:
                decoded = jwt.decode(
                    test_token,
                    jwt_secret_decoded,
                    algorithms=["HS256"],
                    audience=aud
                )
                print(f"✅ Decode successful with audience: {aud}")
                break
        except Exception as e:
            print(f"❌ Decode failed with audience {aud}: {e}")

if __name__ == "__main__":
    decode_jwt_no_verify()
