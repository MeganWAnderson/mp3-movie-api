"""
Data Loaders
DS 3500 - MP1

Loads CSV, JSON, and YAML files using the appropriate parser.
Returns a DataFrame for CSV files and Python objects
for JSON and YAML files.
"""

# Imports
import json
from pathlib import Path
import logging

import pandas as pd
import yaml

# Use the logging configuration set up by the main pipeline.
logger = logging.getLogger(__name__)

# Define load functions
def load_csv(filepath):
    """
    Load a CSV file into a DataFrame.
    Args:
        filepath: Path to the CSV file.
    Returns:
        DataFrame containing the CSV data.
    """
    df = pd.read_csv(filepath)
    logger.info(f"Loaded CSV file: {filepath} ({len(df)} rows)")
    return df

def load_json(filepath):
    """
    Load a JSON file into a Python object (dict or list).
    Args:
        filepath: Path to the JSON file.
    Returns:
        Python object containing the JSON data.
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    logger.info(f"Loaded JSON file: {filepath}")
    return data

def load_yaml(filepath):
    """
    Load a YAML file into a Python object (dict or list).
    Args:
        filepath: Path to the YAML file.
    Returns:
        Python object containing the YAML data.
    """
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    logger.info(f"Loaded YAML file: {filepath}")
    return data
    
# Final Load Function
def load_data(filepath):
    """
    Load a file using its extension.
    Args:
        filepath: File path as a string or Path object.
    Returns:
        DataFrame for CSV files, or a Python object for JSON/YAML files.
    Raises:
        ValueError: If the file extension is unsupported.
    """
    filepath = Path(filepath)
    extension = filepath.suffix.lower()
    if extension == ".csv":
        return load_csv(filepath)
    elif extension == ".json":
        return load_json(filepath)
    elif extension == ".yaml" or extension == ".yml":
        return load_yaml(filepath)
    else:
        logger.error(f"Unsupported file format: {filepath.suffix}")
        raise ValueError(f"Unsupported file format: {filepath.suffix}")
