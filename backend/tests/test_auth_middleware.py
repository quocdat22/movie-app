"""
Test script for FastAPI auth middleware
Run this to test authentication functionality
"""

import asyncio
import httpx
import os
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_auth_middleware():
    """
    Test the authentication middleware
    """
    print("🧪 Testing FastAPI Auth Middleware")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Health check (public endpoint)
        print("\n1. Testing public health endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 2: Auth status without token
        print("\n2. Testing auth status without token...")
        try:
            response = await client.get(f"{BASE_URL}/api/auth/session")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: Protected endpoint without token (should fail)
        print("\n3. Testing protected endpoint without token...")
        try:
            response = await client.get(f"{BASE_URL}/api/protected/profile")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 4: Protected endpoint with invalid token (should fail)
        print("\n4. Testing protected endpoint with invalid token...")
        try:
            headers = {"Authorization": "Bearer invalid_token"}
            response = await client.get(f"{BASE_URL}/api/protected/profile", headers=headers)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 5: Test with valid token (if available)
        valid_token = os.getenv("TEST_JWT_TOKEN")
        if valid_token:
            print("\n5. Testing with valid token...")
            try:
                headers = {"Authorization": f"Bearer {valid_token}"}
                response = await client.get(f"{BASE_URL}/api/protected/profile", headers=headers)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.json()}")
            except Exception as e:
                print(f"   Error: {e}")
        else:
            print("\n5. Skipping valid token test (TEST_JWT_TOKEN not set)")
    
    print("\n" + "=" * 50)
    print("✅ Auth middleware testing complete!")

def print_middleware_info():
    """
    Print information about the auth middleware setup
    """
    print("\n🔒 FastAPI Auth Middleware Configuration")
    print("=" * 50)
    print("Protected Paths:")
    protected_paths = [
        "/api/protected",
        "/api/user", 
        "/api/profile",
        "/api/movies/rate",
        "/api/reviews",
        "/api/favorites",
        "/api/watchlist"
    ]
    for path in protected_paths:
        print(f"   ✓ {path}")
    
    print("\nExcluded Paths (Public):")
    excluded_paths = [
        "/",
        "/docs",
        "/redoc",
        "/openapi.json", 
        "/api/health",
        "/api/movies",
        "/api/auth"
    ]
    for path in excluded_paths:
        print(f"   ✓ {path}")
    
    print("\nFeatures:")
    features = [
        "JWT token validation",
        "Automatic user injection into request state",
        "Role-based access control",
        "Security headers",
        "Request logging",
        "Flexible path configuration"
    ]
    for feature in features:
        print(f"   ✓ {feature}")

if __name__ == "__main__":
    print_middleware_info()
    
    # Run the async test
    asyncio.run(test_auth_middleware())
