"""
Sprint 1: Foundation & Setup
Basic auth endpoints for user profile management
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr
import logging
from ..auth import get_current_user, get_optional_user
from ..db import get_supabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Pydantic models for request/response
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordUpdateRequest(BaseModel):
    password: str
    access_token: str

class PasswordResetResponse(BaseModel):
    success: bool
    message: str

@router.post("/password-reset-request", response_model=PasswordResetResponse)
async def request_password_reset(request: PasswordResetRequest):
    """
    Send password reset email to user
    """
    try:
        supabase = get_supabase()
        logger.info(f"Password reset requested for email: {request.email}")
        
        # Send password reset email via Supabase
        result = supabase.auth.reset_password_email(
            email=request.email,
            options={
                "redirect_to": "http://localhost:3000/auth/reset-password"
            }
        )
        
        logger.info(f"Password reset email sent successfully for: {request.email}")
        
        return PasswordResetResponse(
            success=True,
            message="Password reset email sent successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to send password reset email for {request.email}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to send password reset email: {str(e)}"
        )

@router.post("/password-reset-confirm", response_model=PasswordResetResponse)
async def confirm_password_reset(request: PasswordUpdateRequest):
    """
    Confirm password reset with new password and access token
    """
    try:
        supabase = get_supabase()
        logger.info("Password reset confirmation attempt")
        
        # Set the session using the access token
        supabase.auth.set_session(request.access_token, refresh_token=None)
        
        # Update the password
        result = supabase.auth.update_user({
            "password": request.password
        })
        
        if result.user:
            logger.info(f"Password updated successfully for user: {result.user.id}")
            return PasswordResetResponse(
                success=True,
                message="Password updated successfully"
            )
        else:
            logger.error("Password update failed - no user returned")
            raise HTTPException(status_code=400, detail="Password update failed")
            
    except Exception as e:
        logger.error(f"Password reset confirmation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update password: {str(e)}"
        )

@router.get("/verify-reset-token")
async def verify_reset_token(access_token: str):
    """
    Verify if a password reset token is valid
    """
    try:
        supabase = get_supabase()
        logger.info("Verifying password reset token")
        
        # Try to get user with the provided token
        supabase.auth.set_session(access_token, refresh_token=None)
        user = supabase.auth.get_user()
        
        if user and user.user:
            logger.info(f"Token verified successfully for user: {user.user.id}")
            return {
                "valid": True,
                "user_id": user.user.id,
                "email": user.user.email
            }
        else:
            logger.warning("Invalid or expired reset token")
            return {"valid": False}
            
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return {"valid": False}

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
