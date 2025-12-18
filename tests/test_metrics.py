"""Unit tests for the Metrics Calculator module.

Tests cover CTR and CPC calculations including zero-division
protection and DataFrame integration.
"""

import pytest
import pandas as pd

from src.metrics import calculate_ctr, calculate_cpc, add_metrics_to_dataframe


class TestCalculateCTR:
    """Test suite for calculate_ctr function."""

    def test_ctr_with_valid_values(self) -> None:
        """Test CTR calculation with typical campaign values."""
        # 50 clicks / 2500 impressions = 2.0%
        assert calculate_ctr(50, 2500) == 2.0

    def test_ctr_with_zero_impressions(self) -> None:
        """Test CTR returns 0.0 when impressions is zero (division protection)."""
        assert calculate_ctr(100, 0) == 0.0

    def test_ctr_with_zero_clicks(self) -> None:
        """Test CTR returns 0.0 when clicks is zero."""
        assert calculate_ctr(0, 1000) == 0.0

    def test_ctr_with_negative_impressions(self) -> None:
        """Test CTR handles negative impressions gracefully."""
        assert calculate_ctr(50, -100) == 0.0

    def test_ctr_high_performance_campaign(self) -> None:
        """Test CTR calculation for high-performing campaign."""
        # 500 clicks / 5000 impressions = 10.0%
        assert calculate_ctr(500, 5000) == 10.0

    def test_ctr_rounds_to_two_decimals(self) -> None:
        """Test CTR is rounded to 2 decimal places."""
        # 33 clicks / 1000 impressions = 3.3%
        assert calculate_ctr(33, 1000) == 3.3


class TestCalculateCPC:
    """Test suite for calculate_cpc function."""

    def test_cpc_with_valid_values(self) -> None:
        """Test CPC calculation with typical campaign values."""
        # R1000 / 50 clicks = R20.00
        assert calculate_cpc(1000.0, 50) == 20.0

    def test_cpc_with_zero_clicks(self) -> None:
        """Test CPC returns 0.0 when clicks is zero (division protection)."""
        assert calculate_cpc(500.0, 0) == 0.0

    def test_cpc_with_zero_spend(self) -> None:
        """Test CPC returns 0.0 when spend is zero."""
        assert calculate_cpc(0.0, 100) == 0.0

    def test_cpc_with_negative_clicks(self) -> None:
        """Test CPC handles negative clicks gracefully."""
        assert calculate_cpc(500.0, -10) == 0.0

    def test_cpc_efficient_campaign(self) -> None:
        """Test CPC calculation for cost-efficient campaign."""
        # R500 / 100 clicks = R5.00
        assert calculate_cpc(500.0, 100) == 5.0

    def test_cpc_rounds_to_two_decimals(self) -> None:
        """Test CPC is rounded to 2 decimal places."""
        # R100 / 3 clicks = R33.33
        assert calculate_cpc(100.0, 3) == 33.33


class TestAddMetricsToDataFrame:
    """Test suite for add_metrics_to_dataframe function."""

    def test_adds_ctr_and_cpc_columns(self) -> None:
        """Test that CTR and CPC columns are added to DataFrame."""
        df = pd.DataFrame({
            "campaign_name": ["Test Campaign"],
            "amount_spent": [1000.0],
            "link_clicks": [50],
            "impressions": [2500]
        })

        result = add_metrics_to_dataframe(df)

        assert "ctr" in result.columns
        assert "cpc" in result.columns
        assert result.iloc[0]["ctr"] == 2.0
        assert result.iloc[0]["cpc"] == 20.0

    def test_preserves_original_columns(self) -> None:
        """Test that original columns are preserved."""
        df = pd.DataFrame({
            "campaign_name": ["Summer Sale"],
            "amount_spent": [1500.0],
            "link_clicks": [75],
            "impressions": [5000]
        })

        result = add_metrics_to_dataframe(df)

        assert result.iloc[0]["campaign_name"] == "Summer Sale"
        assert result.iloc[0]["amount_spent"] == 1500.0
        assert result.iloc[0]["link_clicks"] == 75
        assert result.iloc[0]["impressions"] == 5000

    def test_handles_zero_division_in_dataframe(self) -> None:
        """Test zero-division protection works in DataFrame context."""
        df = pd.DataFrame({
            "campaign_name": ["Zero Impressions", "Zero Clicks"],
            "amount_spent": [500.0, 1000.0],
            "link_clicks": [50, 0],
            "impressions": [0, 5000]
        })

        result = add_metrics_to_dataframe(df)

        # Zero impressions -> CTR = 0
        assert result.iloc[0]["ctr"] == 0.0
        # Zero clicks -> CPC = 0
        assert result.iloc[1]["cpc"] == 0.0

    def test_raises_error_for_missing_columns(self) -> None:
        """Test that missing required columns raise KeyError."""
        df = pd.DataFrame({
            "campaign_name": ["Test"],
            "amount_spent": [100.0]
            # Missing link_clicks and impressions
        })

        with pytest.raises(KeyError) as exc_info:
            add_metrics_to_dataframe(df)

        assert "link_clicks" in str(exc_info.value) or "impressions" in str(exc_info.value)

    def test_does_not_modify_original_dataframe(self) -> None:
        """Test that original DataFrame is not modified."""
        df = pd.DataFrame({
            "campaign_name": ["Test"],
            "amount_spent": [1000.0],
            "link_clicks": [50],
            "impressions": [2500]
        })

        original_columns = list(df.columns)
        add_metrics_to_dataframe(df)

        assert list(df.columns) == original_columns
        assert "ctr" not in df.columns
        assert "cpc" not in df.columns

    def test_multiple_campaigns(self) -> None:
        """Test metrics calculation for multiple campaigns."""
        df = pd.DataFrame({
            "campaign_name": ["Campaign A", "Campaign B", "Campaign C"],
            "amount_spent": [1000.0, 2000.0, 500.0],
            "link_clicks": [50, 100, 25],
            "impressions": [2500, 8000, 1000]
        })

        result = add_metrics_to_dataframe(df)

        assert len(result) == 3
        # Campaign A: CTR = 2.0%, CPC = R20.00
        assert result.iloc[0]["ctr"] == 2.0
        assert result.iloc[0]["cpc"] == 20.0
        # Campaign B: CTR = 1.25%, CPC = R20.00
        assert result.iloc[1]["ctr"] == 1.25
        assert result.iloc[1]["cpc"] == 20.0
        # Campaign C: CTR = 2.5%, CPC = R20.00
        assert result.iloc[2]["ctr"] == 2.5
        assert result.iloc[2]["cpc"] == 20.0
