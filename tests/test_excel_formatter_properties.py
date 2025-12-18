"""Property-based tests for the Excel Formatter module.

These tests verify universal correctness properties for Excel report
generation using the Hypothesis library.
"""

import pytest
import pandas as pd
import re
from pathlib import Path
from hypothesis import given, strategies as st, settings
from openpyxl import load_workbook

from src.excel_formatter import (
    generate_timestamped_filename,
    generate_report,
    CPC_THRESHOLD,
)


class TestTimestampedFilenameProperty:
    """Property-based tests for timestamped filename generation.

    **Feature: admetric-pro, Property 9: Timestamped Filename Format**
    **Validates: Requirements 8.1**
    """

    @settings(max_examples=100)
    @given(st.integers(min_value=1, max_value=100))
    def test_filename_matches_pattern(self, _: int) -> None:
        """Property: Filename always matches expected pattern.

        **Feature: admetric-pro, Property 9: Timestamped Filename Format**
        **Validates: Requirements 8.1**

        For any generated report, the output filename SHALL match the
        pattern AdMetric_Pro_Report_YYYY-MM-DD_HHMM.xlsx.
        """
        filename = generate_timestamped_filename()

        # Pattern: AdMetric_Pro_Report_YYYY-MM-DD_HHMM.xlsx
        pattern = r"^AdMetric_Pro_Report_\d{4}-\d{2}-\d{2}_\d{4}\.xlsx$"
        assert re.match(pattern, filename), f"Filename '{filename}' doesn't match expected pattern"


class TestHeaderFormattingProperty:
    """Property-based tests for header formatting.

    **Feature: admetric-pro, Property 4: Header Formatting Consistency**
    **Validates: Requirements 4.1, 4.2**
    """

    @given(
        num_campaigns=st.integers(min_value=1, max_value=10),
        base_spend=st.floats(min_value=100.0, max_value=10000.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=50)
    def test_all_headers_formatted(self, tmp_path_factory, num_campaigns: int, base_spend: float) -> None:
        """Property: All header cells have bold font and dark blue background.

        **Feature: admetric-pro, Property 4: Header Formatting Consistency**
        **Validates: Requirements 4.1, 4.2**

        For any generated Excel report, all header cells in the first row
        SHALL have bold font and dark blue background color applied.
        """
        tmp_path = tmp_path_factory.mktemp("reports")

        # Generate test data
        df = pd.DataFrame({
            "campaign_name": [f"Campaign {i}" for i in range(num_campaigns)],
            "amount_spent": [base_spend + i * 100 for i in range(num_campaigns)],
            "link_clicks": [50 + i * 10 for i in range(num_campaigns)],
            "impressions": [2500 + i * 500 for i in range(num_campaigns)],
            "ctr": [2.0 for _ in range(num_campaigns)],
            "cpc": [20.0 for _ in range(num_campaigns)]
        })

        report_path = generate_report(df, str(tmp_path))
        wb = load_workbook(report_path)
        ws = wb["Campaign Details"]

        # Check all header cells
        for cell in ws[1]:
            if cell.value:
                assert cell.font.bold is True, f"Header '{cell.value}' is not bold"
                assert cell.fill.start_color.rgb == "001F4E79", f"Header '{cell.value}' doesn't have dark blue fill"


class TestCPCThresholdHighlightingProperty:
    """Property-based tests for CPC threshold highlighting.

    **Feature: admetric-pro, Property 6: CPC Threshold Highlighting**
    **Validates: Requirements 5.1, 5.2**
    """

    @given(
        low_cpc=st.floats(min_value=0.0, max_value=19.99, allow_nan=False, allow_infinity=False),
        high_cpc=st.floats(min_value=20.01, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=50)
    def test_cpc_threshold_highlighting(self, tmp_path_factory, low_cpc: float, high_cpc: float) -> None:
        """Property: Rows with CPC > R20.00 are highlighted, others are not.

        **Feature: admetric-pro, Property 6: CPC Threshold Highlighting**
        **Validates: Requirements 5.1, 5.2**

        For any campaign row in the generated Excel report, if CPC exceeds
        R20.00 then the row SHALL have red background highlighting,
        otherwise the row SHALL have no red highlighting.
        """
        tmp_path = tmp_path_factory.mktemp("reports")

        df = pd.DataFrame({
            "campaign_name": ["Low CPC Campaign", "High CPC Campaign"],
            "amount_spent": [low_cpc * 10, high_cpc * 10],
            "link_clicks": [10, 10],
            "impressions": [1000, 1000],
            "ctr": [1.0, 1.0],
            "cpc": [low_cpc, high_cpc]
        })

        report_path = generate_report(df, str(tmp_path))
        wb = load_workbook(report_path)
        ws = wb["Campaign Details"]

        # Row 2 (Low CPC) should NOT be highlighted
        low_cpc_fill = ws.cell(row=2, column=1).fill.start_color.rgb
        assert low_cpc_fill != "00FFC7CE", f"Low CPC row incorrectly highlighted (CPC={low_cpc})"

        # Row 3 (High CPC) SHOULD be highlighted
        high_cpc_fill = ws.cell(row=3, column=1).fill.start_color.rgb
        assert high_cpc_fill == "00FFC7CE", f"High CPC row not highlighted (CPC={high_cpc})"


class TestExecutiveSummaryAggregationProperty:
    """Property-based tests for Executive Summary aggregation.

    **Feature: admetric-pro, Property 8: Executive Summary Aggregation**
    **Validates: Requirements 7.2, 7.3, 7.4, 7.5, 7.6**
    """

    @given(
        spend_values=st.lists(
            st.floats(min_value=100.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=10
        ),
        click_values=st.lists(
            st.integers(min_value=10, max_value=1000),
            min_size=1,
            max_size=10
        ),
        impression_values=st.lists(
            st.integers(min_value=1000, max_value=100000),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=50)
    def test_summary_aggregates_match_data(
        self,
        tmp_path_factory,
        spend_values: list[float],
        click_values: list[int],
        impression_values: list[int]
    ) -> None:
        """Property: Executive Summary aggregates match sum/average of campaign data.

        **Feature: admetric-pro, Property 8: Executive Summary Aggregation**
        **Validates: Requirements 7.2, 7.3, 7.4, 7.5, 7.6**

        For any set of campaign data, the Executive Summary SHALL display
        aggregates that match the sum/average of the underlying data.
        """
        tmp_path = tmp_path_factory.mktemp("reports")

        # Ensure all lists have same length
        min_len = min(len(spend_values), len(click_values), len(impression_values))
        spend_values = spend_values[:min_len]
        click_values = click_values[:min_len]
        impression_values = impression_values[:min_len]

        df = pd.DataFrame({
            "campaign_name": [f"Campaign {i}" for i in range(min_len)],
            "amount_spent": spend_values,
            "link_clicks": click_values,
            "impressions": impression_values,
            "ctr": [2.0 for _ in range(min_len)],
            "cpc": [s / c if c > 0 else 0 for s, c in zip(spend_values, click_values)]
        })

        report_path = generate_report(df, str(tmp_path))
        wb = load_workbook(report_path)
        summary_ws = wb["Executive Summary"]

        # Calculate expected values
        expected_total_spend = sum(spend_values)
        expected_total_clicks = sum(click_values)
        expected_total_impressions = sum(impression_values)

        # Find values in summary sheet
        summary_text = ""
        for row in summary_ws.iter_rows(min_row=1, max_row=15, max_col=2):
            for cell in row:
                if cell.value:
                    summary_text += str(cell.value) + " "

        # Verify Total Spend is present (formatted as R X,XXX.XX)
        assert f"{expected_total_spend:,.2f}" in summary_text, \
            f"Expected Total Spend {expected_total_spend:,.2f} not found in summary"
