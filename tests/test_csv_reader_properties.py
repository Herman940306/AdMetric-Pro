"""Property-based tests for the CSV Reader module.

This module contains property-based tests that verify universal correctness
properties for the CSV Reader functionality. Using the Hypothesis library,
these tests automatically generate diverse test cases to ensure the CSV
ingestion and column mapping behaves correctly across all valid inputs.

Business Value:
    Ensures reliable data ingestion from Meta Ads exports, preventing
    data corruption that could lead to incorrect client reports.

Example:
    Run these tests with pytest::

        pytest tests/test_csv_reader_properties.py -v
"""

import logging
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pytest import TempPathFactory

from src.csv_reader import COLUMN_MAPPING, REQUIRED_COLUMNS, read_meta_csv

# Configure module logger
logger = logging.getLogger(__name__)


def create_campaign_name_strategy() -> st.SearchStrategy[str]:
    """Create a Hypothesis strategy for generating valid campaign names.

    Generates realistic campaign names using alphanumeric characters,
    spaces, hyphens, and underscores. Filters out empty or whitespace-only
    strings and strings starting with spaces to avoid CSV parsing issues.

    Returns:
        A Hypothesis SearchStrategy that generates valid campaign name strings.

    Example:
        >>> strategy = create_campaign_name_strategy()
        >>> # Use with @given decorator in property tests
    """
    return st.text(
        alphabet=st.characters(
            whitelist_categories=("L", "N"),
            whitelist_characters=" -_"
        ),
        min_size=1,
        max_size=50
    ).filter(lambda x: x.strip() != "" and not x.startswith(" "))


def create_amount_spent_strategy() -> st.SearchStrategy[float]:
    """Create a Hypothesis strategy for generating valid spend amounts.

    Generates float values representing ZAR currency amounts within
    realistic bounds for advertising campaigns.

    Returns:
        A Hypothesis SearchStrategy that generates valid spend amounts
        between 0.0 and 1,000,000.0 ZAR.
    """
    return st.floats(
        min_value=0.0,
        max_value=1_000_000.0,
        allow_nan=False,
        allow_infinity=False
    )


def create_clicks_strategy() -> st.SearchStrategy[int]:
    """Create a Hypothesis strategy for generating valid click counts.

    Returns:
        A Hypothesis SearchStrategy that generates integer click counts
        between 0 and 1,000,000.
    """
    return st.integers(min_value=0, max_value=1_000_000)


def create_impressions_strategy() -> st.SearchStrategy[int]:
    """Create a Hypothesis strategy for generating valid impression counts.

    Returns:
        A Hypothesis SearchStrategy that generates integer impression counts
        between 0 and 10,000,000.
    """
    return st.integers(min_value=0, max_value=10_000_000)


# Initialize strategies for use in property tests
campaign_name_strategy: st.SearchStrategy[str] = create_campaign_name_strategy()
amount_spent_strategy: st.SearchStrategy[float] = create_amount_spent_strategy()
clicks_strategy: st.SearchStrategy[int] = create_clicks_strategy()
impressions_strategy: st.SearchStrategy[int] = create_impressions_strategy()


class TestCSVDataPreservationProperty:
    """Property-based tests for CSV data preservation.

    This test class verifies that the CSV reader correctly preserves all
    campaign data during the ingestion process. Using property-based testing,
    it ensures data integrity across a wide range of automatically generated
    test cases.

    Feature:
        admetric-pro, Property 1: CSV Data Preservation

    Validates:
        Requirements 1.1, 2.1

    Business Value:
        Guarantees that client campaign data is never corrupted or lost
        during the report generation process.
    """

    @given(
        campaign_name=campaign_name_strategy,
        amount_spent=amount_spent_strategy,
        link_clicks=clicks_strategy,
        impressions=impressions_strategy
    )
    @settings(max_examples=100)
    def test_csv_data_preservation_single_row(
        self,
        tmp_path_factory: TempPathFactory,
        campaign_name: str,
        amount_spent: float,
        link_clicks: int,
        impressions: int
    ) -> None:
        """Verify that reading a CSV preserves all campaign values exactly.

        For any valid Meta Ads CSV file containing campaign data, reading
        the file and extracting columns SHALL produce a DataFrame where
        each row's values match the original CSV values exactly.

        Feature:
            admetric-pro, Property 1: CSV Data Preservation

        Validates:
            Requirements 1.1, 2.1

        Args:
            tmp_path_factory: Pytest fixture for creating temporary directories.
            campaign_name: Hypothesis-generated campaign name string.
            amount_spent: Hypothesis-generated spend amount in ZAR.
            link_clicks: Hypothesis-generated click count.
            impressions: Hypothesis-generated impression count.

        Raises:
            AssertionError: If any data value is not preserved correctly.
        """
        # Arrange: Create CSV with generated data
        tmp_path = tmp_path_factory.mktemp("data")
        csv_file = tmp_path / "meta_ads.csv"

        # Round amount_spent to 2 decimal places (currency precision)
        amount_spent_rounded = round(amount_spent, 2)

        csv_content = (
            f"Campaign Name,Amount Spent (ZAR),Link Clicks,Impressions\n"
            f"{campaign_name},{amount_spent_rounded},{link_clicks},{impressions}\n"
        )
        csv_file.write_text(csv_content, encoding="utf-8")

        # Act: Read the CSV
        df = read_meta_csv(str(csv_file))

        # Assert: Data is preserved
        assert len(df) == 1, "DataFrame should contain exactly one row"
        assert df.iloc[0]["campaign_name"] == campaign_name
        assert abs(df.iloc[0]["amount_spent"] - amount_spent_rounded) < 0.01
        assert df.iloc[0]["link_clicks"] == link_clicks
        assert df.iloc[0]["impressions"] == impressions

    @given(
        num_campaigns=st.integers(min_value=1, max_value=20),
        base_spend=amount_spent_strategy,
        base_clicks=clicks_strategy,
        base_impressions=impressions_strategy
    )
    @settings(max_examples=100)
    def test_csv_row_count_preservation(
        self,
        tmp_path_factory: TempPathFactory,
        num_campaigns: int,
        base_spend: float,
        base_clicks: int,
        base_impressions: int
    ) -> None:
        """Verify that the row count is preserved when reading a CSV file.

        For any valid CSV with N campaign rows, the resulting DataFrame
        SHALL contain exactly N rows, ensuring no data is lost or duplicated.

        Feature:
            admetric-pro, Property 1: CSV Data Preservation

        Validates:
            Requirements 1.1, 2.1

        Args:
            tmp_path_factory: Pytest fixture for creating temporary directories.
            num_campaigns: Hypothesis-generated number of campaigns (1-20).
            base_spend: Hypothesis-generated base spend amount for campaigns.
            base_clicks: Hypothesis-generated base click count for campaigns.
            base_impressions: Hypothesis-generated base impression count.

        Raises:
            AssertionError: If the row count does not match the input.
        """
        # Arrange: Create CSV with multiple rows
        tmp_path = tmp_path_factory.mktemp("data")
        csv_file = tmp_path / "meta_ads.csv"

        lines: list[str] = ["Campaign Name,Amount Spent (ZAR),Link Clicks,Impressions"]
        for i in range(num_campaigns):
            spend = round(base_spend + i * 100, 2)
            clicks = base_clicks + i * 10
            impressions = base_impressions + i * 100
            lines.append(f"Campaign {i+1},{spend},{clicks},{impressions}")

        csv_file.write_text("\n".join(lines), encoding="utf-8")

        # Act
        df = read_meta_csv(str(csv_file))

        # Assert: Row count preserved
        assert len(df) == num_campaigns, f"Expected {num_campaigns} rows, got {len(df)}"

    @given(
        amount_spent=amount_spent_strategy,
        link_clicks=clicks_strategy,
        impressions=impressions_strategy
    )
    @settings(max_examples=100)
    def test_column_mapping_consistency(
        self,
        tmp_path_factory: TempPathFactory,
        amount_spent: float,
        link_clicks: int,
        impressions: int
    ) -> None:
        """Verify that column mapping is consistent for all valid inputs.

        For any valid CSV, the output DataFrame SHALL always have exactly
        the mapped column names: campaign_name, amount_spent, link_clicks,
        impressions. This ensures downstream metric calculations receive
        consistently named columns.

        Feature:
            admetric-pro, Property 1: CSV Data Preservation

        Validates:
            Requirements 2.1

        Args:
            tmp_path_factory: Pytest fixture for creating temporary directories.
            amount_spent: Hypothesis-generated spend amount in ZAR.
            link_clicks: Hypothesis-generated click count.
            impressions: Hypothesis-generated impression count.

        Raises:
            AssertionError: If column names do not match expected mapping.
        """
        # Arrange
        tmp_path = tmp_path_factory.mktemp("data")
        csv_file = tmp_path / "meta_ads.csv"

        csv_content = (
            f"Campaign Name,Amount Spent (ZAR),Link Clicks,Impressions\n"
            f"Test Campaign,{round(amount_spent, 2)},{link_clicks},{impressions}\n"
        )
        csv_file.write_text(csv_content, encoding="utf-8")

        # Act
        df = read_meta_csv(str(csv_file))

        # Assert: Columns are always mapped correctly
        expected_columns: list[str] = [
            "campaign_name",
            "amount_spent",
            "link_clicks",
            "impressions"
        ]
        assert list(df.columns) == expected_columns
