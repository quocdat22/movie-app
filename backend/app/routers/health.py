"""
Health check and authentication testing endpoints
"""

from fastapi import APIRouter, Request, Depends
from typing import Dict, Any, Optional
from app.middleware.auth import get_current_user_from_request, is_authenticated, require_authentication

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
async def health_check():
    """
    Public health check endpoint
    """
    return {
        "status": "healthy",
        "service": "movie-app-api",
        "version": "1.0.0"
    }

@router.get("/auth/status")
async def auth_status(request: Request):
    """
    Check authentication status (public endpoint)
    """
    user = get_current_user_from_request(request)
    authenticated = is_authenticated(request)
    
    return {
        "authenticated": authenticated,
        "user_id": user.get("id") if user else None,
        "email": user.get("email") if user else None,
        "role": user.get("role") if user else None
    }

@router.get("/protected/profile")
async def get_protected_profile(request: Request):
    """
    Protected endpoint that requires authentication
    """
    user = require_authentication(request)
    
    return {
        "message": "Access granted to protected resource",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user.get("role", "authenticated"),
            "metadata": user.get("user_metadata", {})
        }
    }

@router.get("/protected/admin")
async def admin_only_endpoint(request: Request):
    """
    Admin-only protected endpoint
    """
    user = require_authentication(request)
    
    if user.get("role") != "admin":
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return {
        "message": "Admin access granted",
        "user": user
    }
