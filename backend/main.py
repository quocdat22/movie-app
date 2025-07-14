from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import our auth middleware
from app.middleware.auth import AuthMiddleware

# Import routers
from app.routers import health
from app.routers import movies
from app.routers import jwt_auth
from app.routers import protected

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Movie App API",
    description="Backend API for Movie App with authentication",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add authentication middleware
app.add_middleware(
    AuthMiddleware,
    protected_paths=[
        "/api/protected",
        "/api/user",
        "/api/profile",
        "/api/movies/.*/rate",       # Movie rating endpoints
        "/api/movies/.*/favorite",   # Movie favorite endpoints  
        "/api/movies/.*/watchlist",  # Movie watchlist endpoints
        "/api/movies/favorites",     # User favorites list
        "/api/movies/watchlist",     # User watchlist list
        "/api/movies/rated",         # User rated movies
        "/api/movies/user-stats",    # User statistics
        "/api/reviews",
        "/api/favorites",
        "/api/watchlist"
    ],
    excluded_paths=[
        "/",
        "/docs",
        "/redoc", 
        "/openapi.json",
        "/api/health",
        "/api/movies",  # Public movie browsing
        "/api/auth"     # Auth endpoints don't need auth
    ]
)

@app.get("/")
def read_root():
    return {
        "message": "Movie App API",
        "version": "1.0.0",
        "status": "running",
        "auth": "enabled"
    }

# Debug endpoint to check environment variables (remove in production)
@app.get("/debug/env")
def debug_env():
    import base64
    
    jwt_secret_raw = os.getenv("SUPABASE_JWT_SECRET")
    app_secret = os.getenv("APP_JWT_SECRET")
    
    # Test base64 decoding
    jwt_secret_decoded = None
    base64_decode_success = False
    if jwt_secret_raw:
        try:
            jwt_secret_decoded = base64.b64decode(jwt_secret_raw)
            base64_decode_success = True
        except Exception as e:
            base64_decode_success = False
    
    return {
        "supabase_jwt_secret_loaded": jwt_secret_raw is not None,
        "supabase_jwt_secret_raw_length": len(jwt_secret_raw) if jwt_secret_raw else 0,
        "supabase_jwt_secret_decoded_length": len(jwt_secret_decoded) if jwt_secret_decoded else 0,
        "base64_decode_success": base64_decode_success,
        "app_jwt_secret_loaded": app_secret is not None,
        "app_jwt_secret_length": len(app_secret) if app_secret else 0,
        "supabase_url": os.getenv("SUPABASE_URL"),
        "middleware_loaded": "AuthMiddleware should be using base64 decoded secret"
    }

# Include routers with proper API versioning
app.include_router(health.router)      # health.py already has /api prefix
app.include_router(movies.router)      # movies.py already has /api/movies prefix  
app.include_router(jwt_auth.router)    # jwt_auth.py already has /api/auth prefix
app.include_router(protected.router)   # protected.py already has /api/protected prefix