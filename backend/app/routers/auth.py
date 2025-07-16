"""
Sprint 1: Foundation & Setup
Basic auth endpoints for user profile management
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from ..auth import get_current_user, get_optional_user
from ..db import get_supabase

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/me")
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user profile information
    """
    try:
        supabase = get_supabase()
        
        # Get user profile from profiles table
        result = supabase.table("profiles").select("*").eq("id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        profile = result.data[0]
        
        return {
            "id": profile["id"],
            "email": profile["email"],
            "full_name": profile["full_name"],
            "avatar_url": profile["avatar_url"],
            "created_at": profile["created_at"],
            "updated_at": profile["updated_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")

@router.get("/status")
async def auth_status(current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)):
    """
    Check authentication status (public endpoint)
    """
    if current_user:
        return {
            "authenticated": True,
            "user_id": current_user["id"],
            "email": current_user.get("email"),
            "role": current_user.get("role", "authenticated")
        }
    else:
        return {
            "authenticated": False,
            "user_id": None,
            "email": None,
            "role": "anonymous"
        }
