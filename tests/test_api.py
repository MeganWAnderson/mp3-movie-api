"""
API Tests
DS 3500 - MP3

Tests SQLite persistence, cache invalidation after processing,
and cache hits that skip the database.
"""

import pandas as pd
import pytest

from src import MovieStorage
import main

COLUMNS = ["title", "release_year", "rating", "genre"]


def test_movies_persist(client, test_storage, uploaded_movies):
    # A second storage object pointing at the same database file
    other = MovieStorage(test_storage.db_path)

    df = other.get()
    assert len(df) == 20
    assert other.count_movies() == 20
    assert list(df.columns) == COLUMNS

    expected_titles = pd.read_csv("fixtures/sample_movies.csv")["title"].tolist()
    assert df["title"].tolist() == expected_titles

    storage_ids = [row["id"] for row in other.select_columns(COLUMNS, limit=100)]
    response = client.get("/movies", params={"limit": 100})
    assert response.status_code == 200
    api_ids = [row["id"] for row in response.json()["data"]]

    assert storage_ids == list(range(1, 21))
    assert api_ids == list(range(1, 21))


def test_cache_and_processing(client, uploaded_movies, processing_body):
    # Populate the cache for two limits
    first = {}
    for limit in (100, 1):
        response = client.get("/movies", params={"limit": limit})
        assert response.status_code == 200
        first[limit] = response.json()
        assert main.cache.get(limit) == first[limit]

    # Repeat limit=100
    repeat = client.get("/movies", params={"limit": 100})
    assert repeat.status_code == 200
    assert repeat.json() == first[100]

    # Process and check the cache was cleared
    response = client.post("/movies/process", json=processing_body)
    assert response.status_code == 200
    body = response.json()
    assert body["validation_rows_removed"] == 0
    report = body["cleaning_report"]
    assert report["rows_before"] == 20
    assert report["rows_after"] == 16
    assert report["rows_removed"] == 4
    assert main.cache.get(100) is None
    assert main.cache.get(1) is None

    # Retrieve the processed data
    response = client.get("/movies", params={"limit": 100})
    assert response.status_code == 200
    body = response.json()
    assert body["total_rows"] == 16
    assert [r["title"] for r in body["data"]] == [f"Movie {c}" for c in "ABCDEFGHIJKLMNOP"]
    assert [r["id"] for r in body["data"]] == list(range(1, 17))
    assert main.cache.get(100) == body


def test_cache_hit_skips_database(client, uploaded_movies, monkeypatch):
    # Populate the cache
    first = client.get("/movies", params={"limit": 100})
    assert first.status_code == 200

    # Make any database read fail the test
    def fail_if_called(*args, **kwargs):
        pytest.fail("Database was accessed on a cache hit")

    monkeypatch.setattr(main.storage, "select_columns", fail_if_called)
    monkeypatch.setattr(main.storage, "count_movies", fail_if_called)

    # The repeat request must come from the cache
    second = client.get("/movies", params={"limit": 100})
    assert second.status_code == 200
    assert second.json() == first.json()