"""FastAPI application entrypoint."""
from __future__ import annotations

import logging

from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

from .routers import movies as movies_router

logger = logging.getLogger("uvicorn")

app = FastAPI(title="Movie Service API", version="1.0.0")

# CORS (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movies_router.router)


@app.get("/healthz")
def health_check() -> dict[str, str]:
    """Simple health-check endpoint."""
    return {"status": "ok"} 