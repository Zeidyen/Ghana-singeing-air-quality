# Data guide

Raw/processed data are **not** stored in this repository.

## Expected columns (hourly)
- `timestamp` (ISO 8601, local time Africa/Accra preferred)
- `site` (e.g., Tulaku, James Town, Amasaman, Avernor)
- Pollutants (units in parentheses; choose one per species)
  - `PM25` (µg/m³)
  - `PM10` (µg/m³)
  - `CO` (ppm or mg/m³)
  - `SO2` (ppm or µg/m³)
  - `VOCs` (ppm)
- Climate
  - `AT` (°C) – Atmospheric Temperature
  - `RH` (%) – Relative Humidity

## Folders
