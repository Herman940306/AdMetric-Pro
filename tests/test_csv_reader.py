"""Unit tests for the CSV Reader module.

Tests cover file validation, column mapping, and error handling
for Meta Ads CSV ingestion.
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch

from src.csv_reader import read_meta_csv, REQUIRED_COLUMNS, COLUMN_MAPPING


class TestReadMetaCSV:
    """Test suite for read_meta_csv function."""

    def test_valid_csv_loads_successfully(self, tmp_path: Path) -> None:
        """Test that a valid Meta Ads CSV loads and maps columns correctly.
        
        Args:
            tmp_path: Pytest fixture providing temporary directory.
        """
        # Arrange: Create mock Meta Ads CSV
        csv_file = tmp_path / "meta_ads.csv"
        csv_content = (
            "Campaign Name,Amount Spent (ZAR),Link Clicks,Impressions\n"
            "Summer Sale,1500.50,75,5000\n"
            "Winter Promo,2300.00,120,8500\n"
        )
        csv_file.write_text(csv_content)

        # Act
        df = read_meta_csv(str(csv_file))

        # Assert
        assert len(df) == 2
        assert list(df.columns) == ["campaign_name", "amount_spent", "link_clicks", "impressions"]
        assert df.iloc[0]["campaign_name"] == "Summer Sale"
        assert df.iloc[0]["amount_spent"] == 1500.50
        assert df.iloc[0]["link_clicks"] == 75
        assert df.iloc[0]["impressions"] == 5000

    def test_file_not_found_raises_error(self) -> None:
        """Test that missing file raises FileNotFoundError with descriptive message."""
        with pytest.raises(FileNotFoundError) as exc_info:
            read_meta_csv("nonexistent/path/meta_ads.csv")
        
        assert "not found" in str(exc_info.value).lower()

    def test_missing_column_raises_value_error(self, tmp_path: Path) -> None:
        """Test that missing required columns raise ValueError.
        
        Args:
            tmp_path: Pytest fixture providing temporary directory.
        """
        # Arrange: CSV missing 'Link Clicks' column
        csv_file = tmp_path / "incomplete.csv"
        csv_content = (
            "Campaign Name,Amount Spent (ZAR),Impressions\n"
            "Test Campaign,500.00,1000\n"
        )
        csv_file.write_text(csv_content)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            read_meta_csv(str(csv_file))
        
        assert "Link Clicks" in str(exc_info.value)

    def test_invalid_file_extension_raises_error(self, tmp_path: Path) -> None:
        """Test that non-CSV files raise ValueError.
        
        Args:
            tmp_path: Pytest fixture providing temporary directory.
        """
        # Arrange: Create a .txt file
        txt_file = tmp_path / "data.txt"
        txt_file.write_text("not a csv")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            read_meta_csv(str(txt_file))
        
        assert "csv" in str(exc_info.value).lower()

    def test_empty_csv_raises_error(self, tmp_path: Path) -> None:
        """Test that empty CSV files raise ValueError.
        
        Args:
            tmp_path: Pytest fixture providing temporary directory.
        """
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        with pytest.raises(ValueError) as exc_info:
            read_meta_csv(str(csv_file))
        
        assert "empty" in str(exc_info.value).lower()

    def test_numeric_coercion_handles_invalid_values(self, tmp_path: Path) -> None:
        """Test that non-numeric values are coerced to defaults.
        
        Args:
            tmp_path: Pytest fixture providing temporary directory.
        """
        csv_file = tmp_path / "bad_numbers.csv"
        csv_content = (
            "Campaign Name,Amount Spent (ZAR),Link Clicks,Impressions\n"
            "Test Campaign,invalid,N/A,abc\n"
        )
        csv_file.write_text(csv_content)

        df = read_meta_csv(str(csv_file))

        # Invalid values should be coerced to 0
        assert df.iloc[0]["amount_spent"] == 0.0
        assert df.iloc[0]["link_clicks"] == 0
        assert df.iloc[0]["impressions"] == 0

    def test_column_mapping_matches_design_spec(self) -> None:
        """Test that column mapping matches design document specification."""
        expected_mapping = {
            "Campaign Name": "campaign_name",
            "Amount Spent (ZAR)": "amount_spent",
            "Link Clicks": "link_clicks",
            "Impressions": "impressions",
        }
        assert COLUMN_MAPPING == expected_mapping

    def test_required_columns_complete(self) -> None:
        """Test that all required columns are defined."""
        expected_columns = [
            "Campaign Name",
            "Amount Spent (ZAR)",
            "Link Clicks",
            "Impressions",
        ]
        assert REQUIRED_COLUMNS == expected_columns


class TestCTRAndCPCCalculationPrep:
    """Tests verifying data is ready for metric calculations."""

    def test_dataframe_ready_for_ctr_calculation(self, tmp_path: Path) -> None:
        """Test that loaded data supports CTR calculation: (clicks / impressions) * 100.
        
        Args:
            tmp_path: Pytest fixture providing temporary directory.
        """
        csv_file = tmp_path / "meta_ads.csv"
        csv_content = (
            "Campaign Name,Amount Spent (ZAR),Link Clicks,Impressions\n"
            "Test Campaign,1000.00,50,2500\n"
        )
        csv_file.write_text(csv_content)

        df = read_meta_csv(str(csv_file))
        
        # Verify CTR can be calculated
        clicks = df.iloc[0]["link_clicks"]
        impressions = df.iloc[0]["impressions"]
        expected_ctr = (clicks / impressions) * 100  # 2.0%
        
        assert expected_ctr == 2.0

    def test_dataframe_ready_for_cpc_calculation(self, tmp_path: Path) -> None:
        """Test that loaded data supports CPC calculation: spend / clicks.
        
        Args:
            tmp_path: Pytest fixture providing temporary directory.
        """
        csv_file = tmp_path / "meta_ads.csv"
        csv_content = (
            "Campaign Name,Amount Spent (ZAR),Link Clicks,Impressions\n"
            "Test Campaign,1000.00,50,2500\n"
        )
        csv_file.write_text(csv_content)

        df = read_meta_csv(str(csv_file))
        
        # Verify CPC can be calculated
        spend = df.iloc[0]["amount_spent"]
        clicks = df.iloc[0]["link_clicks"]
        expected_cpc = spend / clicks  # R20.00
        
        assert expected_cpc == 20.0
