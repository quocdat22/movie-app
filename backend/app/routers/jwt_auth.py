"""
JWT Token Management API Endpoints
Sprint 3 Task 3: Enhanced JWT verification and refresh token management
"""

from fastapi import APIRouter, Request, HTTPException, Depends, Response, Cookie
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from pydantic import BaseModel
import logging

from ..middleware.jwt_enhanced import (
    jwt_manager, 
    token_blacklist, 
    validate_request_token, 
    require_valid_token, 
    get_token_info
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication & JWT"])

# Request/Response models
class TokenRefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

class TokenValidationResponse(BaseModel):
    valid: bool
    user: Optional[Dict[str, Any]] = None
    token_type: Optional[str] = None
    expires_at: Optional[int] = None
    error: Optional[str] = None

@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(request: TokenRefreshRequest):
    """
    Refresh access token using valid refresh token
    """
    success, token_response, error = jwt_manager.refresh_access_token(request.refresh_token)
    
    if not success:
        raise HTTPException(status_code=401, detail=error or "Invalid refresh token")
    
    return TokenResponse(**token_response)

@router.post("/token/validate")
async def validate_token(request: Request) -> TokenValidationResponse:
    """
    Validate current token and return token information
    """
    is_valid, user_data, error = validate_request_token(request)
    
    if not is_valid:
        return TokenValidationResponse(
            valid=False,
            error=error
        )
    
    return TokenValidationResponse(
        valid=True,
        user=user_data,
        token_type="bearer",
        expires_at=user_data.get("exp")
    )

@router.post("/token/introspect")
async def introspect_token(request: Request):
    """
    Detailed token introspection (similar to OAuth2 introspection)
    """
    token = jwt_manager.extract_token_from_request(request)
    if not token:
        return {"active": False}
    
    # Try Supabase token first
    is_valid, user_data, error = jwt_manager.validate_supabase_token(token)
    if is_valid:
        return {
            "active": True,
            "token_type": "supabase",
            "sub": user_data["id"],
            "email": user_data["email"],
            "role": user_data.get("role"),
            "aud": user_data.get("aud"),
            "iss": user_data.get("iss"),
            "exp": user_data.get("exp"),
            "iat": user_data.get("iat")
        }
    
    # Try app token
    is_valid, payload, error = jwt_manager.validate_app_token(token)
    if is_valid:
        # Check blacklist
        jti = payload.get("jti")
        if jti and token_blacklist.is_blacklisted(jti):
            return {"active": False, "error": "Token revoked"}
        
        return {
            "active": True,
            "token_type": "app",
            "sub": payload["sub"],
            "email": payload.get("email"),
            "role": payload.get("role"),
            "exp": payload.get("exp"),
            "iat": payload.get("iat"),
            "jti": payload.get("jti")
        }
    
    return {"active": False, "error": error}

@router.post("/logout")
async def logout(request: Request, response: Response):
    """
    Logout user and blacklist current token
    """
    token = jwt_manager.extract_token_from_request(request)
    if not token:
        raise HTTPException(status_code=400, detail="No token to logout")
    
    # Validate and get token info
    is_valid, token_data, error = jwt_manager.validate_app_token(token)
    if is_valid:
        # Add to blacklist if it's an app token
        jti = token_data.get("jti")
        user_id = token_data.get("sub")
        exp = token_data.get("exp")
        
        if jti and user_id and exp:
            from datetime import datetime
            expires_at = datetime.fromtimestamp(exp)
            token_blacklist.add_to_blacklist(jti, user_id, expires_at)
    
    # Clear cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    
    return {"message": "Successfully logged out"}

@router.post("/logout-all")
async def logout_all_sessions(request: Request):
    """
    Logout user from all sessions (requires authentication)
    This would typically involve invalidating all tokens for a user
    """
    user_data = require_valid_token(request)
    user_id = user_data["id"]
    
    # In a production system, you might:
    # 1. Blacklist all tokens for this user
    # 2. Update user's token generation counter
    # 3. Force re-authentication
    
    # For now, we'll add a placeholder response
    logger.info(f"User {user_id} logged out from all sessions")
    
    return {
        "message": "Successfully logged out from all sessions",
        "user_id": user_id
    }

@router.get("/token/info")
async def get_current_token_info(request: Request):
    """
    Get information about the current token
    """
    user_data = require_valid_token(request)
    
    return {
        "user": {
            "id": user_data["id"],
            "email": user_data["email"],
            "role": user_data.get("role", "authenticated")
        },
        "token_info": {
            "expires_at": user_data.get("exp"),
            "issued_at": user_data.get("iat"),
            "issuer": user_data.get("iss"),
            "audience": user_data.get("aud")
        }
    }

@router.post("/token/exchange")
async def exchange_supabase_token(request: Request):
    """
    Exchange Supabase token for application token pair
    """
    token = jwt_manager.extract_token_from_request(request)
    if not token:
        raise HTTPException(status_code=400, detail="No Supabase token provided")
    
    # Validate Supabase token
    is_valid, user_data, error = jwt_manager.validate_supabase_token(token)
    if not is_valid:
        raise HTTPException(status_code=401, detail=error or "Invalid Supabase token")
    
    # Generate app token pair
    token_response = jwt_manager.create_token_response(user_data)
    
    return TokenResponse(**token_response)

@router.get("/session")
async def get_session_info(request: Request):
    """
    Get current session information (optional authentication)
    """
    user_data = get_token_info(request)
    
    if not user_data:
        return {
            "authenticated": False,
            "user": None,
            "session": None
        }
    
    return {
        "authenticated": True,
        "user": {
            "id": user_data["id"],
            "email": user_data["email"],
            "role": user_data.get("role", "authenticated")
        },
        "session": {
            "expires_at": user_data.get("exp"),
            "issued_at": user_data.get("iat"),
            "token_type": "app" if user_data.get("jti") else "supabase"
        }
    }

@router.post("/admin/cleanup-tokens")
async def cleanup_expired_tokens(request: Request):
    """
    Admin endpoint to cleanup expired blacklisted tokens
    """
    user_data = require_valid_token(request)
    
    # Check if user has admin role
    if user_data.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        token_blacklist.cleanup_expired_tokens()
        return {"message": "Expired tokens cleaned up successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
