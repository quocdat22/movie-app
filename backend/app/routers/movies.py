"""FastAPI router implementing movie endpoints."""
from __future__ import annotations

import os
import httpx
from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status  # type: ignore
from postgrest.exceptions import APIError

from ..db import get_supabase
from ..schemas import Movie, MovieListResponse, Pagination, MovieDetailResponse, CastMember, Company, GenreListResponse

router = APIRouter(prefix="/movies", tags=["Movies"])

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


def _paginate(total_items: int, page: int, page_size: int) -> Pagination:
    total_pages = (total_items + page_size - 1) // page_size
    return Pagination(page=page, page_size=page_size, total_pages=total_pages, total_items=total_items)


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
    pagination = Pagination(page=page, page_size=page_size, total_pages=total_pages_est, total_items=total_items_est)

    return MovieListResponse(data=movies, pagination=pagination)


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
    pagination = _paginate(total_items, page, page_size)
    return MovieListResponse(data=movies, pagination=pagination)


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