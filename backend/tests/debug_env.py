#!/usr/bin/env python3
"""
Debug script to check environment variable loading
"""
import os
from dotenv import load_dotenv

print("🔍 Environment Variable Debug")
print("=" * 40)

# Load environment variables
load_dotenv()

# Check key environment variables
env_vars = [
    "SUPABASE_JWT_SECRET",
    "APP_JWT_SECRET", 
    "REFRESH_TOKEN_SECRET",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY"
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f"{var}: {'*' * 10}...{value[-10:] if len(value) > 20 else value}")
    else:
        print(f"{var}: NOT SET")

# Test JWT encoding/decoding
print("\n🧪 JWT Test")
print("=" * 20)

try:
    import jwt
    from datetime import datetime, timedelta
    
    secret = os.getenv("SUPABASE_JWT_SECRET")
    if secret:
        payload = {
            "sub": "test-user-123",
            "email": "test@example.com", 
            "role": "authenticated",
            "aud": "authenticated",
            "iss": "supabase",
            "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
            "iat": int(datetime.utcnow().timestamp())
        }
        
        token = jwt.encode(payload, secret, algorithm="HS256")
        print(f"Generated token: {token[:50]}...")
        
        # Try to decode it back
        decoded = jwt.decode(token, secret, algorithms=["HS256"], audience="authenticated")
        print(f"Decoded successfully: {decoded['email']}")
    else:
        print("SUPABASE_JWT_SECRET not found")
        
except Exception as e:
    print(f"JWT test failed: {e}")
