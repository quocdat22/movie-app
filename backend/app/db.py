"""Supabase client setup for backend FastAPI service."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import cast

from supabase import Client, create_client  # type: ignore
from dotenv import load_dotenv  # type: ignore

# Load environment variables from a .env file if present (no override of existing vars)
load_dotenv()

ENV_SUPABASE_URL = "SUPABASE_URL"
ENV_SUPABASE_SERVICE_ROLE_KEY = "SUPABASE_SERVICE_ROLE_KEY"


def _get_env(var: str) -> str:
    value = os.getenv(var)
    if not value:
        raise RuntimeError(f"Environment variable '{var}' is required but not set.")
    return cast(str, value)


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """Return a cached Supabase client instance.

    We use SERVICE_ROLE key since the backend needs full CRUD access.
    The key **must** be kept secret and never exposed to the frontend.
    """
    supabase_url = _get_env(ENV_SUPABASE_URL)
    service_role_key = _get_env(ENV_SUPABASE_SERVICE_ROLE_KEY)

    return create_client(supabase_url, service_role_key) 