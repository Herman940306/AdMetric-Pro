"""CSV Reader module for AdMetric Pro.

This module handles the ingestion and validation of Meta Ads CSV exports,
mapping raw column names to standardized internal names for processing.
"""

import logging
from pathlib import Path

import pandas as pd

# Configure module logger
logger = logging.getLogger(__name__)

# Required columns from Meta Ads export
REQUIRED_COLUMNS = [
    "Campaign Name",
    "Amount Spent (ZAR)",
    "Link Clicks",
    "Impressions",
]

# Column mapping: Meta Ads export name -> internal name
COLUMN_MAPPING = {
    "Campaign Name": "campaign_name",
    "Amount Spent (ZAR)": "amount_spent",
    "Link Clicks": "link_clicks",
    "Impressions": "impressions",
}


def read_meta_csv(file_path: str) -> pd.DataFrame:
    """Read and validate a Meta Ads CSV file.

    Loads a CSV file exported from Meta Ads Manager, validates that all
    required columns are present, and returns a DataFrame with standardized
    column names ready for metric calculations.

    Args:
        file_path: Path to the Meta Ads CSV file.

    Returns:
        DataFrame with mapped columns: campaign_name, amount_spent,
        link_clicks, impressions.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If required columns are missing or CSV is malformed.

    Example:
        >>> df = read_meta_csv("exports/meta_ads_dec.csv")
        >>> print(df.columns.tolist())
        ['campaign_name', 'amount_spent', 'link_clicks', 'impressions']
    """
    path = Path(file_path)

    # Validate file exists
    logger.info("Checking file path: %s", path)
    if not path.exists():
        logger.error("File not found: %s", path)
        raise FileNotFoundError(f"Meta Ads CSV file not found: {path}")

    # Validate file extension
    if path.suffix.lower() != ".csv":
        logger.error("Invalid file type: %s (expected .csv)", path.suffix)
        raise ValueError(f"Expected CSV file, got: {path.suffix}")

    # Read CSV file with Campaign Name as string to preserve values like "00" and "NULL"
    logger.info("Reading Meta Ads CSV file...")
    try:
        df = pd.read_csv(path, dtype={"Campaign Name": str}, keep_default_na=False, na_values=[])
    except pd.errors.EmptyDataError:
        logger.error("CSV file is empty: %s", path)
        raise ValueError(f"CSV file is empty: {path}")
    except pd.errors.ParserError as e:
        logger.error("Failed to parse CSV file: %s", e)
        raise ValueError(f"Invalid CSV format: {e}")

    logger.info("Loaded %d campaign records from CSV", len(df))

    # Validate required columns
    logger.info("Mapping Meta Ads columns...")
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        logger.error("Missing required columns: %s", missing_columns)
        raise ValueError(
            f"Missing required columns in CSV: {', '.join(missing_columns)}"
        )

    # Extract and rename columns
    df_mapped = df[REQUIRED_COLUMNS].copy()
    df_mapped.rename(columns=COLUMN_MAPPING, inplace=True)

    # Ensure correct data types
    logger.info("Validating data types...")
    df_mapped["campaign_name"] = df_mapped["campaign_name"].astype(str)
    df_mapped["amount_spent"] = pd.to_numeric(df_mapped["amount_spent"], errors="coerce").fillna(0.0)
    df_mapped["link_clicks"] = pd.to_numeric(df_mapped["link_clicks"], errors="coerce").fillna(0).astype(int)
    df_mapped["impressions"] = pd.to_numeric(df_mapped["impressions"], errors="coerce").fillna(0).astype(int)

    logger.info("Successfully mapped %d campaigns with columns: %s", 
                len(df_mapped), df_mapped.columns.tolist())

    return df_mapped
