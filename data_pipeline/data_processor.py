"""
Data Processor
DS 3500 - MP1

Cleans DataFrames by removing duplicates, handling missing values,
and removing outliers based on the configured processing steps.
Also generates a report summarizing the cleaning results.
"""

# Imports
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def remove_duplicates(df):
    """
    Remove duplicate rows from a DataFrame.
    Args:
        df: DataFrame to clean.
    Returns:
        DataFrame with duplicate rows removed.
    """
    rows_start = len(df)
    clean_df = df.drop_duplicates()
    rows_removed = rows_start - len(clean_df)

    logger.debug(f"Removed {rows_removed} duplicate rows.")
    return clean_df

def handle_missing(df, axis="rows"):
    """
    Drop rows or columns containing missing values.
    Args:
        df: DataFrame to clean.
        axis: Axis along which to drop missing values ('rows' or 'columns').
    Returns:
        DataFrame with missing values dropped.
    """
    rows_start = len(df)
    cols_start = len(df.columns)

    if axis == "rows":
        clean_df = df.dropna(axis=0)
        rows_end = len(clean_df)
        logger.debug(f"Dropped {rows_start - rows_end} rows with missing values.")
    elif axis == "columns":
        clean_df = df.dropna(axis=1)
        cols_end = len(clean_df.columns)
        logger.debug(f"Dropped {cols_start - cols_end} columns with missing values.")
    else:
        logger.error(f"Invalid axis specified: {axis}. Must be 'rows' or 'columns'.")
        raise ValueError("Invalid axis specified. Must be 'rows' or 'columns'.")

    return clean_df

def remove_outliers(df, columns, method, threshold):
    """
    Remove outliers from specified columns using the given method and threshold.
    Args:
        df: DataFrame to clean.
        columns: List of column names to check for outliers.
        method: Method to use for outlier detection ('zscore' or 'iqr').
        threshold: Threshold value for the chosen method.
    Returns:
        DataFrame with outliers removed from specified columns.
    Raises:
        ValueError: If an invalid method is specified.
    """
    if method not in ("zscore", "iqr"):
        logger.error(f"Invalid method specified: {method}. Must be 'zscore' or 'iqr'.")
        raise ValueError("Invalid method specified. Must be 'zscore' or 'iqr'.")

    clean_df = df.copy()

    for col in columns:
        if col not in clean_df.columns:
            logger.warning(f"Column '{col}' not found in DataFrame. Skipping outlier removal for this column.")
            continue

        if not pd.api.types.is_numeric_dtype(clean_df[col]):
            logger.warning(f"Column '{col}' is not numeric. Skipping outlier removal for this column.")
            continue

        rows_start = len(clean_df)

        if method == "zscore":
            mean = clean_df[col].mean()
            std = clean_df[col].std()

            # Avoid calculating z-scores for entirely missing columns.
            if pd.isna(std) or std == 0:
                logger.warning(f"Standard deviation for column '{col}' is zero or NaN. Skipping outlier removal for this column.")
                continue

            z_scores = (clean_df[col] - mean) / std
            clean_df = clean_df[abs(z_scores) <= threshold]
            logger.debug(f"Removed {rows_start - len(clean_df)} outliers from column '{col}' using z-score method with threshold {threshold}.")

        else: # method == "iqr"
            Q1 = clean_df[col].quantile(0.25)
            Q3 = clean_df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR

            # Keep missing values
            keep_rows = (clean_df[col].isna() | ( (clean_df[col] >= lower_bound) & (clean_df[col] <= upper_bound) ) )
            clean_df = clean_df[keep_rows]

            logger.debug(f"Removed {rows_start - len(clean_df)} outliers from column '{col}' using IQR method with threshold {threshold}.")

    return clean_df

def process_data(df, config):
    """
    Process the DataFrame according to the specified configuration.
    Args:
        df: DataFrame to process.
        config: Dictionary containing processing configuration.
    Returns:
        Processed DataFrame.
    """
    processing = config.get("processing", {})

    # Remove duplicate rows if specified
    if processing.get("remove_duplicates", False):
        df = remove_duplicates(df)

    # Handle missing values if specified
    missing_config = processing.get("missing", {})
    if missing_config.get("enabled", False):
        axis = missing_config.get("axis", "rows")
        df = handle_missing(df, axis=axis)

    # Remove outliers if specified
    outliers_config = processing.get("outliers", {})
    if outliers_config.get("enabled", False):
        columns = outliers_config.get("columns", [])
        method = outliers_config.get("method", "zscore")
        threshold = outliers_config.get("threshold", 3)
        df = remove_outliers(df, columns, method, threshold)

    return df

def create_cleaning_report(df_before, df_after):
    """
    Create a report summarizing the cleaning results.
    Args:
        df_before: DataFrame before cleaning.
        df_after: DataFrame after cleaning.
    Returns:
        Dictionary containing the cleaning report.
    """
    report = {
        "rows_before": len(df_before),
        "rows_after": len(df_after),
        "columns_before": len(df_before.columns),
        "columns_after": len(df_after.columns),
        "rows_removed": len(df_before) - len(df_after),
        "columns_removed": len(df_before.columns) - len(df_after.columns)
    }

    return report