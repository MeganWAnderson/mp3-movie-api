"""
Pipeline Utilities
DS 3500 - MP1

Configures logging for the pipeline and checks that an
input path exists and is a file.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def setup_logging(verbose=False):
    """Configure logging for the pipeline."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S"
    )

def validate_input(filepath):
    """Check whether the input path exists and is a file."""
    path = Path(filepath)
    if not path.exists():
        logger.error(f"Input file does not exist: {filepath}")
        return False
    if not path.is_file():
        logger.error(f"Input path is not a file: {filepath}")
        return False
    logger.info(f"Input file validated: {filepath}")
    return True
