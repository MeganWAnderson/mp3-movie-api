"""
Data Validator
DS 3500 - MP1

Validates input DataFrames before data processing.

Checks for required columns, removes rows containing invalid
numeric values, converts numeric columns to numeric data types,
and logs validation results.
"""

# Imports
import logging
import pandas as pd


logger = logging.getLogger(__name__)

# Define validation function
def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data.

    Args:
        df: DataFrame to validate.
        required_columns: Column names that must exist.
        numeric_columns: Column names whose values should be numeric.

    Returns:
        DataFrame with invalid numeric rows removed and numeric
        columns converted to numeric data types.

    Raises:
        ValueError: If required columns are missing.
    """

    # Create static before df for comparison 
    before_rows = len(df)

    # Check for required columns
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Remove rows with invalid values in numeric columns.
    for col in numeric_columns:
        invalid_rows = []
        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except ValueError:
                    # Log a warning and record this row's index.
                    invalid_rows.append(i)
        if invalid_rows:
            logger.warning(f"Removed {len(invalid_rows)} rows with invalid numeric values from column '{col}'")
        df = df.drop(index=invalid_rows)

        # Convert to a numeric data type.
        df[col] = pd.to_numeric(df[col])


    logger.debug(f"Validation: {before_rows} --> {len(df)} rows")
    return df