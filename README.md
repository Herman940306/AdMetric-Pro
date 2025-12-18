# AdMetric Pro

**Automated Data Engineering & Reporting Engine for High-Scale Digital Agencies**

*Eliminating 20+ hours of manual reporting for media teams — one command at a time.*

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/Tests-121%20Passing-brightgreen.svg)](#quality-assurance--testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Release](https://img.shields.io/badge/Release-v1.0.0-blue.svg)](https://github.com/Herman940306/AdMetric-Pro/releases)

---

## The Problem

Every week, your team exports campaign data from Meta Ads Manager. Then comes the tedious part:

- ⏱️ Manually calculating CTR and CPC for each campaign
- 💰 Formatting currency columns to ZAR (R)
- 🔴 Highlighting underperforming campaigns
- 📊 Creating summary sheets for clients

**Time wasted**: 2-4 hours per client, per week.

## The Solution

One command. Professional reports. Happy clients.

```bash
python -m src.main path/to/meta_export.csv
```

```
============================================================
[SUCCESS] Report generated: AdMetric_Pro_Report_2025-12-18_0744.xlsx
[SUMMARY] 16 Campaigns processed. 12 Red Flags found.
============================================================
```

---

## See it in Action

### Campaign Details Report
Red highlighting automatically flags campaigns with CPC > R20.00 — no manual formatting required.

![Campaign Details Preview](docs/assets/report_preview.png)

### Executive Summary Dashboard
One-glance overview of total spend, clicks, impressions, and key performance metrics.

![Executive Summary Preview](docs/assets/dashboard_preview.png)

---

## Key Features

| Feature | Business Value |
|---------|----------------|
| **Multi-Channel Data Aggregation** | Process Meta Ads exports with automatic column mapping |
| **ZAR Currency Formatting** | Reports ready for South African clients (R1,234.56) |
| **Automated Metric Calculations** | CTR and CPC calculated instantly with zero-division protection |
| **Intelligent Red Flagging** | High-cost campaigns (CPC > R20) highlighted automatically |
| **Executive Summary Dashboard** | One-page overview for busy clients and stakeholders |
| **Timestamped Output** | Never overwrite previous reports — full audit trail |
| **Configurable Thresholds** | Customize red flag limits per industry with `--cpc-threshold` |

---

## Quality Assurance & Testing

AdMetric Pro is built with **enterprise-grade reliability**:

### 121 Automated Tests
```
===================================== 121 passed in 17.64s =====================================
```

| Test Category | Count | Coverage |
|---------------|-------|----------|
| Unit Tests | 89 | Core functions, edge cases, error handling |
| Property-Based Tests | 32 | Hypothesis-powered fuzzing for data integrity |

**What we test:**
- ✅ CSV data preservation (round-trip integrity)
- ✅ Zero-division protection (CTR/CPC with 0 clicks)
- ✅ Excel formatting consistency (headers, currency, colors)
- ✅ Conditional formatting accuracy (CPC threshold highlighting)
- ✅ Executive Summary aggregation (totals match source data)

### Branch Protection & Security

This repository follows **enterprise security standards**:

- 🔒 **Protected main branch** — No direct pushes, all changes via PR
- 🏷️ **Semantic versioning** — Tagged releases (v1.0.0)
- 📋 **Conventional Commits** — Clean, traceable git history
- 🔐 **No sensitive data** — All client data in `.gitignore`

---

## Installation

```bash
# Clone the repository
git clone https://github.com/Herman940306/AdMetric-Pro.git
cd AdMetric-Pro

# Install dependencies
pip install -r requirements.txt
```

### Modern Installation (pyproject.toml)
```bash
pip install -e .
```

---

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
| Column | Description |
|--------|-------------|
| `Campaign Name` | Name of the advertising campaign |
| `Amount Spent (ZAR)` | Total spend in South African Rand |
| `Link Clicks` | Number of link clicks |
| `Impressions` | Number of ad impressions |

---

## Output

AdMetric Pro generates a professionally formatted Excel workbook:

| Sheet | Contents |
|-------|----------|
| **Campaign Details** | All campaigns with CTR, CPC, and red flag highlighting |
| **Executive Summary** | Total Spend, Impressions, Clicks, Avg CPC, Overall CTR |

**Filename format:** `AdMetric_Pro_Report_YYYY-MM-DD_HHMM.xlsx`

---

## Architecture

```
AdMetric-Pro/
├── src/
│   ├── main.py              # CLI entry point with argument parsing
│   ├── csv_reader.py        # CSV ingestion and column validation
│   ├── metrics.py           # CTR/CPC calculations with edge case handling
│   ├── excel_formatter.py   # Professional Excel styling and output
│   └── generate_visuals.py  # README preview image generation
├── tests/                   # 121 automated tests (Pytest + Hypothesis)
├── docs/assets/             # Visual previews for documentation
├── mock_data/               # Sample data for testing and demos
└── output/                  # Generated reports (gitignored)
```

---

## Design Decisions & Technical Choices

### Why openpyxl?

We chose **openpyxl** over alternatives like xlsxwriter for its superior styling capabilities:
- Native support for conditional formatting rules
- Fine-grained control over cell colors, fonts, and borders
- Ability to read and modify existing Excel files
- Active maintenance and excellent documentation

### Why R20.00 as the Default CPC Threshold?

The R20.00 threshold is based on **South African digital advertising benchmarks**:
- Average CPC for Facebook Ads in SA ranges from R5-R15 for most industries
- Campaigns exceeding R20.00 CPC typically indicate targeting issues or low-quality traffic
- This threshold can be customized via `--cpc-threshold` for different industries

### Architecture Principles

- **Modular Design**: Separate modules for CSV reading, metrics calculation, and Excel formatting allow independent testing and future extensibility
- **Property-Based Testing**: Using Hypothesis for comprehensive edge case coverage
- **Defensive Programming**: Zero-division protection, graceful error handling, detailed logging

---

## Roadmap

- [ ] Google Ads CSV support
- [ ] Multi-currency support (USD, EUR, GBP)
- [ ] Direct Meta Ads API integration
- [ ] Automated email delivery of reports
- [ ] Web dashboard interface

---

## License

MIT License — Built for the Cape Town marketing community.

---

## About the Author

Built by **Herman Swanepoel** — a data engineer passionate about eliminating manual work for digital agencies.

📍 Cape Town, South Africa

---

**Questions?** [Open an issue](https://github.com/Herman940306/AdMetric-Pro/issues) or reach out. We're here to help agencies work smarter.
