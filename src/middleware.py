"""
Request Logging Middleware
DS 3500 - MP2

Assigns each request a short ID, logs its method, path, status code,
and duration, and returns the ID in the X-Request-ID response header.
"""

# Imports
import logging
import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse

# Set up logging
logger = logging.getLogger(__name__)


async def log_requests(request: Request, call_next):
    """Log one request and attach its request ID to the response."""
    request_id = uuid.uuid4().hex[:8]
    request.state.request_id = request_id
    started = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        # Log the full traceback, but don't expose details to the client
        logger.error(
            f"Unhandled error: request_id={request_id}", exc_info=True
        )
        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

    duration_ms = (time.perf_counter() - started) * 1000

    # Build one log line summarizing the request
    message = (
        f"request_id={request_id} {request.method} {request.url.path} "
        f"status={response.status_code} duration={duration_ms:.1f}ms"
    )

    # ERROR for server errors, WARNING for client errors, INFO otherwise
    if 500 <= response.status_code < 600:
        logger.error(message)
    elif 400 <= response.status_code < 500:
        logger.warning(message)
    else:
        logger.info(message)

    response.headers["X-Request-ID"] = request_id
    return response
