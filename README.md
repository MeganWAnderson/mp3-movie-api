# MP3 Movie API

This FastAPI application stores a movie collection in SQLite and serves it through a small REST API. `POST /upload` reads a CSV with `title`, `release_year`, `rating`, and `genre` columns, checks the columns, and replaces the stored collection using `MovieStorage` in `src/storage.py`. `GET /movies` retrieves movies with a SQL query and returns them along with the total row count, while `GET /movies/search` filters movies by minimum rating and returns selected columns. `POST /movies/process` loads the stored movies, validates and cleans them with the MP1 `data_pipeline` functions (duplicates, missing values, and IQR outliers), and saves the cleaned result back to SQLite. Repeated `GET /movies` requests are cached in `src/cache.py` using FakeRedis, with one entry per `limit` that expires after 90 seconds. Whenever an upload or processing request saves new data successfully, the whole cache is cleared so later requests never return outdated movies. Because the data lives in SQLite, it survives server restarts, while the cache lives only in memory.

## Running the API

```bash
python -m uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs.

## Running the Tests

```bash
python -m pytest tests -v
```

## Sample Processing Request

After uploading `fixtures/sample_movies.csv`, send this body to `POST /movies/process`:

```json
{
  "validation": {
    "required_columns": ["title", "release_year", "rating", "genre"],
    "numeric_columns": ["release_year", "rating"]
  },
  "processing": {
    "remove_duplicates": true,
    "missing": {"enabled": true, "axis": "rows"},
    "outliers": {"enabled": true, "columns": ["rating"], "method": "iqr", "threshold": 1.5}
  }
}
```

Expected response:

```json
{
  "validation_rows_removed": 0,
  "cleaning_report": {
    "rows_before": 20,
    "rows_after": 16,
    "rows_removed": 4,
    "columns_before": 4,
    "columns_after": 4,
    "columns_removed": 0
  }
}
```