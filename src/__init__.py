"""
Source package for the REST API.
"""

from .middleware import log_requests
from .models import (
    DatasetInfo,
    HealthResponse,
    ProcessConfig,
    ProcessingReport,
    MovieUploadInfo,
    MovieDataResponse,
    MovieProcessingReport,
)
from .storage import MovieStorage
from .cache import MovieCache
from .utils import setup_logging

__all__ = ["MovieStorage", "MovieCache"]