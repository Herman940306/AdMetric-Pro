"""Visual Generation utility for AdMetric Pro.

This script generates high-quality preview images for the README
to showcase the tool's output to potential clients. These visuals
serve as marketing assets demonstrating the professional quality
of AdMetric Pro reports.

Usage:
    python -m src.generate_visuals

Example:
    >>> from src.generate_visuals import generate_executive_summary_image
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     "amount_spent": [1000.0],
    ...     "impressions": [5000],
    ...     "link_clicks": [100]
    ... })
    >>> generate_executive_summary_image(df, "output/summary.png")
"""

import logging
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from src.csv_reader import read_meta_csv
from src.metrics import add_metrics_to_dataframe

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Style constants
DARK_BLUE = "#1F4E79"
LIGHT_BLUE = "#2E75B6"
WHITE = "#FFFFFF"
LIGHT_GRAY = "#D6DCE4"
RED_FLAG = "#FFC7CE"
CPC_THRESHOLD = 20.00


def generate_executive_summary_image(df: pd.DataFrame, output_path: str) -> None:
    """Generate Executive Summary dashboard preview image.

    Creates a clean, professional table showing aggregated metrics
    that would appear in the Executive Summary sheet. This image
    is used in the README to showcase the dashboard output.

    Args:
        df: DataFrame with campaign data and calculated metrics.
            Expected columns: amount_spent, impressions, link_clicks.
        output_path: Path to save the PNG image.

    Returns:
        None. Writes image file to output_path.

    Raises:
        KeyError: If required columns are missing from DataFrame.
        ValueError: If Plotly cannot generate the image.

    Example:
        >>> df = pd.DataFrame({
        ...     "amount_spent": [1000.0, 500.0],
        ...     "impressions": [5000, 2500],
        ...     "link_clicks": [100, 50]
        ... })
        >>> generate_executive_summary_image(df, "docs/assets/summary.png")
    """
    logger.info("Generating Executive Summary preview...")

    # Calculate aggregates
    total_spend = df["amount_spent"].sum()
    total_impressions = df["impressions"].sum()
    total_clicks = df["link_clicks"].sum()
    avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0
    overall_ctr = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0

    # Create summary data
    metrics = ["Total Spend", "Total Impressions", "Total Clicks", "Average CPC", "Overall CTR"]
    values = [
        f"R {total_spend:,.2f}",
        f"{total_impressions:,}",
        f"{total_clicks:,}",
        f"R {avg_cpc:.2f}",
        f"{overall_ctr:.2f}%"
    ]

    # Create figure
    fig = go.Figure()

    # Add table
    fig.add_trace(go.Table(
        header=dict(
            values=["<b>Metric</b>", "<b>Value</b>"],
            fill_color=LIGHT_BLUE,
            font=dict(color=WHITE, size=14),
            align="center",
            height=35
        ),
        cells=dict(
            values=[metrics, values],
            fill_color=[LIGHT_GRAY, WHITE],
            font=dict(color="#333333", size=13),
            align=["left", "right"],
            height=30
        )
    ))

    # Update layout
    fig.update_layout(
        title=dict(
            text="<b>AdMetric Pro - Executive Summary</b>",
            font=dict(size=18, color=DARK_BLUE),
            x=0.5
        ),
        width=500,
        height=300,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    # Save image
    fig.write_image(output_path, scale=2)
    logger.info("Saved: %s", output_path)


def generate_report_preview_image(df: pd.DataFrame, output_path: str, top_n: int = 10) -> None:
    """Generate Campaign Details report preview image.

    Creates a preview showing the top campaigns with ZAR formatting
    and red flag highlighting for high CPC campaigns (CPC > R20.00).
    This image demonstrates the conditional formatting feature.

    Args:
        df: DataFrame with campaign data and calculated metrics.
            Expected columns: campaign_name, amount_spent, link_clicks,
            impressions, ctr, cpc.
        output_path: Path to save the PNG image.
        top_n: Number of campaigns to show (default: 10).

    Returns:
        None. Writes image file to output_path.

    Raises:
        KeyError: If required columns are missing from DataFrame.
        ValueError: If Plotly cannot generate the image.

    Example:
        >>> df = pd.DataFrame({
        ...     "campaign_name": ["Summer Sale"],
        ...     "amount_spent": [1000.0],
        ...     "link_clicks": [50],
        ...     "impressions": [2500],
        ...     "ctr": [2.0],
        ...     "cpc": [20.0]
        ... })
        >>> generate_report_preview_image(df, "docs/assets/report.png", top_n=5)
    """
    logger.info("Generating Report preview (top %d campaigns)...", top_n)

    # Get top campaigns by spend
    preview_df = df.head(top_n).copy()

    # Format values for display
    campaign_names = preview_df["campaign_name"].tolist()
    spend_formatted = [f"R {v:,.2f}" for v in preview_df["amount_spent"]]
    clicks = preview_df["link_clicks"].tolist()
    impressions = [f"{v:,}" for v in preview_df["impressions"]]
    ctr_formatted = [f"{v:.2f}%" for v in preview_df["ctr"]]
    cpc_formatted = [f"R {v:.2f}" for v in preview_df["cpc"]]

    # Determine row colors (red for high CPC)
    row_colors = []
    for cpc in preview_df["cpc"]:
        if cpc > CPC_THRESHOLD:
            row_colors.append(RED_FLAG)
        else:
            row_colors.append(WHITE)

    # Create figure
    fig = go.Figure()

    # Add table
    fig.add_trace(go.Table(
        header=dict(
            values=[
                "<b>Campaign Name</b>",
                "<b>Spend (ZAR)</b>",
                "<b>Clicks</b>",
                "<b>Impressions</b>",
                "<b>CTR</b>",
                "<b>CPC (ZAR)</b>"
            ],
            fill_color=DARK_BLUE,
            font=dict(color=WHITE, size=12),
            align="center",
            height=35
        ),
        cells=dict(
            values=[
                campaign_names,
                spend_formatted,
                clicks,
                impressions,
                ctr_formatted,
                cpc_formatted
            ],
            fill_color=[row_colors] * 6,
            font=dict(color="#333333", size=11),
            align=["left", "right", "right", "right", "right", "right"],
            height=28
        )
    ))

    # Update layout
    fig.update_layout(
        title=dict(
            text="<b>AdMetric Pro - Campaign Details</b><br><sup>🔴 Red rows indicate CPC > R20.00</sup>",
            font=dict(size=16, color=DARK_BLUE),
            x=0.5
        ),
        width=900,
        height=450,
        margin=dict(l=20, r=20, t=80, b=20)
    )

    # Save image
    fig.write_image(output_path, scale=2)
    logger.info("Saved: %s", output_path)


def main() -> int:
    """Generate all visual assets for README.

    Orchestrates the complete visual generation pipeline:
    1. Load sample campaign data from mock_data/
    2. Calculate CTR and CPC metrics
    3. Generate Executive Summary dashboard image
    4. Generate Campaign Details report preview image

    Returns:
        Exit code (0 for success, 1 for error).

    Raises:
        FileNotFoundError: If mock data file is not found.
        IOError: If images cannot be written to disk.

    Example:
        >>> exit_code = main()
        >>> assert exit_code == 0
    """
    logger.info("=" * 50)
    logger.info("AdMetric Pro - Visual Generator")
    logger.info("=" * 50)

    try:
        # Create output directory
        assets_dir = Path("docs/assets")
        assets_dir.mkdir(parents=True, exist_ok=True)

        # Load and process data
        logger.info("Loading mock data...")
        df = read_meta_csv("mock_data/sample_meta_ads.csv")
        df = add_metrics_to_dataframe(df)

        # Generate images
        generate_executive_summary_image(df, str(assets_dir / "dashboard_preview.png"))
        generate_report_preview_image(df, str(assets_dir / "report_preview.png"))

        logger.info("=" * 50)
        logger.info("Visual generation complete!")
        logger.info("Assets saved to: docs/assets/")
        logger.info("=" * 50)

        return 0

    except FileNotFoundError as e:
        logger.error("Mock data file not found: %s", e)
        return 1
    except IOError as e:
        logger.error("Failed to write image: %s", e)
        return 1
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
