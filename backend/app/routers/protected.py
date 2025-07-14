"""
Protected Endpoints Router
Handles endpoints that require authentication
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Dict, Any
from ..middleware.auth import require_authentication
from ..auth import get_current_user

router = APIRouter(prefix="/api/protected", tags=["Protected"])

@router.get("/profile")
async def get_protected_profile(request: Request):
    """
    Get current user profile - protected endpoint
    """
    user = require_authentication(request)
    
    return {
        "message": "This is a protected endpoint",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user.get("role", "authenticated")
        }
    }

@router.get("/test")
async def protected_test(request: Request):
    """
    Test protected endpoint
    """
    user = require_authentication(request)
    
    return {
        "message": "Authentication successful",
        "authenticated": True,
        "user_id": user["id"],
        "timestamp": "2025-01-14T00:00:00Z"
    }
