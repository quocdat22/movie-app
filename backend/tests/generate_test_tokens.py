#!/usr/bin/env python3
"""
Generate test JWT tokens for development
"""

import jwt
import time
import os
from datetime import datetime, timedelta

def generate_test_supabase_token():
    """Generate a test Supabase-style JWT token"""
    
    secret = "UGwZyXlazBlFeAHDhlIEdFUWPrgqEAgQzEoTP1NFavPUoJ9DRhN9DziQEaCEMK4D8IQRAwYoLaUiql8jMHQBrA=="
    
    now = datetime.utcnow()
    payload = {
        "sub": "test-user-id-123",
        "email": "test@example.com",
        "role": "authenticated",
        "aud": "authenticated",
        "iss": "https://vpwvtaetbqzvzknokkso.supabase.co",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=24)).timestamp()),  # 24 hours instead of 1 hour
        "app_metadata": {"provider": "email"},
        "user_metadata": {"name": "Test User"}
    }
    
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

def generate_app_test_token():
    """Generate a test application JWT token"""
    
    secret = "your_app_jwt_secret_change_in_production"
    
    now = datetime.utcnow()
    payload = {
        "sub": "test-user-id-123",
        "email": "test@example.com",
        "role": "authenticated",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),  # 1 hour instead of 15 minutes for testing
        "iss": "movie-app",
        "aud": "movie-app-users",
        "token_type": "access",
        "jti": "test-token-123"
    }
    
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

def generate_refresh_token():
    """Generate a test refresh token"""
    
    secret = "your_refresh_token_secret_change_in_production"
    
    now = datetime.utcnow()
    payload = {
        "sub": "test-user-id-123",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=7)).timestamp()),  # 7 days
        "iss": "movie-app",
        "token_type": "refresh",
        "jti": "test-refresh-token-123"
    }
    
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

if __name__ == "__main__":
    print("🔑 JWT Token Generator for Testing")
    print("=" * 50)
    
    # Generate Supabase-style token
    supabase_token = generate_test_supabase_token()
    print(f"\n📋 Test Supabase Token (24h expiry):")
    print(f"Bearer {supabase_token}")
    
    # Generate app token
    app_token = generate_app_test_token()
    print(f"\n📋 Test App Token (1h expiry):")
    print(f"Bearer {app_token}")
    
    # Generate refresh token
    refresh_token = generate_refresh_token()
    print(f"\n📋 Test Refresh Token (7d expiry):")
    print(f"{refresh_token}")
    
    print(f"\n🧪 Test Commands:")
    print(f"# Test with Supabase token:")
    print(f'curl -X POST http://localhost:8000/api/auth/token/exchange \\')
    print(f'  -H "Authorization: Bearer {supabase_token}"')
    
    print(f"\n# Test with app token:")
    print(f'curl -X POST http://localhost:8000/api/auth/token/validate \\')
    print(f'  -H "Authorization: Bearer {app_token}"')
    
    print(f"\n# Test refresh token:")
    print(f'curl -X POST http://localhost:8000/api/auth/token/refresh \\')
    print(f'  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"refresh_token": "{refresh_token}"}}\'')
    
    print(f"\n💡 Copy these tokens for testing!")
