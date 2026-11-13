"""
Test Fixtures
DS 3500 - MP3

Shared pytest fixtures for the API tests: a temporary SQLite storage,
a fresh cache, a test client, the sample movie CSV, an uploaded
collection, and the default processing request body.
"""

# Imports
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import main
from src import MovieCache, MovieStorage


@pytest.fixture
def test_storage(tmp_path):
    """Return a MovieStorage backed by a temporary database file."""
    return MovieStorage(tmp_path / "test_movies.db")


@pytest.fixture
def client(test_storage, monkeypatch):
    """Provide a TestClient using test storage and a fresh cache."""
    monkeypatch.setattr(main, "storage", test_storage)
    monkeypatch.setattr(main, "cache", MovieCache())
    with TestClient(main.app) as test_client:
        yield test_client


@pytest.fixture
def sample_csv_bytes():
    """Return the raw bytes of the sample movie CSV."""
    return (Path("fixtures") / "sample_movies.csv").read_bytes()


@pytest.fixture
def uploaded_movies(client, sample_csv_bytes):
    """Upload the sample movies and return the upload response."""
    response = client.post(
        "/upload",
        files={"file": ("sample_movies.csv", sample_csv_bytes, "text/csv")}
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def processing_body():
    """Return a config that validates all movie columns, removes
    duplicates and missing rows, and removes rating outliers."""
    return {
        "validation": {
            "required_columns": ["title", "release_year", "rating", "genre"],
            "numeric_columns": ["release_year", "rating"]
        },
        "processing": {
            "remove_duplicates": True,
            "missing": {"enabled": True, "axis": "rows"},
            "outliers": {
                "enabled": True,
                "columns": ["rating"],
                "method": "iqr",
                "threshold": 1.5
            }
        }
    }