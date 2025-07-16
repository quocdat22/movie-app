#!/usr/bin/env python3
"""
Direct test of JWT manager to verify base64 decoding
"""
import sys
import os
import base64
import jwt
from datetime import datetime, timedelta

# Add the backend path to sys.path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def test_jwt_manager_directly():
    """Test the JWT manager directly to see if it's using base64 decoded secret"""
    print("🔬 Direct JWT Manager Test")
    print("=" * 30)
    
    try:
        # Import and test the JWT manager
        from app.middleware.jwt_enhanced import JWTManager
        
        # Create JWT manager instance
        jwt_manager = JWTManager()
        
        print(f"JWT Manager initialized")
        print(f"Supabase JWT secret type: {type(jwt_manager.supabase_jwt_secret)}")
        if jwt_manager.supabase_jwt_secret:
            print(f"Supabase JWT secret length: {len(jwt_manager.supabase_jwt_secret)}")
            print(f"Is bytes?: {isinstance(jwt_manager.supabase_jwt_secret, bytes)}")
        
        # Create a test token using the raw base64 secret (like our local test)
        jwt_secret_raw = os.getenv("SUPABASE_JWT_SECRET") 
        jwt_secret_decoded = base64.b64decode(jwt_secret_raw)
        
        payload = {
            "sub": "test-user-direct",
            "email": "direct@example.com",
            "role": "authenticated",
            "aud": "authenticated",  # This should match Supabase's audience
            "iss": "supabase",
            "exp": int((datetime.utcnow() + timedelta(hours=24)).timestamp()),
            "iat": int((datetime.utcnow() - timedelta(minutes=5)).timestamp()),
            "app_metadata": {},
            "user_metadata": {}
        }
        
        # Generate token with our decoded secret
        test_token = jwt.encode(payload, jwt_secret_decoded, algorithm="HS256")
        print(f"\nTest token generated: {test_token[:50]}...")
        
        # Test validation using JWT manager
        print(f"\n🔍 Testing JWT validation step by step...")
        
        # First test - decode the token manually with the same secret
        try:
            manual_payload = jwt.decode(
                test_token,
                jwt_secret_decoded,
                algorithms=["HS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                    "require_exp": True,
                    "require_iat": True,
                },
                leeway=10
            )
            print(f"✅ Manual decode successful: {manual_payload.get('email')}")
            print(f"   Audience in token: {manual_payload.get('aud')}")
        except Exception as e:
            print(f"❌ Manual decode failed: {e}")
        
        # Now test with JWT manager
        is_valid, user_data, error = jwt_manager.validate_supabase_token(test_token)
        print(f"\nJWT Manager validation result:")
        print(f"Valid: {is_valid}")
        if error:
            print(f"Error: {error}")
        else:
            print(f"User: {user_data.get('email') if user_data else 'None'}")
            
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_jwt_manager_directly()
