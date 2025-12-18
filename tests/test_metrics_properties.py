"""Property-based tests for the Metrics Calculator module.

These tests verify universal correctness properties for CTR and CPC
calculations using the Hypothesis library.
"""

import pytest
import pandas as pd
from hypothesis import given, strategies as st, settings, assume

from src.metrics import calculate_ctr, calculate_cpc, add_metrics_to_dataframe


class TestCTRCalculationProperty:
    """Property-based tests for CTR calculation.

    **Feature: admetric-pro, Property 2: CTR Calculation Correctness**
    **Validates: Requirements 3.1, 3.3**
    """

    @given(
        clicks=st.integers(min_value=0, max_value=1_000_000),
        impressions=st.integers(min_value=1, max_value=10_000_000)
    )
    @settings(max_examples=100)
    def test_ctr_formula_correctness(self, clicks: int, impressions: int) -> None:
        """Property: CTR equals (clicks / impressions) × 100 for non-zero impressions.

        **Feature: admetric-pro, Property 2: CTR Calculation Correctness**
        **Validates: Requirements 3.1**

        For any campaign with non-zero impressions, the calculated CTR
        SHALL equal (link_clicks / impressions) × 100.

        Args:
            clicks: Generated click count.
            impressions: Generated impression count (non-zero).
        """
        result = calculate_ctr(clicks, impressions)
        expected = round((clicks / impressions) * 100, 2)

        assert result == expected, f"CTR mismatch: {result} != {expected}"

    @given(clicks=st.integers(min_value=0, max_value=1_000_000))
    @settings(max_examples=100)
    def test_ctr_zero_impressions_returns_zero(self, clicks: int) -> None:
        """Property: CTR equals 0.0 when impressions is zero.

        **Feature: admetric-pro, Property 2: CTR Calculation Correctness**
        **Validates: Requirements 3.3**

        For any campaign with zero impressions, CTR SHALL equal 0.0.

        Args:
            clicks: Generated click count.
        """
        result = calculate_ctr(clicks, 0)
        assert result == 0.0, f"CTR should be 0.0 for zero impressions, got {result}"

    @given(
        clicks=st.integers(min_value=0, max_value=1_000_000),
        impressions=st.integers(min_value=1, max_value=10_000_000)
    )
    @settings(max_examples=100)
    def test_ctr_is_non_negative(self, clicks: int, impressions: int) -> None:
        """Property: CTR is always non-negative.

        **Feature: admetric-pro, Property 2: CTR Calculation Correctness**
        **Validates: Requirements 3.1**

        Args:
            clicks: Generated click count.
            impressions: Generated impression count.
        """
        result = calculate_ctr(clicks, impressions)
        assert result >= 0.0, f"CTR should be non-negative, got {result}"

    @given(
        clicks=st.integers(min_value=0, max_value=1_000_000),
        impressions=st.integers(min_value=1, max_value=10_000_000)
    )
    @settings(max_examples=100)
    def test_ctr_bounded_by_clicks_ratio(self, clicks: int, impressions: int) -> None:
        """Property: CTR cannot exceed (clicks/impressions)*100.

        **Feature: admetric-pro, Property 2: CTR Calculation Correctness**
        **Validates: Requirements 3.1**

        Args:
            clicks: Generated click count.
            impressions: Generated impression count.
        """
        result = calculate_ctr(clicks, impressions)
        max_possible = (clicks / impressions) * 100

        assert result <= max_possible + 0.01, f"CTR {result} exceeds max {max_possible}"


class TestCPCCalculationProperty:
    """Property-based tests for CPC calculation.

    **Feature: admetric-pro, Property 3: CPC Calculation Correctness**
    **Validates: Requirements 3.2, 3.4**
    """

    @given(
        spend=st.floats(min_value=0.0, max_value=1_000_000.0, allow_nan=False, allow_infinity=False),
        clicks=st.integers(min_value=1, max_value=1_000_000)
    )
    @settings(max_examples=100)
    def test_cpc_formula_correctness(self, spend: float, clicks: int) -> None:
        """Property: CPC equals spend / clicks for non-zero clicks.

        **Feature: admetric-pro, Property 3: CPC Calculation Correctness**
        **Validates: Requirements 3.2**

        For any campaign with non-zero clicks, the calculated CPC
        SHALL equal (amount_spent / link_clicks).

        Args:
            spend: Generated spend amount in ZAR.
            clicks: Generated click count (non-zero).
        """
        result = calculate_cpc(spend, clicks)
        expected = round(spend / clicks, 2)

        assert result == expected, f"CPC mismatch: {result} != {expected}"

    @given(spend=st.floats(min_value=0.0, max_value=1_000_000.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_cpc_zero_clicks_returns_zero(self, spend: float) -> None:
        """Property: CPC equals 0.0 when clicks is zero.

        **Feature: admetric-pro, Property 3: CPC Calculation Correctness**
        **Validates: Requirements 3.4**

        For any campaign with zero clicks, CPC SHALL equal 0.0.

        Args:
            spend: Generated spend amount in ZAR.
        """
        result = calculate_cpc(spend, 0)
        assert result == 0.0, f"CPC should be 0.0 for zero clicks, got {result}"

    @given(
        spend=st.floats(min_value=0.0, max_value=1_000_000.0, allow_nan=False, allow_infinity=False),
        clicks=st.integers(min_value=1, max_value=1_000_000)
    )
    @settings(max_examples=100)
    def test_cpc_is_non_negative(self, spend: float, clicks: int) -> None:
        """Property: CPC is always non-negative.

        **Feature: admetric-pro, Property 3: CPC Calculation Correctness**
        **Validates: Requirements 3.2**

        Args:
            spend: Generated spend amount.
            clicks: Generated click count.
        """
        result = calculate_cpc(spend, clicks)
        assert result >= 0.0, f"CPC should be non-negative, got {result}"
