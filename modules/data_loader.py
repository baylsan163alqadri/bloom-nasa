"""Data Team owns this module. Stable output contract: 4 objects."""
from pathlib import Path
import json
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def load_datasets():
    """Return (ndvi_df, rainfall_df, areas_geojson, metadata).

    Absent datasets are returned empty, never synthesized as NASA data.
    """
    ndvi_path = DATA_DIR / "ndvi_annual.csv"
    rainfall_path = DATA_DIR / "rainfall_annual.csv"
    geo_path = DATA_DIR / "study_areas.geojson"
    meta_path = DATA_DIR / "metadata.json"

    ndvi = pd.read_csv(ndvi_path) if ndvi_path.exists() else pd.DataFrame(
        columns=["year", "area_id", "ndvi", "valid_observations"])
    rain = pd.read_csv(rainfall_path) if rainfall_path.exists() else pd.DataFrame(
        columns=["year", "area_id", "rainfall_mm"])
    geo = json.loads(geo_path.read_text(encoding="utf-8")) if geo_path.exists() else {
        "type": "FeatureCollection", "features": []}
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    return ndvi, rain, geo, meta
