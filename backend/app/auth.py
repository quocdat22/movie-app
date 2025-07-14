"""
Sprint 1: Foundation & Setup
Basic authentication utilities for FastAPI backend
"""

import jwt
import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests

# JWT Configuration
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
JWT_ALGORITHM = "HS256"
SUPABASE_URL = os.getenv("SUPABASE_URL")

security = HTTPBearer()

class AuthError(Exception):
    """Custom authentication error"""
    def __init__(self, error: str, status_code: int = 401):
        self.error = error
        self.status_code = status_code

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify JWT token from Supabase Auth
    """
    try:
        if not JWT_SECRET:
            raise AuthError("JWT secret not configured")
        
        # Decode and verify the token
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            audience="authenticated"
        )
        
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthError("Invalid token")
    except Exception as e:
        raise AuthError(f"Token verification failed: {str(e)}")

def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Extract user information from JWT token
    """
    try:
        payload = verify_jwt_token(token)
        
        return {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "aud": payload.get("aud"),
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }
    except AuthError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user
    """
    try:
        token = credentials.credentials
        user = get_user_from_token(token)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    except AuthError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.error,
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency to optionally get authenticated user (doesn't raise error if no token)
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        return get_user_from_token(token)
    except AuthError:
        return None

def create_auth_headers(service_role_key: str) -> Dict[str, str]:
    """
    Create headers for Supabase API calls with service role
    """
    return {
        "Authorization": f"Bearer {service_role_key}",
        "apikey": service_role_key,
        "Content-Type": "application/json"
    }
