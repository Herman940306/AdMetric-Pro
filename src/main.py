"""Main entry point for AdMetric Pro.

This module provides the CLI interface for processing Meta Ads CSV
exports into professionally formatted Excel reports.

Usage:
    python -m src.main path/to/meta_ads.csv
    python -m src.main path/to/meta_ads.csv --output reports/
    python -m src.main path/to/meta_ads.csv --cpc-threshold 25.00
"""

import argparse
import logging
import sys
from pathlib import Path

from src.csv_reader import read_meta_csv
from src.metrics import add_metrics_to_dataframe
from src.excel_formatter import generate_report, CPC_THRESHOLD

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for AdMetric Pro CLI.

    Configures and parses arguments for the report generation pipeline,
    including input file path, output directory, CPC threshold, and
    verbosity settings.

    Args:
        args: List of command-line arguments to parse. If None, uses sys.argv.
            Primarily used for testing purposes.

    Returns:
        Namespace containing parsed arguments with attributes:
            - input_file (str): Path to the Meta Ads CSV file.
            - output (str): Output directory for the Excel report.
            - cpc_threshold (float): CPC threshold for red highlighting.
            - verbose (bool): Whether to enable verbose logging.

    Example:
        >>> args = parse_arguments(["data/meta_ads.csv", "--output", "reports/"])
        >>> args.input_file
        'data/meta_ads.csv'
        >>> args.output
        'reports/'
    """
    parser = argparse.ArgumentParser(
        prog="AdMetric Pro",
        description="Transform Meta Ads CSV exports into client-ready Excel reports.",
        epilog="Built for Cape Town digital marketing agencies."
    )

    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the Meta Ads CSV file exported from Ads Manager."
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output",
        help="Output directory for the Excel report (default: output/)."
    )

    parser.add_argument(
        "--cpc-threshold", "-t",
        type=float,
        default=CPC_THRESHOLD,
        help=f"CPC threshold for red highlighting in ZAR (default: R{CPC_THRESHOLD:.2f})."
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging output."
    )

    return parser.parse_args(args)


def main() -> int:
    """Main entry point for AdMetric Pro.

    Orchestrates the complete pipeline:
    1. Read and validate Meta Ads CSV
    2. Calculate CTR and CPC metrics
    3. Generate formatted Excel report

    Returns:
        Exit code (0 for success, 1 for error).

    Example:
        >>> # From command line:
        >>> python -m src.main data/meta_export.csv --output reports/
    """
    args = parse_arguments()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("=" * 60)
    logger.info("AdMetric Pro - Meta Ads Report Generator")
    logger.info("=" * 60)

    try:
        # Step 1: Read CSV
        logger.info("Step 1/3: Reading Meta Ads CSV...")
        input_path = Path(args.input_file)
        df = read_meta_csv(str(input_path))
        logger.info("Loaded %d campaigns from %s", len(df), input_path.name)

        # Step 2: Calculate metrics
        logger.info("Step 2/3: Calculating CTR and CPC metrics...")
        df_with_metrics = add_metrics_to_dataframe(df)

        # Log summary statistics
        total_spend = df_with_metrics["amount_spent"].sum()
        avg_cpc = df_with_metrics[df_with_metrics["cpc"] > 0]["cpc"].mean()
        high_cpc_count = len(df_with_metrics[df_with_metrics["cpc"] > args.cpc_threshold])

        logger.info("Total Spend: R%.2f", total_spend)
        logger.info("Average CPC: R%.2f", avg_cpc if avg_cpc == avg_cpc else 0)  # Handle NaN
        logger.info("Campaigns with CPC > R%.2f: %d", args.cpc_threshold, high_cpc_count)

        # Step 3: Generate report
        logger.info("Step 3/3: Generating Excel report...")

        # Update CPC threshold if custom value provided
        if args.cpc_threshold != CPC_THRESHOLD:
            from src import excel_formatter
            excel_formatter.CPC_THRESHOLD = args.cpc_threshold
            logger.info("Using custom CPC threshold: R%.2f", args.cpc_threshold)

        report_path = generate_report(df_with_metrics, args.output)

        logger.info("=" * 60)
        logger.info("SUCCESS! Report generated: %s", report_path)
        logger.info("=" * 60)

        return 0

    except FileNotFoundError as e:
        logger.error("File not found: %s", e)
        return 1
    except ValueError as e:
        logger.error("Data validation error: %s", e)
        return 1
    except IOError as e:
        logger.error("Failed to write report: %s", e)
        return 1
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        logger.debug("Full traceback:", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
