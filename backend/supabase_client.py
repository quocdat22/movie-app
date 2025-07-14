"""Supabase client factory.

This module exposes a single function `get_supabase()` that returns
an initialized Supabase client. The credentials are read from
environment variables so **never** hard-code keys.

Environment variables expected (see .env file):
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY depending on usage)
"""
from functools import lru_cache
from os import getenv

from supabase import create_client, Client  # type: ignore


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """Return a cached Supabase client instance."""
    url = getenv("SUPABASE_URL")
    key = getenv("SUPABASE_SERVICE_ROLE_KEY") or getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError(
            "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY/NEXT_PUBLIC_SUPABASE_ANON_KEY"
        )

    return create_client(url, key) 