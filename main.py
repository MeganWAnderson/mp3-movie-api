"""
Movie API
DS 3500 - MP3

FastAPI application that uploads movie CSVs, stores them in SQLite,
and retrieves, searches, and processes movies using SQL and MP1 modules.
"""

# Imports
import io
import logging
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile

# Local Imports
from data_pipeline import create_cleaning_report, process_data, validate_dataframe
from src import (
    HealthResponse,
    MovieDataResponse,
    MovieProcessingReport,
    MovieStorage,
    MovieUploadInfo,
    ProcessConfig,
    log_requests,
    setup_logging,
)
from src.storage import MOVIE_COLUMNS


# Set up logging
setup_logging(verbose=True)
logger = logging.getLogger(__name__)

# Set up FastAPI app and dataset storage
app = FastAPI(title="Data Processing API", version="1.0.0")
app.middleware("http")(log_requests)
storage = MovieStorage()

# API Endpoints
@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return HealthResponse(status="ok", version="1.0.0")


@app.post("/upload", response_model=MovieUploadInfo)
async def upload_movies(file: UploadFile = File(...)):
    """Read and store a CSV upload."""
    # Extension check and CSV parsing (unchanged from MP2)
    extension = Path(file.filename or "").suffix.lower()
    if extension != ".csv":
        logger.warning(f"Unsupported file format: {extension}")
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except pd.errors.EmptyDataError:
        logger.warning(f"Uploaded CSV file is empty: {file.filename}")
        raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")
    except pd.errors.ParserError:
        logger.warning(f"Uploaded file could not be parsed as CSV: {file.filename}")
        raise HTTPException(status_code=400, detail="Uploaded file could not be parsed as CSV.")
    except UnicodeDecodeError:
        logger.warning(f"Uploaded file is not valid UTF-8 text: {file.filename}")
        raise HTTPException(status_code=400, detail="Uploaded file is not valid UTF-8 text.")

    # Quick validation before saving
    if sorted(df.columns) != sorted(MOVIE_COLUMNS):
        logger.warning(f"Unexpected columns: {list(df.columns)}")
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain columns: {MOVIE_COLUMNS}",
        )
    if df.empty:
        logger.warning(f"Uploaded CSV file is empty: {file.filename}")
        raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")

    df = df[MOVIE_COLUMNS]

    # Replace the stored collection
    storage.save(df)
    logger.info(f"Uploaded movies: filename={file.filename}, rows={len(df)}")

    return MovieUploadInfo(
        filename=file.filename,
        rows=len(df),
        columns=len(df.columns),
        column_names=list(df.columns),
    )


@app.get("/movies", response_model=MovieDataResponse)
def get_movies(limit: int = Query(default=100, ge=1)):
    """Return up to limit stored movies and the total count."""
    # Use MovieStorage methods to retrieve up to limit rows and count the total number of stored movies.
    # Return {"data": ..., "total_rows": ...}.
    # If empty, return {"data": [], "total_rows": 0}.
    # Log the row count at INFO.
    records = storage.select_columns(MOVIE_COLUMNS, limit=limit)
    total = storage.count_movies()
    logger.info(f"Retrieved movies: returned_rows={len(records)}, total_rows={total}")
    return MovieDataResponse(data=records, total_rows=total)

@app.get("/movies/search", response_model=list[dict])
def query_movies(
    columns: list[str] = Query(default=["title"]),
    min_rating: float = Query(default=0, ge=0, le=10),
    limit: int = Query(default=100, ge=1)
):
    # Call storage.query_movies(columns, min_rating, limit).
    # Catch ValueError and raise HTTPException with status 400.
    # Return id plus the selected fields, or [] if there are no matches.
    # Log the selected columns and returned row count at INFO.
    try:
        records = storage.query_movies(columns, min_rating, limit)
        logger.info(f"Queried movies: columns={columns}, min_rating={min_rating}, returned_rows={len(records)}")
        return records
    except ValueError as e:
        logger.warning(f"Query failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/movies/process", response_model=MovieProcessingReport)
def process_movies(config: ProcessConfig):
    """Validate and process the stored movies using MP1 functions."""

    # Retrieve a copy of the stored dataset.
    df = storage.get()
    if df.empty:
        logger.warning("No movies stored. Upload a CSV first.")
        raise HTTPException(status_code=400, detail="No movies stored. Upload a CSV first.")

    # Convert the request model to the dict format MP1 expects.
    config_dict = config.model_dump()
    required = config_dict["validation"]["required_columns"]
    numeric = config_dict["validation"]["numeric_columns"]

    # Check numeric columns exist
    missing_cols = [col for col in numeric if col not in df.columns]
    if missing_cols:
        logger.warning(f"Numeric columns not found: {missing_cols}")
        raise HTTPException(
            status_code=400,
            detail=f"Numeric columns not found: {missing_cols}",
        )

    # Validate, then process a copy of the validated data
    try:
        validated = validate_dataframe(
            df, required_columns=required, numeric_columns=numeric
        )
        validation_rows_removed = len(df) - len(validated)
        validated_copy = validated.copy()

        processed = process_data(validated_copy, config_dict)
        cleaning_report = create_cleaning_report(validated_copy, processed)
    except ValueError as error:
        logger.warning(f"Processing failed due to validation or processing error: {error}")
        raise HTTPException(status_code=400, detail=str(error))

    # TODO 3: Save the processed DataFrame using storage.save().
    # Return validation_rows_removed and cleaning_report without a dataset ID.
    storage.save(processed)

    logger.info(
        f"Processed movies: "
        f"validation_rows_removed={validation_rows_removed}, "
        f"rows_before={cleaning_report['rows_before']}, "
        f"rows_after={cleaning_report['rows_after']}"
    )

    return {
        "validation_rows_removed": validation_rows_removed,
        "cleaning_report": cleaning_report,
    }
