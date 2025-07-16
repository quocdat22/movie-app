"""FastAPI router implementing movie endpoints with authentication."""
from __future__ import annotations

import os
import httpx
from typing import List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request  # type: ignore
from postgrest.exceptions import APIError

from ..db import get_supabase
from ..schemas import Movie, MovieListResponse, MovieDetailResponse, CastMember, Company, GenreListResponse
from ..middleware.auth import get_current_user_from_request, require_authentication, is_authenticated

router = APIRouter(prefix="/api/movies", tags=["Movies"])

# Allowed sort fields mapping to column names
_SORT_FIELDS = {"popularity": "popularity", "release_year": "release_year", "title": "title", "created_at": "created_at"}


@router.get("/genres", response_model=GenreListResponse)
def get_genres():
    """Retrieve a list of all unique movie genres using RPC."""
    supabase = get_supabase()
    try:
        resp = supabase.rpc("get_all_genres").execute()
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

    genres = [row.get("genre") for row in resp.data if row.get("genre")]
    return GenreListResponse(data=genres)


def _create_movie_list_response(movies: List[Movie], page: int, page_size: int, total: int) -> MovieListResponse:
    """Helper function to create MovieListResponse with pagination"""
    total_pages = (total + page_size - 1) // page_size
    return MovieListResponse(
        movies=movies,
        page=page,
        per_page=page_size,
        total=total,
        total_pages=total_pages
    )


@router.get("", response_model=MovieListResponse)
def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    genre: Optional[List[str]] = Query(None),
    release_year: Optional[int] = Query(None),
    release_year_gte: Optional[int] = Query(None),
    release_year_lte: Optional[int] = Query(None),
    sort_by: str = Query("created_at", pattern="^(release_year|title|created_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
):
    """List movies with optional filtering and pagination (via SQL RPC)."""
    supabase = get_supabase()

    # Prepare params for RPC
    rpc_params: dict[str, Any] = {
        "p_sort_field": sort_by,
        "p_sort_order": sort_order,
        "p_limit": page_size,
        "p_offset": (page - 1) * page_size,
    }

    if genre:
        rpc_params["p_genre"] = genre  # text[]
    if release_year is not None:
        rpc_params["p_release_year"] = release_year
    if release_year_gte is not None:
        rpc_params["p_release_year_gte"] = release_year_gte
    if release_year_lte is not None:
        rpc_params["p_release_year_lte"] = release_year_lte

    try:
        resp = supabase.rpc("filter_movies", rpc_params).execute()
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

    movies = [Movie(**rec) for rec in resp.data]  # type: ignore[arg-type]
    total_items_est = (page - 1) * page_size + len(resp.data)
    total_pages_est = page if len(resp.data) < page_size else page + 1  # simple heuristic

    return MovieListResponse(
        movies=movies,
        page=page,
        per_page=page_size,
        total=total_items_est,
        total_pages=total_pages_est
    )


@router.get("/search", response_model=MovieListResponse)
def search_movies(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", pattern="^(popularity|release_year|title|created_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
):
    """Search movies by title (case-insensitive, partial match)."""
    supabase = get_supabase()
    base_query = supabase.table("movies").text_search("title", q, config="english")

    # Count
    try:
        count_resp = base_query.select("id", count="exact").execute()
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)
    total_items = count_resp.count or 0

    # Sorting, Pagination, and Data Fetching
    order_desc = sort_order == "desc"
    start = (page - 1) * page_size
    end = start + page_size - 1
    try:
        data_resp = (
            base_query.select("*")
            .order(_SORT_FIELDS[sort_by], desc=order_desc)
            .order("id") # Add secondary sort for stable pagination
            .range(start, end)
            .execute()
        )
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

    movies = [Movie(**rec) for rec in data_resp.data]  # type: ignore[arg-type]
    return _create_movie_list_response(movies, page, page_size, total_items)


TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


@router.get("/{id}", response_model=MovieDetailResponse)
def get_movie(id: int, lite: bool = Query(False)):
    """Retrieve enriched movie details by ID."""
    supabase = get_supabase()
    try:
        resp = supabase.table("movies").select("*").eq("id", id).limit(1).execute()
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

    if not resp.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    db_movie_data = resp.data[0]

    # If lite is requested or TMDB key absent, return only DB data
    if lite or not TMDB_API_KEY:
        return MovieDetailResponse(**db_movie_data)

    try:
        tmdb_url = f"{TMDB_BASE_URL}/movie/{id}?append_to_response=videos,credits&api_key={TMDB_API_KEY}"
        with httpx.Client() as client:
            tmdb_res = client.get(tmdb_url)
            tmdb_res.raise_for_status()
            tmdb_data = tmdb_res.json()
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"Warning: Could not fetch extra details from TMDB for movie {id}: {e}")
        return MovieDetailResponse(**db_movie_data)

    # Process trailer
    trailer_key = next((v["key"] for v in tmdb_data.get("videos", {}).get("results", []) if v.get("site") == "YouTube" and v.get("type") == "Trailer" and v.get("official")), None)
    if not trailer_key: # Fallback to any trailer
        trailer_key = next((v["key"] for v in tmdb_data.get("videos", {}).get("results", []) if v.get("site") == "YouTube" and v.get("type") == "Trailer"), None)

    # Process cast
    cast = [
        CastMember(
            id=member["id"],
            name=member["name"],
            character=member["character"],
            profile_path=f"{TMDB_IMAGE_BASE_URL}{member['profile_path']}" if member.get("profile_path") else None
        )
        for member in tmdb_data.get("credits", {}).get("cast", [])[:10]
    ]

    # Process companies
    companies = [
        Company(
            id=company["id"],
            name=company["name"],
            logo_path=f"{TMDB_IMAGE_BASE_URL}{company['logo_path']}" if company.get("logo_path") else None
        )
        for company in tmdb_data.get("production_companies", [])
    ]

    response_data = {
        **db_movie_data,
        "vote_average": tmdb_data.get("vote_average"),
        "vote_count": tmdb_data.get("vote_count"),
        "trailer_key": trailer_key,
        "cast": cast,
        "production_companies": companies,
    }

    return MovieDetailResponse(**response_data)

# Protected movie rating endpoints
@router.post("/{movie_id}/rate")
async def rate_movie(
    movie_id: int,
    rating: float = Query(..., ge=0.5, le=5.0),
    request: Request = None
):
    """
    Rate a movie (requires authentication)
    Rating scale: 0.5 to 5.0 stars
    """
    user = require_authentication(request)
    supabase = get_supabase()
    
    # Check if movie exists
    try:
        movie_resp = supabase.table("movies").select("id").eq("id", movie_id).limit(1).execute()
        if not movie_resp.data:
            raise HTTPException(status_code=404, detail="Movie not found")
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)
    
    # Insert or update rating
    rating_data = {
        "user_id": user["id"],
        "movie_id": movie_id,
        "rating": rating,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    try:
        # Use upsert to handle both insert and update
        resp = supabase.table("movie_ratings").upsert(rating_data).execute()
        return {
            "message": "Rating saved successfully",
            "rating": rating,
            "movie_id": movie_id,
            "user_id": user["id"]
        }
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

@router.get("/{movie_id}/rating")
async def get_user_movie_rating(movie_id: int, request: Request):
    """
    Get current user's rating for a movie (requires authentication)
    """
    user = require_authentication(request)
    supabase = get_supabase()
    
    try:
        resp = supabase.table("movie_ratings").select("rating, updated_at").eq("user_id", user["id"]).eq("movie_id", movie_id).limit(1).execute()
        
        if not resp.data:
            return {"rating": None, "message": "No rating found"}
        
        return {
            "rating": resp.data[0]["rating"],
            "updated_at": resp.data[0]["updated_at"],
            "movie_id": movie_id
        }
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

@router.delete("/{movie_id}/rating")
async def delete_movie_rating(movie_id: int, request: Request):
    """
    Remove user's rating for a movie (requires authentication)
    """
    user = require_authentication(request)
    supabase = get_supabase()
    
    try:
        resp = supabase.table("movie_ratings").delete().eq("user_id", user["id"]).eq("movie_id", movie_id).execute()
        
        return {
            "message": "Rating removed successfully",
            "movie_id": movie_id
        }
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

# Protected favorites endpoints
@router.post("/{movie_id}/favorite")
async def add_to_favorites(movie_id: int, request: Request):
    """
    Add movie to user's favorites (requires authentication)
    """
    user = require_authentication(request)
    supabase = get_supabase()
    
    # Check if movie exists
    try:
        movie_resp = supabase.table("movies").select("id").eq("id", movie_id).limit(1).execute()
        if not movie_resp.data:
            raise HTTPException(status_code=404, detail="Movie not found")
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)
    
    favorite_data = {
        "user_id": user["id"],
        "movie_id": movie_id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    try:
        resp = supabase.table("user_favorites").insert(favorite_data).execute()
        return {
            "message": "Movie added to favorites",
            "movie_id": movie_id
        }
    except APIError as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=409, detail="Movie already in favorites")
        raise HTTPException(status_code=int(e.code), detail=e.message)

@router.delete("/{movie_id}/favorite")
async def remove_from_favorites(movie_id: int, request: Request):
    """
    Remove movie from user's favorites (requires authentication)
    """
    user = require_authentication(request)
    supabase = get_supabase()
    
    try:
        resp = supabase.table("user_favorites").delete().eq("user_id", user["id"]).eq("movie_id", movie_id).execute()
        
        return {
            "message": "Movie removed from favorites",
            "movie_id": movie_id
        }
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

@router.get("/{movie_id}/favorite")
async def check_favorite_status(movie_id: int, request: Request):
    """
    Check if movie is in user's favorites (requires authentication)
    """
    user = require_authentication(request)
    supabase = get_supabase()
    
    try:
        resp = supabase.table("user_favorites").select("created_at").eq("user_id", user["id"]).eq("movie_id", movie_id).limit(1).execute()
        
        is_favorite = len(resp.data) > 0
        return {
            "is_favorite": is_favorite,
            "movie_id": movie_id,
            "added_at": resp.data[0]["created_at"] if is_favorite else None
        }
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

# Protected watchlist endpoints
@router.post("/{movie_id}/watchlist")
async def add_to_watchlist(movie_id: int, request: Request):
    """
    Add movie to user's watchlist (requires authentication)
    """
    user = require_authentication(request)
    supabase = get_supabase()
    
    # Check if movie exists
    try:
        movie_resp = supabase.table("movies").select("id").eq("id", movie_id).limit(1).execute()
        if not movie_resp.data:
            raise HTTPException(status_code=404, detail="Movie not found")
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)
    
    watchlist_data = {
        "user_id": user["id"],
        "movie_id": movie_id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    try:
        resp = supabase.table("user_watchlist").insert(watchlist_data).execute()
        return {
            "message": "Movie added to watchlist",
            "movie_id": movie_id
        }
    except APIError as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=409, detail="Movie already in watchlist")
        raise HTTPException(status_code=int(e.code), detail=e.message)

@router.delete("/{movie_id}/watchlist")
async def remove_from_watchlist(movie_id: int, request: Request):
    """
    Remove movie from user's watchlist (requires authentication)
    """
    user = require_authentication(request)
    supabase = get_supabase()
    
    try:
        resp = supabase.table("user_watchlist").delete().eq("user_id", user["id"]).eq("movie_id", movie_id).execute()
        
        return {
            "message": "Movie removed from watchlist",
            "movie_id": movie_id
        }
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

@router.get("/{movie_id}/watchlist")
async def check_watchlist_status(movie_id: int, request: Request):
    """
    Check if movie is in user's watchlist (requires authentication)
    """
    user = require_authentication(request)
    supabase = get_supabase()
    
    try:
        resp = supabase.table("user_watchlist").select("created_at").eq("user_id", user["id"]).eq("movie_id", movie_id).limit(1).execute()
        
        in_watchlist = len(resp.data) > 0
        return {
            "in_watchlist": in_watchlist,
            "movie_id": movie_id,
            "added_at": resp.data[0]["created_at"] if in_watchlist else None
        }
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

# Enhanced movie detail endpoint with user context
@router.get("/{id}/enhanced", response_model=MovieDetailResponse)
async def get_movie_enhanced(id: int, lite: bool = Query(False), request: Request = None):
    """
    Retrieve enriched movie details with user-specific data (rating, favorite, watchlist)
    """
    supabase = get_supabase()
    user = get_current_user_from_request(request)
    
    try:
        resp = supabase.table("movies").select("*").eq("id", id).limit(1).execute()
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

    if not resp.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    db_movie_data = resp.data[0]

    # Get user-specific data if authenticated
    user_data = {}
    if user:
        try:
            # Get user rating
            rating_resp = supabase.table("movie_ratings").select("rating").eq("user_id", user["id"]).eq("movie_id", id).limit(1).execute()
            user_data["user_rating"] = rating_resp.data[0]["rating"] if rating_resp.data else None
            
            # Get favorite status
            favorite_resp = supabase.table("user_favorites").select("created_at").eq("user_id", user["id"]).eq("movie_id", id).limit(1).execute()
            user_data["is_favorite"] = len(favorite_resp.data) > 0
            
            # Get watchlist status
            watchlist_resp = supabase.table("user_watchlist").select("created_at").eq("user_id", user["id"]).eq("movie_id", id).limit(1).execute()
            user_data["in_watchlist"] = len(watchlist_resp.data) > 0
            
        except APIError:
            # If user data fetch fails, continue without it
            pass

    # If lite is requested or TMDB key absent, return only DB data
    if lite or not TMDB_API_KEY:
        response_data = {**db_movie_data, **user_data}
        return MovieDetailResponse(**response_data)

    try:
        tmdb_url = f"{TMDB_BASE_URL}/movie/{id}?append_to_response=videos,credits&api_key={TMDB_API_KEY}"
        with httpx.Client() as client:
            tmdb_res = client.get(tmdb_url)
            tmdb_res.raise_for_status()
            tmdb_data = tmdb_res.json()
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"Warning: Could not fetch extra details from TMDB for movie {id}: {e}")
        response_data = {**db_movie_data, **user_data}
        return MovieDetailResponse(**response_data)

    # Process trailer
    trailer_key = next((v["key"] for v in tmdb_data.get("videos", {}).get("results", []) if v.get("site") == "YouTube" and v.get("type") == "Trailer" and v.get("official")), None)
    if not trailer_key: # Fallback to any trailer
        trailer_key = next((v["key"] for v in tmdb_data.get("videos", {}).get("results", []) if v.get("site") == "YouTube" and v.get("type") == "Trailer"), None)

    # Process cast
    cast = [
        CastMember(
            id=member["id"],
            name=member["name"],
            character=member["character"],
            profile_path=f"{TMDB_IMAGE_BASE_URL}{member['profile_path']}" if member.get("profile_path") else None
        )
        for member in tmdb_data.get("credits", {}).get("cast", [])[:10]
    ]

    # Process companies
    companies = [
        Company(
            id=company["id"],
            name=company["name"],
            logo_path=f"{TMDB_IMAGE_BASE_URL}{company['logo_path']}" if company.get("logo_path") else None
        )
        for company in tmdb_data.get("production_companies", [])
    ]

    response_data = {
        **db_movie_data,
        "vote_average": tmdb_data.get("vote_average"),
        "vote_count": tmdb_data.get("vote_count"),
        "trailer_key": trailer_key,
        "cast": cast,
        "production_companies": companies,
        **user_data
    }

    return MovieDetailResponse(**response_data)

# User-specific movie lists (Protected endpoints)
@router.get("/favorites", response_model=MovieListResponse)
async def get_user_favorites(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    request: Request = None
):
    """
    Get user's favorite movies (requires authentication)
    """
    user = require_authentication(request)
    supabase = get_supabase()
    
    offset = (page - 1) * per_page
    
    try:
        # Get total count
        count_resp = supabase.table("user_favorites").select("*", count="exact").eq("user_id", user["id"]).execute()
        total = count_resp.count
        
        # Get favorites with movie details
        resp = supabase.table("user_favorites").select(
            "*, movies(*)"
        ).eq("user_id", user["id"]).order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
        
        movies = []
        for favorite in resp.data:
            movie_data = favorite["movies"]
            if movie_data:
                movie_data["poster_path"] = f"{TMDB_IMAGE_BASE_URL}{movie_data['poster_path']}" if movie_data.get("poster_path") else None
                movie_data["backdrop_path"] = f"{TMDB_IMAGE_BASE_URL}{movie_data['backdrop_path']}" if movie_data.get("backdrop_path") else None
                movies.append(Movie(**movie_data))
        
        return MovieListResponse(
            movies=movies,
            page=page,
            per_page=per_page,
            total=total,
            total_pages=(total + per_page - 1) // per_page
        )
        
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

@router.get("/watchlist", response_model=MovieListResponse)
async def get_user_watchlist(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    request: Request = None
):
    """
    Get user's watchlist movies (requires authentication)
    """
    user = require_authentication(request)
    supabase = get_supabase()
    
    offset = (page - 1) * per_page
    
    try:
        # Get total count
        count_resp = supabase.table("user_watchlist").select("*", count="exact").eq("user_id", user["id"]).execute()
        total = count_resp.count
        
        # Get watchlist with movie details
        resp = supabase.table("user_watchlist").select(
            "*, movies(*)"
        ).eq("user_id", user["id"]).order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
        
        movies = []
        for watchlist_item in resp.data:
            movie_data = watchlist_item["movies"]
            if movie_data:
                movie_data["poster_path"] = f"{TMDB_IMAGE_BASE_URL}{movie_data['poster_path']}" if movie_data.get("poster_path") else None
                movie_data["backdrop_path"] = f"{TMDB_IMAGE_BASE_URL}{movie_data['backdrop_path']}" if movie_data.get("backdrop_path") else None
                movies.append(Movie(**movie_data))
        
        return MovieListResponse(
            movies=movies,
            page=page,
            per_page=per_page,
            total=total,
            total_pages=(total + per_page - 1) // per_page
        )
        
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

@router.get("/rated", response_model=MovieListResponse)
async def get_user_rated_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    min_rating: float = Query(0.5, ge=0.5, le=5.0),
    max_rating: float = Query(5.0, ge=0.5, le=5.0),
    request: Request = None
):
    """
    Get user's rated movies with optional rating filters (requires authentication)
    """
    user = require_authentication(request)
    supabase = get_supabase()
    
    offset = (page - 1) * per_page
    
    try:
        # Build query with rating filters
        base_query = supabase.table("movie_ratings").select(
            "*, movies(*)", count="exact"
        ).eq("user_id", user["id"]).gte("rating", min_rating).lte("rating", max_rating)
        
        # Get total count
        count_resp = base_query.execute()
        total = count_resp.count
        
        # Get rated movies with details
        resp = base_query.order("updated_at", desc=True).range(offset, offset + per_page - 1).execute()
        
        movies = []
        for rating_item in resp.data:
            movie_data = rating_item["movies"]
            if movie_data:
                movie_data["poster_path"] = f"{TMDB_IMAGE_BASE_URL}{movie_data['poster_path']}" if movie_data.get("poster_path") else None
                movie_data["backdrop_path"] = f"{TMDB_IMAGE_BASE_URL}{movie_data['backdrop_path']}" if movie_data.get("backdrop_path") else None
                movie_data["user_rating"] = rating_item["rating"]  # Add user's rating to movie data
                movies.append(Movie(**movie_data))
        
        return MovieListResponse(
            movies=movies,
            page=page,
            per_page=per_page,
            total=total,
            total_pages=(total + per_page - 1) // per_page
        )
        
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)

@router.get("/user-stats")
async def get_user_movie_stats(request: Request):
    """
    Get user's movie interaction statistics (requires authentication)
    """
    user = require_authentication(request)
    supabase = get_supabase()
    
    try:
        # Get favorites count
        favorites_resp = supabase.table("user_favorites").select("*", count="exact").eq("user_id", user["id"]).execute()
        favorites_count = favorites_resp.count
        
        # Get watchlist count
        watchlist_resp = supabase.table("user_watchlist").select("*", count="exact").eq("user_id", user["id"]).execute()
        watchlist_count = watchlist_resp.count
        
        # Get ratings stats
        ratings_resp = supabase.table("movie_ratings").select("rating").eq("user_id", user["id"]).execute()
        ratings_data = ratings_resp.data
        
        ratings_count = len(ratings_data)
        average_rating = sum(r["rating"] for r in ratings_data) / ratings_count if ratings_count > 0 else 0
        
        # Get rating distribution
        rating_distribution = {}
        for rating in ratings_data:
            star_level = round(rating["rating"])
            rating_distribution[star_level] = rating_distribution.get(star_level, 0) + 1
        
        return {
            "user_id": user["id"],
            "favorites_count": favorites_count,
            "watchlist_count": watchlist_count,
            "ratings_count": ratings_count,
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution
        }
        
    except APIError as e:
        raise HTTPException(status_code=int(e.code), detail=e.message)