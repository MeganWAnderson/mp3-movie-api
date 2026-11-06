"""
Test Fixtures
DS 3500 - MP2

Shared pytest fixtures for the API tests: a test client with
empty storage, sample CSV data, an uploaded dataset, and a
default processing request body.
"""

# Imports
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app, storage


@pytest.fixture
def client():
    """Provide a TestClient, clearing storage before and after each test."""
    storage.clear()
    with TestClient(app) as test_client:
        yield test_client
    storage.clear()


@pytest.fixture
def sample_csv_bytes():
    """Return the raw bytes of the sample CSV file."""
    filepath = Path("fixtures") / "sample_data.csv"
    return filepath.read_bytes()


@pytest.fixture
def uploaded_dataset_id(client, sample_csv_bytes):
    """Upload a fresh copy of the sample CSV and return its dataset ID."""
    response = client.post(
        "/upload",
        files={
            "file": (
                "sample_data.csv",
                sample_csv_bytes,
                "text/csv"
            )
        }
    )
    assert response.status_code == 200
    return response.json()["id"]


@pytest.fixture
def processing_body():
    """Return a config that validates score, removes duplicates and
    missing rows, and skips outlier removal."""
    return {
        "validation": {
            "required_columns": ["student_id", "score"],
            "numeric_columns": ["score"]
        },
        "processing": {
            "remove_duplicates": True,
            "missing": {
                "enabled": True,
                "axis": "rows"
            },
            "outliers": {
                "enabled": False,
                "columns": [],
                "method": "iqr",
                "threshold": 1.5
            }
        }
    }