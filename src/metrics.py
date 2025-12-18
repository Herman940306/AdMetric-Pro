"""Metrics Calculator module for AdMetric Pro.

This module provides functions to calculate key advertising performance
metrics (CTR and CPC) with robust zero-division protection, ensuring
reliable calculations even with edge-case campaign data.
"""

import logging

import pandas as pd

# Configure module logger
logger = logging.getLogger(__name__)


def calculate_ctr(clicks: int, impressions: int) -> float:
    """Calculate Click-Through Rate (CTR) for a campaign.

    CTR measures the effectiveness of an ad by showing what percentage
    of impressions resulted in clicks. Higher CTR indicates more
    engaging ad content.

    Formula: (clicks / impressions) × 100

    Args:
        clicks: Number of link clicks on the ad.
        impressions: Number of times the ad was displayed.

    Returns:
        CTR as a percentage (e.g., 2.5 for 2.5%).
        Returns 0.0 if impressions is zero to prevent division errors.

    Example:
        >>> calculate_ctr(50, 2500)
        2.0
        >>> calculate_ctr(0, 1000)
        0.0
        >>> calculate_ctr(100, 0)
        0.0
    """
    if impressions <= 0:
        logger.debug("Zero or negative impressions, returning CTR of 0.0")
        return 0.0

    ctr = (clicks / impressions) * 100
    return round(ctr, 2)


def calculate_cpc(spend: float, clicks: int) -> float:
    """Calculate Cost Per Click (CPC) for a campaign.

    CPC measures the cost efficiency of clicks, showing how much
    each click costs on average. Lower CPC indicates more efficient
    ad spend.

    Formula: spend / clicks

    Args:
        spend: Amount spent on the campaign in ZAR.
        clicks: Number of link clicks on the ad.

    Returns:
        CPC in ZAR (e.g., 15.50 for R15.50 per click).
        Returns 0.0 if clicks is zero to prevent division errors.

    Example:
        >>> calculate_cpc(1000.00, 50)
        20.0
        >>> calculate_cpc(500.00, 0)
        0.0
        >>> calculate_cpc(0.0, 100)
        0.0
    """
    if clicks <= 0:
        logger.debug("Zero or negative clicks, returning CPC of 0.0")
        return 0.0

    cpc = spend / clicks
    return round(cpc, 2)


def add_metrics_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Add CTR and CPC columns to a campaign DataFrame.

    Processes each campaign row to calculate performance metrics,
    applying zero-division protection automatically. This transforms
    raw campaign data into actionable insights for client reports.

    Args:
        df: DataFrame with columns: amount_spent, link_clicks, impressions.
            Typically output from csv_reader.read_meta_csv().

    Returns:
        DataFrame with two additional columns:
        - ctr: Click-Through Rate as percentage
        - cpc: Cost Per Click in ZAR

    Raises:
        KeyError: If required columns are missing from the DataFrame.

    Example:
        >>> df = pd.DataFrame({
        ...     'campaign_name': ['Summer Sale'],
        ...     'amount_spent': [1000.0],
        ...     'link_clicks': [50],
        ...     'impressions': [2500]
        ... })
        >>> result = add_metrics_to_dataframe(df)
        >>> result['ctr'].iloc[0]
        2.0
        >>> result['cpc'].iloc[0]
        20.0
    """
    required_columns = ["amount_spent", "link_clicks", "impressions"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        logger.error("Missing required columns for metrics: %s", missing)
        raise KeyError(f"Missing required columns: {', '.join(missing)}")

    logger.info("Calculating CTR and CPC for %d campaigns...", len(df))

    # Create a copy to avoid modifying the original DataFrame
    df_with_metrics = df.copy()

    # Calculate CTR: (clicks / impressions) * 100
    df_with_metrics["ctr"] = df_with_metrics.apply(
        lambda row: calculate_ctr(row["link_clicks"], row["impressions"]),
        axis=1
    )

    # Calculate CPC: spend / clicks
    df_with_metrics["cpc"] = df_with_metrics.apply(
        lambda row: calculate_cpc(row["amount_spent"], row["link_clicks"]),
        axis=1
    )

    logger.info("Metrics calculated successfully. CTR range: %.2f%% - %.2f%%, CPC range: R%.2f - R%.2f",
                df_with_metrics["ctr"].min(),
                df_with_metrics["ctr"].max(),
                df_with_metrics["cpc"].min(),
                df_with_metrics["cpc"].max())

    return df_with_metrics
