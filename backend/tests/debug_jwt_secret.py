#!/usr/bin/env python3
"""
Test to debug JWT secret mismatch
"""
import requests
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

def debug_jwt_secret():
    """Debug JWT secret usage"""
    print("🔍 JWT Secret Debug")
    print("=" * 30)
    
    # Get environment info from server
    response = requests.get(f"{BASE_URL}/debug/env")
    server_env = response.json()
    print(f"Server JWT secret length: {server_env['supabase_jwt_secret_length']}")
    
    # Get local JWT secret
    local_secret = os.getenv("SUPABASE_JWT_SECRET")
    print(f"Local JWT secret length: {len(local_secret) if local_secret else 0}")
    
    # Create a simple token and test validation
    if local_secret:
        print(f"\nLocal secret (first 20 chars): {local_secret[:20]}...")
        print(f"Local secret (last 20 chars): ...{local_secret[-20:]}")
        
        # Generate a minimal valid token
        payload = {
            "sub": "test-user",
            "email": "test@example.com",
            "aud": "authenticated",
            "role": "authenticated",
            "exp": int((datetime.utcnow() + timedelta(minutes=30)).timestamp()),
            "iat": int(datetime.utcnow().timestamp())
        }
        
        token = jwt.encode(payload, local_secret, algorithm="HS256")
        print(f"\nGenerated token: {token}")
        
        # Test if we can decode it locally
        try:
            decoded = jwt.decode(token, local_secret, algorithms=["HS256"], audience="authenticated")
            print("✅ Local decode successful")
        except Exception as e:
            print(f"❌ Local decode failed: {e}")
        
        # Test with server
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/api/auth/token/validate", headers=headers)
        result = response.json()
        print(f"\nServer validation result:")
        print(f"Valid: {result.get('valid')}")
        if result.get('error'):
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    debug_jwt_secret()
