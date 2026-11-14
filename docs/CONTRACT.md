# BLOOM Integration Contract (v1.0) — DO NOT RENAME WITHOUT TEAM APPROVAL

## Data files
**NDVI**: `data/ndvi_annual.csv` with `year` (int), `area_id` (str), `ndvi` (float, unitless), `valid_observations` (int). Composite product: NASA MODIS MOD13Q1.061. Apply its 0.0001 scale factor and suitable quality masks when exporting.

**Rainfall**: `data/rainfall_annual.csv` with `year` (int), `area_id` (str), `rainfall_mm` (float, annual total mm). Product: NASA GPM IMERG Monthly V07. Convert source monthly precipitation rates (mm/hr) to monthly totals using actual hours per month before summing annual totals.

**Geography**: `data/study_areas.geojson` is a valid GeoJSON `FeatureCollection` with two polygon `Feature`s, each with `properties.area_id`: `area_a`, `area_b`. Use the **same exact polygons** for spatial aggregation and map display.

**Metadata**: `data/metadata.json` records region names, date coverage, NASA product IDs, units, aggregation, QA method, extraction date, and spatial-resolution limitations.

Annual data span 2005–2024 (20 years) when observations are available. Missing values are null/NaN, NEVER zero-filled. Rows keyed by (`year`, `area_id`) must be unique. Every selected study area must correspond to real, documented geography.

## Module interfaces (one agreed version)
```python
# modules/data_loader.py
load_datasets() -> tuple[ndvi_df, rainfall_df, geojson_dict, metadata_dict]

# modules/trend_analysis.py
analyze_trend(df, value_column: str, start_year: int, end_year: int) -> dict

# modules/mystery_engine.py
analyze_mystery(ndvi_df, rainfall_df, area_id: str) -> dict

# modules/map_view.py
render_map(study_areas: dict, selected_area_id: str) -> None

# modules/dashboard.py
render_dashboard(ndvi_df, rainfall_df, trend_results: dict, mystery_result: dict) -> None

# modules/report_generator.py
generate_report(area_id: str, study_period: tuple, trend_results: dict, mystery_result: dict, metadata: dict) -> str
```

`analyze_trend` receives an already filtered (ONE area) dataframe, then filters years itself. Caller should pass either NDVI or rainfall df (not a concatenation of two areas). Valid `value_column`: `ndvi` or `rainfall_mm`.

### TrendResult dictionary
```json
{
  "variable": "ndvi",
  "direction": "insufficient_data",
  "significant": null,
  "slope_per_year": null,
  "slope_per_decade": null,
  "p_value": null,
  "kendall_tau": null,
  "r_squared": null,
  "n_observations": 0,
  "status": "not_analyzed"
}
```
For successful analysis, allowed direction values: `increasing`, `decreasing`, `not_significant`, `insufficient_data`. `significant` is a boolean only when a test can be executed. Never interpret `not_significant` as stability.

### MysteryResult dictionary
```json
{
  "area_id": "area_a",
  "model_status": "not_evaluated",
  "validation_r2": null,
  "validation_mae": null,
  "anomalies": [],
  "opposing_trends": null,
  "verdict": "Pending analysis",
  "limitations": []
}
```
Rainfall-based prediction MUST have out-of-sample temporal validation and a documented anomaly threshold. On inadequate model performance, report `insufficient_evidence` instead of inventing anomalies. Correlation never establishes irrigation or causation. GPM spatial resolution may be far coarser than MODIS.

## Rules for all AI-generated code
- Python + Streamlit, **not** React or separate API backends.
- One entry point: `app.py`; one GitHub repo; four feature branches.
- Do not rename public functions, paths, or columns without team approval.
- If data are not ready: show a clear `Data unavailable` state.
- Avoid touching another teammate's files.
- Add tests for math and data validation.
