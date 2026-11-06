"""
Logging Utilities
DS 3500 - MP2

Configures application-wide logging with a consistent format,
reused from the MP1 pipeline.
"""

# Imports
import logging


def setup_logging(verbose=False):
    """
    Configure logging for the application.

    Args:
        verbose: If True, log at DEBUG level; otherwise log at INFO.
    """
    # DEBUG when verbose, otherwise INFO
    level = logging.DEBUG if verbose else logging.INFO

    # Each entry shows time, level, logger name, and message
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S"
    )