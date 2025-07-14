"""
Sprint 3 Task 3: Enhanced JWT Verification and Refresh Token Management
Advanced JWT handling with token refresh, validation, and security features
"""

import jwt
import os
import time
import hashlib
import secrets
import base64
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
import logging

from ..db import get_supabase

logger = logging.getLogger(__name__)

class JWTManager:
    """Enhanced JWT token management with refresh tokens and advanced validation"""
    
    def __init__(self):
        # Load environment variables with better error handling
        supabase_jwt_secret_raw = os.getenv("SUPABASE_JWT_SECRET")
        if supabase_jwt_secret_raw:
            # Decode base64 encoded JWT secret from Supabase
            try:
                self.supabase_jwt_secret = base64.b64decode(supabase_jwt_secret_raw)
                logger.info("Successfully decoded SUPABASE_JWT_SECRET")
            except Exception as e:
                logger.error(f"Failed to decode SUPABASE_JWT_SECRET: {e}")
                self.supabase_jwt_secret = supabase_jwt_secret_raw.encode('utf-8')
        else:
            logger.warning("SUPABASE_JWT_SECRET not set - Supabase token validation will fail")
            self.supabase_jwt_secret = None
            
        self.app_jwt_secret = os.getenv("APP_JWT_SECRET")
        if not self.app_jwt_secret:
            logger.warning("APP_JWT_SECRET not set - using fallback secret (NOT FOR PRODUCTION)")
            self.app_jwt_secret = "fallback-secret-change-in-production"
            
        self.refresh_token_secret = os.getenv("REFRESH_TOKEN_SECRET")
        if not self.refresh_token_secret:
            logger.warning("REFRESH_TOKEN_SECRET not set - using fallback secret (NOT FOR PRODUCTION)")
            self.refresh_token_secret = "refresh-secret-change-in-production"
        
        # Token expiration times
        self.access_token_expiry = int(os.getenv("ACCESS_TOKEN_EXPIRY_MINUTES", "15")) * 60  # 15 minutes
        self.refresh_token_expiry = int(os.getenv("REFRESH_TOKEN_EXPIRY_DAYS", "7")) * 24 * 60 * 60  # 7 days
        
        # Algorithm settings
        self.algorithm = "HS256"
        
        # Token validation settings
        self.leeway = int(os.getenv("JWT_LEEWAY_SECONDS", "10"))  # Clock skew tolerance
        
    def validate_supabase_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validate Supabase JWT token with enhanced error handling
        Returns: (is_valid, user_data, error_message)
        """
        if not token:
            return False, None, "No token provided"
            
        if not self.supabase_jwt_secret:
            logger.error("SUPABASE_JWT_SECRET not configured")
            return False, None, "JWT configuration error"
        
        try:
            # Decode with comprehensive validation
            payload = jwt.decode(
                token,
                self.supabase_jwt_secret,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                    "verify_aud": False,  # Disable automatic audience verification
                    "require_exp": True,
                    "require_iat": True,
                },
                leeway=self.leeway
            )
            
            # Validate required claims
            required_claims = ["sub", "email", "exp", "iat"]
            missing_claims = [claim for claim in required_claims if claim not in payload]
            if missing_claims:
                return False, None, f"Missing required claims: {missing_claims}"
            
            # Check token type if present
            if "token_type" in payload and payload["token_type"] != "access":
                return False, None, "Invalid token type"
            
            # Extract user information
            user_data = {
                "id": payload["sub"],
                "email": payload.get("email"),
                "role": payload.get("role", "authenticated"),
                "aud": payload.get("aud"),
                "iss": payload.get("iss"),
                "exp": payload.get("exp"),
                "iat": payload.get("iat"),
                "app_metadata": payload.get("app_metadata", {}),
                "user_metadata": payload.get("user_metadata", {})
            }
            
            logger.info(f"Successfully validated Supabase token for user: {user_data['email']}")
            return True, user_data, None
            
        except jwt.ExpiredSignatureError:
            return False, None, "Token has expired"
        except jwt.InvalidSignatureError:
            return False, None, "Invalid token signature"
        except jwt.InvalidTokenError as e:
            return False, None, f"Invalid token: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error validating JWT: {e}")
            return False, None, "Token validation failed"
    
    def generate_app_access_token(self, user_data: Dict[str, Any]) -> str:
        """Generate application-specific access token"""
        now = datetime.utcnow()
        payload = {
            "sub": user_data["id"],
            "email": user_data["email"],
            "role": user_data.get("role", "authenticated"),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=self.access_token_expiry)).timestamp()),
            "iss": "movie-app",
            "aud": "movie-app-users",
            "token_type": "access",
            "jti": secrets.token_urlsafe(16)  # Unique token ID
        }
        
        return jwt.encode(payload, self.app_jwt_secret, algorithm=self.algorithm)
    
    def generate_refresh_token(self, user_id: str) -> str:
        """Generate refresh token"""
        now = datetime.utcnow()
        payload = {
            "sub": user_id,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=self.refresh_token_expiry)).timestamp()),
            "iss": "movie-app",
            "token_type": "refresh",
            "jti": secrets.token_urlsafe(32)  # Unique token ID for refresh
        }
        
        return jwt.encode(payload, self.refresh_token_secret, algorithm=self.algorithm)
    
    def validate_app_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Validate application-generated access token"""
        try:
            payload = jwt.decode(
                token,
                self.app_jwt_secret,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "require_exp": True,
                    "require_iat": True,
                },
                leeway=self.leeway
            )
            
            # Validate token type
            if payload.get("token_type") != "access":
                return False, None, "Invalid token type"
            
            return True, payload, None
            
        except jwt.ExpiredSignatureError:
            return False, None, "Access token has expired"
        except jwt.InvalidTokenError as e:
            return False, None, f"Invalid access token: {str(e)}"
    
    def validate_refresh_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Validate refresh token"""
        try:
            payload = jwt.decode(
                token,
                self.refresh_token_secret,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "require_exp": True,
                    "require_iat": True,
                },
                leeway=self.leeway
            )
            
            # Validate token type
            if payload.get("token_type") != "refresh":
                return False, None, "Invalid token type"
            
            return True, payload, None
            
        except jwt.ExpiredSignatureError:
            return False, None, "Refresh token has expired"
        except jwt.InvalidTokenError as e:
            return False, None, f"Invalid refresh token: {str(e)}"
    
    def extract_token_from_request(self, request: Request) -> Optional[str]:
        """
        Extract JWT token from request with multiple sources support
        Supports: Authorization header, cookies, query parameters
        """
        # Try Authorization header first (Bearer token)
        authorization = request.headers.get("Authorization")
        if authorization:
            if authorization.startswith("Bearer "):
                return authorization.split("Bearer ", 1)[1].strip()
            # Handle case where token is passed without Bearer prefix
            elif not authorization.startswith("Basic "):
                return authorization.strip()
        
        # Try cookies
        access_token = request.cookies.get("access_token")
        if access_token:
            return access_token
        
        # Try query parameter (for WebSocket or special cases)
        token = request.query_params.get("token")
        if token:
            return token
        
        return None
    
    def create_token_response(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create complete token response with access and refresh tokens"""
        access_token = self.generate_app_access_token(user_data)
        refresh_token = self.generate_refresh_token(user_data["id"])
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expiry,
            "user": {
                "id": user_data["id"],
                "email": user_data["email"],
                "role": user_data.get("role", "authenticated")
            }
        }
    
    def refresh_access_token(self, refresh_token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Refresh access token using valid refresh token
        Returns: (success, token_response, error_message)
        """
        # Validate refresh token
        is_valid, payload, error = self.validate_refresh_token(refresh_token)
        if not is_valid:
            return False, None, error
        
        user_id = payload["sub"]
        
        # Get fresh user data from Supabase
        try:
            supabase = get_supabase()
            user_resp = supabase.auth.admin.get_user_by_id(user_id)
            
            if not user_resp.user:
                return False, None, "User not found"
            
            user_data = {
                "id": user_resp.user.id,
                "email": user_resp.user.email,
                "role": user_resp.user.role or "authenticated"
            }
            
            # Generate new tokens
            token_response = self.create_token_response(user_data)
            return True, token_response, None
            
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return False, None, "Failed to refresh token"

class TokenBlacklist:
    """Manage token blacklist for logout and security"""
    
    def __init__(self):
        try:
            self.supabase = get_supabase()
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client for token blacklist: {e}")
            self.supabase = None
    
    def add_to_blacklist(self, token_jti: str, user_id: str, expires_at: datetime):
        """Add token to blacklist"""
        if not self.supabase:
            logger.error("Supabase client not available for token blacklist")
            return False
            
        try:
            blacklist_data = {
                "jti": token_jti,
                "user_id": user_id,
                "blacklisted_at": datetime.utcnow().isoformat(),
                "expires_at": expires_at.isoformat()
            }
            
            self.supabase.table("token_blacklist").insert(blacklist_data).execute()
            return True
        except Exception as e:
            logger.error(f"Error adding token to blacklist: {e}")
            return False
    
    def is_blacklisted(self, token_jti: str) -> bool:
        """Check if token is blacklisted"""
        if not self.supabase:
            logger.error("Supabase client not available for token blacklist check")
            return False
            
        try:
            resp = self.supabase.table("token_blacklist").select("jti").eq("jti", token_jti).limit(1).execute()
            return len(resp.data) > 0
        except Exception as e:
            logger.error(f"Error checking blacklist: {e}")
            return False
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens from blacklist"""
        if not self.supabase:
            logger.error("Supabase client not available for token cleanup")
            return
            
        try:
            now = datetime.utcnow().isoformat()
            self.supabase.table("token_blacklist").delete().lt("expires_at", now).execute()
        except Exception as e:
            logger.error(f"Error cleaning up blacklist: {e}")

# Global instances
jwt_manager = JWTManager()
token_blacklist = TokenBlacklist()

def validate_request_token(request: Request) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Enhanced token validation for requests
    Supports both Supabase and app tokens with blacklist checking
    """
    token = jwt_manager.extract_token_from_request(request)
    if not token:
        return False, None, "No token provided"
    
    # Try Supabase token first
    is_valid, user_data, error = jwt_manager.validate_supabase_token(token)
    if is_valid:
        return True, user_data, None
    
    # Try app token
    is_valid, payload, error = jwt_manager.validate_app_token(token)
    if is_valid:
        # Check blacklist
        jti = payload.get("jti")
        if jti and token_blacklist.is_blacklisted(jti):
            return False, None, "Token has been revoked"
        
        return True, payload, None
    
    return False, None, error

def require_valid_token(request: Request) -> Dict[str, Any]:
    """Require valid token and return user data"""
    is_valid, user_data, error = validate_request_token(request)
    if not is_valid:
        raise HTTPException(status_code=401, detail=error or "Authentication required")
    
    return user_data

def get_token_info(request: Request) -> Optional[Dict[str, Any]]:
    """Get token info without raising exceptions"""
    is_valid, user_data, _ = validate_request_token(request)
    return user_data if is_valid else None
