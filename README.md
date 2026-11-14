# BLOOM 
**Beyond the Green — Jericho, Palestine**

NASA Space Apps Challenge 2026 — Be An Earth System Trend Detective!

BLOOM investigates long-term vegetation change (NDVI) in two predefined study areas near Jericho, using NASA MODIS vegetation and NASA GPM precipitation products. It will test statistical trends and explore unusual vegetation responses to regional rainfall.

## Team foundation (Phase 1)
This repository is a **working starter skeleton**, not a finished analysis. No real NASA observations are bundled yet, and no findings are claimed.

## Local launch
```bash
python -m venv .venv
# Activate your virtual environment using your operating system's instructions
pip install -r requirements.txt
streamlit run app.py
```

## Data and interfaces
Read [`docs/CONTRACT.md`](docs/CONTRACT.md) **before coding** and [`docs/TEAM_TASKS.md`](docs/TEAM_TASKS.md) for file ownership.

## Planned data files (not yet included)
- `data/ndvi_annual.csv` — `year,area_id,ndvi,valid_observations`
- `data/rainfall_annual.csv` — `year,area_id,rainfall_mm`
- `data/study_areas.geojson` — Polygon FeatureCollection with `area_id` values `area_a`, `area_b`
- `data/metadata.json` — provenance, methods and quality metadata

### Scientific guardrails
- Never present test fixtures or model estimates as NASA measurements.
- A statistically non-significant trend is **not** proof of stability.
- A rainfall–vegetation difference is not evidence of irrigation or causation on its own.
- GPM precipitation is much coarser spatially than MODIS NDVI.

## Version control
Use branches `feature/nasa-data`, `feature/statistics`, `feature/ui`, and `feature/integration`. Only merge reviewed, runnable changes into `main`.
