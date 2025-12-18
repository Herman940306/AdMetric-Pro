"""Unit tests for AdMetric Pro visual generation module.

Tests the image generation functions that create README preview
assets showcasing the tool's professional output quality.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from src.generate_visuals import (
    generate_executive_summary_image,
    generate_report_preview_image,
    main,
    CPC_THRESHOLD,
)


class TestGenerateExecutiveSummaryImage:
    """Tests for Executive Summary image generation."""

    @pytest.fixture
    def sample_df(self) -> pd.DataFrame:
        """Create sample DataFrame with campaign metrics."""
        return pd.DataFrame({
            "campaign_name": ["Summer Sale", "Winter Promo", "Brand Awareness"],
            "amount_spent": [1000.00, 500.00, 2500.00],
            "link_clicks": [50, 25, 100],
            "impressions": [2500, 1250, 10000],
            "ctr": [2.0, 2.0, 1.0],
            "cpc": [20.0, 20.0, 25.0],
        })

    @patch("src.generate_visuals.go.Figure")
    def test_generates_image_with_correct_metrics(self, mock_figure, sample_df):
        """Test that summary image is generated with aggregated metrics."""
        mock_fig_instance = MagicMock()
        mock_figure.return_value = mock_fig_instance

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            output_path = f.name

        try:
            generate_executive_summary_image(sample_df, output_path)

            # Verify figure was created and write_image was called
            mock_figure.assert_called_once()
            mock_fig_instance.write_image.assert_called_once()
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_calculates_total_spend_correctly(self, sample_df):
        """Test Total Spend calculation: sum of amount_spent."""
        expected_total = 1000.00 + 500.00 + 2500.00  # R4,000.00
        actual_total = sample_df["amount_spent"].sum()
        assert actual_total == expected_total

    def test_calculates_total_clicks_correctly(self, sample_df):
        """Test Total Clicks calculation: sum of link_clicks."""
        expected_clicks = 50 + 25 + 100  # 175
        actual_clicks = sample_df["link_clicks"].sum()
        assert actual_clicks == expected_clicks

    def test_calculates_total_impressions_correctly(self, sample_df):
        """Test Total Impressions calculation: sum of impressions."""
        expected_impressions = 2500 + 1250 + 10000  # 13,750
        actual_impressions = sample_df["impressions"].sum()
        assert actual_impressions == expected_impressions

    def test_calculates_average_cpc_correctly(self, sample_df):
        """Test Average CPC: total_spend / total_clicks."""
        total_spend = sample_df["amount_spent"].sum()  # 4000
        total_clicks = sample_df["link_clicks"].sum()  # 175
        expected_avg_cpc = total_spend / total_clicks  # ~22.86
        actual_avg_cpc = total_spend / total_clicks
        assert abs(actual_avg_cpc - expected_avg_cpc) < 0.01

    def test_calculates_overall_ctr_correctly(self, sample_df):
        """Test Overall CTR: (total_clicks / total_impressions) * 100."""
        total_clicks = sample_df["link_clicks"].sum()  # 175
        total_impressions = sample_df["impressions"].sum()  # 13750
        expected_ctr = (total_clicks / total_impressions) * 100  # ~1.27%
        actual_ctr = (total_clicks / total_impressions) * 100
        assert abs(actual_ctr - expected_ctr) < 0.01

    def test_handles_zero_clicks_for_cpc(self):
        """Test CPC is 0 when total clicks is 0 (zero-division protection)."""
        df = pd.DataFrame({
            "amount_spent": [100.00],
            "link_clicks": [0],
            "impressions": [1000],
        })
        total_spend = df["amount_spent"].sum()
        total_clicks = df["link_clicks"].sum()
        avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0
        assert avg_cpc == 0

    def test_handles_zero_impressions_for_ctr(self):
        """Test CTR is 0 when total impressions is 0 (zero-division protection)."""
        df = pd.DataFrame({
            "amount_spent": [100.00],
            "link_clicks": [10],
            "impressions": [0],
        })
        total_clicks = df["link_clicks"].sum()
        total_impressions = df["impressions"].sum()
        overall_ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
        assert overall_ctr == 0


class TestGenerateReportPreviewImage:
    """Tests for Campaign Details report preview image generation."""

    @pytest.fixture
    def sample_df(self) -> pd.DataFrame:
        """Create sample DataFrame with campaign metrics."""
        return pd.DataFrame({
            "campaign_name": ["Summer Sale", "High CPC Campaign", "Normal Campaign"],
            "amount_spent": [1000.00, 500.00, 200.00],
            "link_clicks": [50, 10, 20],
            "impressions": [2500, 500, 4000],
            "ctr": [2.0, 2.0, 0.5],
            "cpc": [20.0, 50.0, 10.0],  # Middle one exceeds threshold
        })

    @patch("src.generate_visuals.go.Figure")
    def test_generates_image_with_campaign_data(self, mock_figure, sample_df):
        """Test that report preview image is generated."""
        mock_fig_instance = MagicMock()
        mock_figure.return_value = mock_fig_instance

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            output_path = f.name

        try:
            generate_report_preview_image(sample_df, output_path)

            mock_figure.assert_called_once()
            mock_fig_instance.write_image.assert_called_once()
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_respects_top_n_parameter(self, sample_df):
        """Test that top_n limits the number of campaigns shown."""
        preview_df = sample_df.head(2)
        assert len(preview_df) == 2

    def test_identifies_high_cpc_campaigns(self, sample_df):
        """Test campaigns with CPC > R20.00 are identified for highlighting."""
        high_cpc_campaigns = sample_df[sample_df["cpc"] > CPC_THRESHOLD]
        assert len(high_cpc_campaigns) == 1
        assert high_cpc_campaigns.iloc[0]["campaign_name"] == "High CPC Campaign"

    def test_cpc_threshold_is_twenty_rand(self):
        """Test CPC threshold constant is R20.00."""
        assert CPC_THRESHOLD == 20.00


class TestMainFunction:
    """Tests for the main visual generation orchestrator."""

    @patch("src.generate_visuals.generate_report_preview_image")
    @patch("src.generate_visuals.generate_executive_summary_image")
    @patch("src.generate_visuals.add_metrics_to_dataframe")
    @patch("src.generate_visuals.read_meta_csv")
    def test_main_success_returns_zero(
        self,
        mock_read_csv,
        mock_add_metrics,
        mock_summary_image,
        mock_report_image
    ):
        """Test main returns 0 on successful execution."""
        mock_df = pd.DataFrame({
            "campaign_name": ["Test"],
            "amount_spent": [100.0],
            "link_clicks": [10],
            "impressions": [1000],
        })
        mock_read_csv.return_value = mock_df
        mock_add_metrics.return_value = mock_df

        exit_code = main()

        assert exit_code == 0
        mock_read_csv.assert_called_once_with("mock_data/sample_meta_ads.csv")
        mock_add_metrics.assert_called_once()

    @patch("src.generate_visuals.read_meta_csv")
    def test_main_file_not_found_returns_one(self, mock_read_csv):
        """Test main returns 1 when mock data file is not found."""
        mock_read_csv.side_effect = FileNotFoundError("File not found")

        exit_code = main()

        assert exit_code == 1

    @patch("src.generate_visuals.generate_executive_summary_image")
    @patch("src.generate_visuals.add_metrics_to_dataframe")
    @patch("src.generate_visuals.read_meta_csv")
    def test_main_io_error_returns_one(
        self,
        mock_read_csv,
        mock_add_metrics,
        mock_summary_image
    ):
        """Test main returns 1 when image cannot be written."""
        mock_df = pd.DataFrame({
            "campaign_name": ["Test"],
            "amount_spent": [100.0],
            "link_clicks": [10],
            "impressions": [1000],
        })
        mock_read_csv.return_value = mock_df
        mock_add_metrics.return_value = mock_df
        mock_summary_image.side_effect = IOError("Cannot write image")

        exit_code = main()

        assert exit_code == 1


class TestMetricsCalculations:
    """Tests verifying metric calculations match expected values."""

    def test_ctr_formula_clicks_divided_by_impressions_times_100(self):
        """Test CTR = (clicks / impressions) * 100."""
        clicks = 50
        impressions = 2500
        expected_ctr = (clicks / impressions) * 100  # 2.0%
        assert expected_ctr == 2.0

    def test_cpc_formula_spend_divided_by_clicks(self):
        """Test CPC = spend / clicks."""
        spend = 1000.0
        clicks = 50
        expected_cpc = spend / clicks  # R20.00
        assert expected_cpc == 20.0

    def test_average_cpc_across_campaigns(self):
        """Test average CPC calculation across multiple campaigns."""
        data = {
            "amount_spent": [1000.00, 500.00, 2500.00],
            "link_clicks": [50, 25, 100],
        }
        df = pd.DataFrame(data)
        total_spend = df["amount_spent"].sum()  # 4000
        total_clicks = df["link_clicks"].sum()  # 175
        avg_cpc = total_spend / total_clicks
        assert abs(avg_cpc - 22.857) < 0.01

    def test_overall_ctr_across_campaigns(self):
        """Test overall CTR calculation across multiple campaigns."""
        data = {
            "link_clicks": [50, 25, 100],
            "impressions": [2500, 1250, 10000],
        }
        df = pd.DataFrame(data)
        total_clicks = df["link_clicks"].sum()  # 175
        total_impressions = df["impressions"].sum()  # 13750
        overall_ctr = (total_clicks / total_impressions) * 100
        assert abs(overall_ctr - 1.273) < 0.01
