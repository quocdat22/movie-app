"""
Sprint 3: Backend Integration & Security
Enhanced FastAPI Authentication Middleware with JWT verification
"""

import jwt
import os
import time
import re
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import logging

# Import enhanced JWT functionality
from .jwt_enhanced import validate_request_token, get_token_info

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for FastAPI
    Handles JWT token validation and user session management
    """
    
    def __init__(self, app, protected_paths: List[str] = None, excluded_paths: List[str] = None):
        super().__init__(app)
        jwt_secret_raw = os.getenv("SUPABASE_JWT_SECRET")
        if jwt_secret_raw:
            try:
                import base64
                self.jwt_secret = base64.b64decode(jwt_secret_raw)
            except Exception:
                self.jwt_secret = jwt_secret_raw.encode('utf-8')
        else:
            self.jwt_secret = None
        self.jwt_algorithm = "HS256"
        
        # Default protected paths (require authentication)
        self.protected_paths = protected_paths or [
            "/api/protected",
            "/api/user",
            "/api/profile",
            "/api/movies/rate",
            "/api/reviews",
            "/api/favorites",
            "/api/watchlist"
        ]
        
        # Paths that don't require authentication
        self.excluded_paths = excluded_paths or [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/health",
            "/api/movies",  # Public movie endpoints
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh"
        ]

    async def dispatch(self, request: Request, call_next):
        """
        Process each request through the authentication middleware
        """
        start_time = time.time()
        
        try:
            # Check if path requires authentication
            requires_auth = self._requires_authentication(request.url.path)
            
            if requires_auth:
                # Validate authentication
                user = await self._authenticate_request(request)
                if not user:
                    return JSONResponse(
                        status_code=401,
                        content={
                            "error": "Authentication required",
                            "message": "Valid JWT token required for this endpoint"
                        }
                    )
                
                # Add user info to request state
                request.state.user = user
                request.state.authenticated = True
            else:
                # For non-protected routes, try to get user if token exists
                user = await self._get_optional_user(request)
                request.state.user = user
                request.state.authenticated = user is not None

            # Process the request
            response = await call_next(request)
            
            # Add security headers
            response = self._add_security_headers(response)
            
            # Log request
            process_time = time.time() - start_time
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Auth: {request.state.authenticated} - "
                f"Time: {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Auth middleware error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "Authentication middleware encountered an error"
                }
            )

    def _requires_authentication(self, path: str) -> bool:
        """
        Check if a path requires authentication
        """
        # Check excluded paths first
        for excluded_path in self.excluded_paths:
            if path.startswith(excluded_path):
                return False
        
        # Check protected paths
        for protected_path in self.protected_paths:
            if path.startswith(protected_path):
                return True
        
        return False

    async def _authenticate_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Authenticate a request and return user info using enhanced JWT validation
        """
        try:
            # Use the enhanced JWT validation
            is_valid, user_data, error = validate_request_token(request)
            if is_valid:
                return user_data
            else:
                logger.warning(f"Authentication failed: {error}")
                return None
            
        except Exception as e:
            logger.warning(f"Authentication failed: {str(e)}")
            return None

    async def _get_optional_user(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Optionally get user from request using enhanced JWT validation
        """
        try:
            return get_token_info(request)
        except Exception:
            return None

    def _verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and extract user information
        """
        try:
            if not self.jwt_secret:
                logger.error("JWT secret not configured")
                return None
            
            # Decode and verify the token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm],
                audience="authenticated"
            )
            
            # Extract user information
            user_info = {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role", "authenticated"),
                "aud": payload.get("aud"),
                "exp": payload.get("exp"),
                "iat": payload.get("iat"),
                "app_metadata": payload.get("app_metadata", {}),
                "user_metadata": payload.get("user_metadata", {})
            }
            
            # Validate required fields
            if not user_info["id"] or not user_info["email"]:
                logger.warning("Invalid token: missing required user information")
                return None
            
            # Check token expiration
            if user_info["exp"] and user_info["exp"] < time.time():
                logger.warning("Token has expired")
                return None
            
            return user_info
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"JWT verification error: {str(e)}")
            return None

    def _add_security_headers(self, response: Response) -> Response:
        """
        Add security headers to response
        """
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RoleBasedAccessControl:
    """
    Role-based access control utilities
    """
    
    @staticmethod
    def require_role(required_role: str):
        """
        Decorator to require specific role for endpoint access
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Get request from args or kwargs
                request = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                
                if not request:
                    raise HTTPException(
                        status_code=500,
                        detail="Internal error: Request not found"
                    )
                
                user = getattr(request.state, 'user', None)
                if not user:
                    raise HTTPException(
                        status_code=401,
                        detail="Authentication required"
                    )
                
                user_role = user.get('role', 'authenticated')
                if user_role != required_role and required_role != 'authenticated':
                    raise HTTPException(
                        status_code=403,
                        detail=f"Access denied. Required role: {required_role}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def require_admin():
        """
        Decorator to require admin role
        """
        return RoleBasedAccessControl.require_role('admin')

    @staticmethod
    def require_user():
        """
        Decorator to require authenticated user
        """
        return RoleBasedAccessControl.require_role('authenticated')


def get_current_user_from_request(request: Request) -> Optional[Dict[str, Any]]:
    """
    Enhanced: Get current user from request using enhanced JWT validation
    Returns user data if authenticated, None otherwise
    """
    try:
        return get_token_info(request)
    except Exception as e:
        logger.error(f"Error getting user from request: {e}")
        return None


def is_authenticated(request: Request) -> bool:
    """
    Enhanced: Check if request has valid authentication using enhanced JWT validation
    """
    user_data = get_current_user_from_request(request)
    return user_data is not None


def require_authentication(request: Request) -> Dict[str, Any]:
    """
    Enhanced: Require authentication and return user data using enhanced JWT validation
    Raises HTTPException if not authenticated
    """
    is_valid, user_data, error = validate_request_token(request)
    if not is_valid:
        raise HTTPException(
            status_code=401, 
            detail=error or "Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user_data
