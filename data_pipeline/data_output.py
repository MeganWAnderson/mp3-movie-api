"""
Data Output
DS 3500 - MP1

Saves the processed DataFrame to a CSV file and ensures
the output directory exists.
"""

# Imports
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Define save function
def save_data(df, filepath):
    """"
    Save a DataFrame as a CSV file.

    Args:
        df: DataFrame to save.
        filepath: Destination path for the output CSV file.

    Returns:
        Path to the saved CSV file.
    """
    path = Path(filepath)

    # Create the output directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    # Save the DataFrame to a CSV file
    df.to_csv(path, index=False)
    logger.debug(f"Saved {len(df)} rows to {path}")

    return path