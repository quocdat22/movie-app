"""Pytest tests for movie endpoints using FastAPI TestClient with mocked Supabase client."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable, List

import pytest  # type: ignore
from fastapi.testclient import TestClient  # type: ignore

from backend.app.main import app
import backend.app.routers.movies as movies_router


# Sample dataset for tests
_SAMPLE_MOVIES: List[dict[str, Any]] = [
    {
        "id": 1,
        "title": "Movie One",
        "overview": "Overview 1",
        "release_year": 2020,
        "poster_url": None,
        "genre": ["Action"],
        "cast_ids": [],
        "company_ids": [],
        "keyword_ids": [],
        "created_at": "2020-01-01T00:00:00Z",
        "updated_at": "2020-01-01T00:00:00Z",
        "popularity": 50,
    },
    {
        "id": 2,
        "title": "Movie Two",
        "overview": "Overview 2",
        "release_year": 2021,
        "poster_url": None,
        "genre": ["Drama", "Action"],
        "cast_ids": [],
        "company_ids": [],
        "keyword_ids": [],
        "created_at": "2021-01-01T00:00:00Z",
        "updated_at": "2021-01-01T00:00:00Z",
        "popularity": 70,
    },
]


class _Response(SimpleNamespace):
    """Mimic Supabase response structure."""

    def __init__(self, data, count=None, status_code=200):
        super().__init__(data=data, count=count, status_code=status_code)


class _FakeQuery:
    def __init__(self, data: List[dict[str, Any]]):
        # underlying data list is copied
        self._data = list(data)
        self._filters: List[Callable[[dict[str, Any]], bool]] = []
        self._text_search_term: str | None = None
        self._order_field: str | None = None
        self._order_desc: bool = False
        self._start: int | None = None
        self._end: int | None = None
        self._count_requested: bool = False
        self._limit: int | None = None

    # Filtering methods
    def contains(self, field: str, values: List[str]):  # type: ignore[override]
        value_set = set(values)
        self._filters.append(lambda row: value_set.issubset(set(row.get(field, []))))
        return self

    def eq(self, field: str, value: Any):
        self._filters.append(lambda row: row.get(field) == value)
        return self

    def gte(self, field: str, value: Any):
        self._filters.append(lambda row: row.get(field) is not None and row[field] >= value)
        return self

    def lte(self, field: str, value: Any):
        self._filters.append(lambda row: row.get(field) is not None and row[field] <= value)
        return self

    # Text search (simplified contains, case-insensitive)
    def text_search(self, field: str, term: str, config: str = "english"):
        self._text_search_term = term.lower()
        self._filters.append(lambda row: self._text_search_term in row.get(field, "").lower())
        return self

    def limit(self, count: int):
        self._limit = count
        return self

    # Selecting / counting
    def select(self, *fields: str, count: str | None = None):  # noqa: D401
        # For simplicity, we ignore field selection.
        self._count_requested = count is not None
        return self

    # Ordering
    def order(self, field: str, desc: bool = False):
        self._order_field = field
        self._order_desc = desc
        return self

    # Pagination
    def range(self, start: int, end: int):  # noqa: A003
        self._start = start
        self._end = end
        return self

    # Execute and build response
    def execute(self):
        data = self._data
        # Apply filters
        for f in self._filters:
            data = list(filter(f, data))

        # Ordering
        if self._order_field:
            data.sort(key=lambda r: r.get(self._order_field, 0), reverse=self._order_desc)  # type: ignore[arg-type]
        # Count
        if self._count_requested:
            return _Response(data=[], count=len(data))
        # Pagination
        if self._start is not None and self._end is not None:
            data = data[self._start : self._end + 1]
        elif self._limit is not None:
            data = data[: self._limit]

        return _Response(data=data)


class _FakeSupabaseClient:
    def __init__(self, data: List[dict[str, Any]]):
        self._data = data

    def table(self, name: str):  # pylint: disable=unused-argument
        return _FakeQuery(self._data)


@pytest.fixture(autouse=True)
def _override_supabase(monkeypatch):
    """Automatically override get_supabase dependency for all tests."""
    fake_client = _FakeSupabaseClient(_SAMPLE_MOVIES)
    monkeypatch.setattr(movies_router, "get_supabase", lambda: fake_client)
    yield


def test_list_movies():
    client = TestClient(app)
    resp = client.get("/movies?page=1&page_size=10")
    assert resp.status_code == 200
    body = resp.json()
    assert body["pagination"]["total_items"] == 2
    assert len(body["data"]) == 2


def test_get_movie_success():
    client = TestClient(app)
    resp = client.get("/movies/1")
    assert resp.status_code == 200
    assert resp.json()["id"] == 1


def test_get_movie_not_found():
    client = TestClient(app)
    resp = client.get("/movies/999")
    assert resp.status_code == 404


def test_search_movies():
    client = TestClient(app)
    resp = client.get("/movies/search?q=Movie&page_size=10")
    assert resp.status_code == 200
    body = resp.json()
    assert body["pagination"]["total_items"] == 2
    # search term 'Movie' matches both sample movies
    assert len(body["data"]) == 2
    resp2 = client.get("/movies/search?q=Two")
    assert resp2.status_code == 200
    assert len(resp2.json()["data"]) == 1 


def test_list_movies_genre_filter():
    client = TestClient(app)
    # Filter by Drama genre; only second movie matches
    resp = client.get("/movies", params={"genre": ["Drama"]})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["id"] == 2


def test_list_movies_release_year_range():
    client = TestClient(app)
    # release_year_lte = 2020 should return only movie with year 2020
    resp = client.get("/movies", params={"release_year_lte": 2020})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["release_year"] == 2020


def test_list_movies_pagination():
    client = TestClient(app)
    # page size 1 should return first item; page 2 second item
    resp_page1 = client.get("/movies", params={"page": 1, "page_size": 1})
    resp_page2 = client.get("/movies", params={"page": 2, "page_size": 1})

    assert resp_page1.status_code == 200 and resp_page2.status_code == 200

    data1 = resp_page1.json()["data"]
    data2 = resp_page2.json()["data"]

    assert len(data1) == 1 and len(data2) == 1
    assert data1[0]["id"] != data2[0]["id"] 