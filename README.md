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
