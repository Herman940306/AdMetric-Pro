# AdMetric Pro

**Eliminate the Excel Headache. Deliver Client-Ready Reports in Seconds.**

AdMetric Pro is a Python automation tool built for Cape Town digital marketing agencies. It transforms raw Meta (Facebook) Ads CSV exports into professionally formatted Excel reports—complete with ZAR currency formatting, calculated metrics, and executive summaries.

## The Problem We Solve

Every week, your team exports campaign data from Meta Ads Manager. Then comes the tedious part:
- Manually calculating CTR and CPC for each campaign
- Formatting currency columns to ZAR (R)
- Highlighting underperforming campaigns
- Creating summary sheets for clients

**Time wasted**: 2-4 hours per client, per week.

## The AdMetric Pro Solution

One command. Professional reports. Happy clients.

```bash
python -m src.main path/to/meta_export.csv
```

**What you get:**
- Automatic CTR and CPC calculations
- ZAR currency formatting (R1,234.56)
- Red highlighting for campaigns with CPC > R20.00
- Executive Summary sheet with totals and averages
- Timestamped filenames to preserve report history

## See it in Action

### Campaign Details Report
Red highlighting automatically flags campaigns with CPC > R20.00 — no manual formatting required.

![Campaign Details Preview](docs/assets/report_preview.png)

### Executive Summary Dashboard
One-glance overview of total spend, clicks, impressions, and key performance metrics.

![Executive Summary Preview](docs/assets/dashboard_preview.png)

## Features

| Feature | Benefit |
|---------|---------|
| **ZAR Currency Formatting** | Reports ready for South African clients |
| **Automatic Metrics** | CTR and CPC calculated instantly |
| **Conditional Formatting** | High-cost campaigns highlighted in red |
| **Executive Summary** | One-page overview for busy clients |
| **Timestamped Output** | Never overwrite previous reports |
| **Custom CPC Threshold** | Set your own red flag limit with `--cpc-threshold` |

## Installation

```bash
# Clone the repository
git clone https://github.com/Herman940306/AdMetric-Pro.git
cd AdMetric-Pro

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python -m src.main path/to/your/meta_ads_export.csv
```

### With Custom Output Directory

```bash
python -m src.main path/to/meta_ads_export.csv --output reports/
```

### With Custom CPC Threshold

```bash
python -m src.main path/to/meta_ads_export.csv --cpc-threshold 25.00
```

### Expected CSV Columns

Your Meta Ads export must include:
- `Campaign Name`
- `Amount Spent (ZAR)`
- `Link Clicks`
- `Impressions`

## Output

AdMetric Pro generates an Excel file with two sheets:

1. **Campaign Details**: All campaigns with calculated CTR and CPC
2. **Executive Summary**: Total Spend, Impressions, Clicks, Average CPC, Overall CTR

Output filename format: `AdMetric_Pro_Report_2025-12-18_1430.xlsx`

## For Developers

### Running Tests

```bash
pytest tests/ -v
```

### Project Structure

```
AdMetric-Pro/
├── src/
│   ├── main.py           # CLI entry point
│   ├── csv_reader.py     # CSV ingestion and validation
│   ├── metrics.py        # CTR/CPC calculations
│   └── excel_formatter.py # Excel styling and output
├── tests/
├── mock_data/
├── output/
└── requirements.txt
```

## Design Decisions & Technical Choices

### Why openpyxl?

We chose **openpyxl** over alternatives like xlsxwriter for its superior styling capabilities:
- Native support for conditional formatting rules
- Fine-grained control over cell colors, fonts, and borders
- Ability to read and modify existing Excel files
- Active maintenance and excellent documentation

### Why R20.00 as the Default CPC Threshold?

The R20.00 threshold is based on South African digital advertising benchmarks:
- Average CPC for Facebook Ads in SA ranges from R5-R15 for most industries
- Campaigns exceeding R20.00 CPC typically indicate targeting issues or low-quality traffic
- This threshold can be customized via `--cpc-threshold` for different industries

### Architecture Decisions

- **Modular Design**: Separate modules for CSV reading, metrics calculation, and Excel formatting allow independent testing and future extensibility
- **Property-Based Testing**: Using Hypothesis for comprehensive edge case coverage (zero-division, data preservation)
- **Logging + Print**: Detailed logging for debugging, clean terminal output for end-users

## License

MIT License - Built for the Cape Town marketing community.

---

**Questions?** Open an issue or reach out. We're here to help agencies work smarter.
