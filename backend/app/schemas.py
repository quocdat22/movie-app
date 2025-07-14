"""Pydantic schema models corresponding to the OpenAPI spec."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl  # type: ignore


class Movie(BaseModel):
    """Movie record as stored in Supabase."""

    id: int = Field(..., json_schema_extra={"example": 634649})
    title: str = Field(..., json_schema_extra={"example": "Spider-Man: No Way Home"})
    overview: Optional[str] = None
    release_year: Optional[int] = Field(None, ge=1888, json_schema_extra={"example": 2021})
    poster_url: Optional[HttpUrl] = None
    genre: Optional[List[str]] = None
    cast_ids: Optional[List[int]] = None
    company_ids: Optional[List[int]] = None
    keyword_ids: Optional[List[int]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CastMember(BaseModel):
    id: int
    name: str
    character: str
    profile_path: Optional[str] = None


class Company(BaseModel):
    id: int
    name: str
    logo_path: Optional[str] = None


class MovieDetailResponse(Movie):
    """Enriched movie details including data from TMDB."""

    vote_average: Optional[float] = Field(None, json_schema_extra={"example": 8.1})
    vote_count: Optional[int] = Field(None, json_schema_extra={"example": 14500})
    trailer_key: Optional[str] = Field(None, json_schema_extra={"example": "JfVOs4VSpmA"})
    cast: List[CastMember] = []
    production_companies: List[Company] = []


class Pagination(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    total_pages: int
    total_items: int


class MovieListResponse(BaseModel):
    data: List[Movie]
    pagination: Pagination


class GenreListResponse(BaseModel):
    data: List[str]


class ErrorResponse(BaseModel):
    detail: str 