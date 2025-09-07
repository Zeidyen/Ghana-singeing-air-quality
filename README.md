# Data guide

This project does not store raw or processed data in the repo.

## Where to get data
- Field measurements (PM2.5, PM10, CO, SO₂, VOCs) – provide source or contact.
- Climate (AT, RH) – specify source (e.g., on-site logger or public API) and timeframe.

## Expected structure
pollution/data/
├── raw/         # raw CSVs as collected
└── processed/   # cleaned/derived tables produced by scripts

## Privacy
Remove personally identifiable info and precise coordinates if sensitive.

## Ethics & Data Availability
This study received ethics approval from CSIR Ghana (Protocol CSIR-IRB0046/2024).
Raw/linked datasets are **restricted** and not posted here. See:
- [ETHICS.md](./ETHICS.md)
- [DATA_AVAILABILITY.md](./DATA_AVAILABILITY.md)


## How to run (locally)

> Assumes your cleaned hourly CSV is at `pollution/data/processed/merged_hourly.csv`.

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m src.stats pollution/data/processed/merged_hourly.csv pollution/reports/tables
ls pollution/reports/tables
