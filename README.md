# Analysis code and data

Manuscript: Characterisation of ambient air pollutant concentrations at animal-singeing sites in urban Ghana: a fixed-point monitoring study and its implications for air quality (SCIAF-D-26-03855)

Everything reported in the manuscript and supplementary file is produced by the scripts in this folder from one input file.

## Contents

| Path | What it is |
| --- | --- |
| `data/pollution_data_raw.xlsx` | The hourly workbook as received: one sheet per site, 360 records per site (359 at TL) |
| `results/clean.csv` | The cleaned analysis dataset (see cleaning rules below) |
| `results/` | All numerical output: descriptive statistics, tests, model coefficients, fit statistics, sensitivity analyses |
| `figures/` | Figures 1 to 5 and Figure S1 at publication resolution |
| `fig/` | Individual figure panels as placed in the manuscript |
| `01_` to `07_` scripts | The analysis, in run order |

## How to run

Requires Python 3 with pandas, numpy, scipy, statsmodels, patsy, matplotlib, openpyxl and pillow. Run from this folder, in order:

```
python 01_main_analysis.py
python 02_spline_models.py
python 03_sensitivity_analyses.py
python 04_figure1_flowchart.py
python 05_figure4_heatmaps.py
python 06_figureS1_site_splines.py
python 07_figures2_3_and_composites.py
```

Versions used: pandas 3.0.5, numpy 2.5.3, scipy 1.18.1, statsmodels 0.15.0, matplotlib 3.11.2.

## What each script produces

| Script | Output | Used for |
| --- | --- | --- |
| `01_main_analysis.py` | `clean.csv`, `desc.csv`, `mw.csv`, `spearman_*.csv`, `coef.csv`, `fit.csv`, `meta.json` | Table 2, Tables S1 to S4, Figure 4 values, Results text |
| `02_spline_models.py` | `spline.csv`, `splinepred.json`, `splinesite.json` | Table S5, Figure S1 |
| `03_sensitivity_analyses.py` | `daily_mw.csv`, `resid_ac.csv`, `completeness.csv`, `spline_sens.csv`, `splineband.json`, Figure 5 | Tables S5, S7, S8, Figure 5 |
| `04_figure1_flowchart.py` | Figure 1 | Study design flowchart |
| `05_figure4_heatmaps.py` | Figure 4 panels | Spearman correlation heatmaps |
| `06_figureS1_site_splines.py` | Figure S1 panels | Site-specific spline fits |
| `07_figures2_3_and_composites.py` | Figures 2 and 3, composite figure files | Boxplots and final figure files |

## Cleaning rules applied in `01_main_analysis.py`

1. The unlabelled 361st row in the AM sheet is dropped.
2. Particulate readings are divided by 1,000 to express them in µg/m³.
3. Where the value entered as PM10 is lower than the value entered as PM2.5, the two values are exchanged (treated as a data-entry error). Rows affected: AM 212, AV 235, JM 189, TL 359.
4. CO, SO2 and VOC values at AV that had been filled by linear interpolation (42 records) are set to missing.
5. One air-temperature reading above 45 °C (TL) and eight relative-humidity readings below 50% are set to missing.
6. Monitoring day is assigned as consecutive blocks of 12 records (day 1 = records 1 to 12, and so on). The workbook has no dates or clock times.

The number of rows changed by each rule is written to `results/meta.json`.

## Codebook for `results/clean.csv`

| Column | Meaning | Unit |
| --- | --- | --- |
| `Hour` | Sequential record number within site, 1 to 360 | – |
| `Site` | Anonymised site code: AM, AV (LPG-fuel); JM, TL (tyre-fuel) | – |
| `day` | Monitoring day, 1 to 30 (assigned from record order) | – |
| `CO` | Carbon monoxide, hourly average | ppm |
| `SO2` | Sulphur dioxide, hourly average | ppm |
| `VOC` | Non-speciated volatile organic compounds, calibration-gas equivalent | ppm |
| `PM25` | PM2.5 after rules 2 and 3 | µg/m³ |
| `PM10` | PM10 after rules 2 and 3 | µg/m³ |
| `AT` | Air temperature | °C |
| `RH` | Relative humidity | % |

The sheets in the raw workbook are named by site code (AM, AV, JM, TL); the real site names have been removed.

## Statistical methods

- Between-site comparisons: two-sided Mann–Whitney U tests on hourly records, with probability of superiority; repeated on daily medians as a sensitivity analysis.
- Correlations: Spearman rank correlations within each site.
- Mixed-effects models (CO, SO2, PM2.5, PM10): site × standardised temperature and humidity, random intercept for monitoring day within site, REML. VOCs: OLS with day-clustered standard errors.
- Spline models: log-link regression (Poisson quasi-likelihood), site fixed effect, cubic B-splines with 3 degrees of freedom for temperature and humidity, standard errors clustered by day; joint Wald tests; repeated after excluding the lowest and highest 5% of temperature and humidity.
