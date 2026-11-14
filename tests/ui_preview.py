"""Standalone BLOOM UI preview. ALL numerical examples are synthetic test data."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Allow imports when launched as: streamlit run tests/ui_preview.py
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.dashboard import render_dashboard  # noqa: E402
from modules.map_view import render_map  # noqa: E402

st.set_page_config(page_title="BLOOM — UI Preview", page_icon="🌱", layout="wide")
css_file = ROOT / "assets" / "bloom.css"
if css_file.is_file():
    st.markdown(f"<style>{css_file.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.markdown(
    '<section class="bloom-hero">'
    '<div class="bloom-eyebrow">NASA SPACE APPS 2026 · CASE 001</div>'
    '<h1>BLOOM</h1>'
    '<div class="bloom-tagline">Beyond the Green.</div>'
    '<p>Every green landscape has a story.<br>'
    'What is really happening to Jericho\'s greenery?</p>'
    '</section>',
    unsafe_allow_html=True,
)
st.warning("SYNTHETIC TEST DATA — NOT NASA OBSERVATIONS OR SCIENTIFIC FINDINGS")
st.caption("UI preview only. Final navigation, app integration, and real-data loading belong to the integration team.")

left, right = st.columns(2)
with left:
    selection = st.radio("Study area", ["area_a", "area_b"], horizontal=True,
                         format_func=lambda x: "Area A" if x == "area_a" else "Area B")
with right:
    scenario = st.selectbox("Preview scenario", [
        "Synthetic complete example", "No data", "Missing rainfall",
        "Insufficient statistics", "Non-significant trend", "Unreliable model",
    ])

# Never invent polygon coordinates. Use actual team GeoJSON only if available.
study_areas = {}
geojson_file = ROOT / "data" / "study_areas.geojson"
if geojson_file.is_file():
    try:
        study_areas = json.loads(geojson_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        st.warning("The study-area GeoJSON could not be read.")
render_map(study_areas, selection)

# Deterministic, explicitly synthetic test fixtures. No NASA data is generated here.
years = list(range(2005, 2025))
ndvi_values = [round(0.34 + 0.003 * (i - 10) + 0.035 * math.sin(i / 2.5), 4)
               for i in range(len(years))]
rain_values = [round(112 + 38 * math.sin(i / 2.2) + 15 * math.cos(i / 4.0), 2)
               for i in range(len(years))]
ndvi_df = pd.DataFrame({"year": years, "area_id": selection, "ndvi": ndvi_values})
rainfall_df = pd.DataFrame({"year": years, "area_id": selection, "rainfall_mm": rain_values})

ndvi_result = {
    "variable": "ndvi", "direction": "increasing", "significant": True,
    "slope_per_decade": 0.03, "p_value": 0.015, "status": "success",
}
rain_result = {
    "variable": "rainfall_mm", "direction": "not_significant", "significant": False,
    "slope_per_decade": -5.6, "p_value": 0.28, "status": "success",
}
trend_results = {"ndvi": ndvi_result, "rainfall": rain_result}
mystery_result = {
    "area_id": selection, "model_status": "validated",
    "validation_r2": 0.63, "validation_mae": 0.027,
    "anomalies": [{"year": 2014, "note": "Synthetic example flag — not a real anomaly"}],
    "opposing_trends": False,
    "verdict": "Synthetic example only. Model conclusions pending NASA data.",
    "limitations": ["All example values on this page are synthetic."],
}

if scenario == "No data":
    ndvi_df = ndvi_df.iloc[0:0]
    rainfall_df = rainfall_df.iloc[0:0]
    trend_results = {}
    mystery_result = {}
elif scenario == "Missing rainfall":
    rainfall_df = rainfall_df.iloc[0:0]
    trend_results["rainfall"] = {"direction": "insufficient_data", "significant": None}
elif scenario == "Insufficient statistics":
    trend_results = {
        "ndvi": {"direction": "insufficient_data", "significant": None},
        "rainfall": {"direction": "insufficient_data", "significant": None},
    }
    mystery_result = {"model_status": "not_evaluated"}
elif scenario == "Non-significant trend":
    trend_results["ndvi"] = {
        "direction": "not_significant", "significant": False,
        "slope_per_decade": 0.03, "p_value": 0.35, "status": "success",
    }
elif scenario == "Unreliable model":
    mystery_result = {"model_status": "insufficient_evidence", "limitations": ["Failed model validation."]}

render_dashboard(ndvi_df, rainfall_df, trend_results, mystery_result)
st.divider()
st.caption("BLOOM UI preview · Test fixtures only · NASA products require verified export and QA.")

