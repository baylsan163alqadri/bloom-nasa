
"""SYNTHETIC data only. Not observed NASA results."""
import numpy as np
import pandas as pd
import pytest
from modules.mystery_engine import analyze_mystery


def data(seed=1, predictability=True):
    rng = np.random.default_rng(seed)
    years = np.arange(2005, 2025)
    rainfall = rng.uniform(100, 800, len(years))
    if predictability:
        ndvi = 0.2 + 0.0005 * rainfall + rng.normal(0, 0.009, len(years))
    else:
        ndvi = rng.uniform(0.1, 0.6, len(years))
    return (
        pd.DataFrame({
            "year": years,
            "area_id": "area_a",
            "ndvi": ndvi
        }),
        pd.DataFrame({
            "year": years,
            "area_id": "area_a",
            "rainfall_mm": rainfall
        })
    )


def test_reliable_model_can_validate():
    nd, rain = data()
    result = analyze_mystery(nd, rain, "area_a")
    assert result["model_status"] == "validated" and result["validation_r2"] > 0
    assert result["validation_mae"] >= 0


def test_weak_model_not_alerted():
    nd, rain = data(predictability=False)
    result = analyze_mystery(nd, rain, "area_a")
    assert result["model_status"] == "insufficient_evidence"
    assert result["anomalies"] == []


def test_no_year_overlap():
    nd, rain = data()
    rain["year"] += 30
    result = analyze_mystery(nd, rain, "area_a")
    assert result["model_status"] == "insufficient_evidence"


def test_missing_input():
    nd, rain = data()
    result = analyze_mystery(nd.iloc[:0], rain, "area_a")
    assert result["model_status"] == "insufficient_evidence"


def test_chronological_holdout_protects_against_future_leakage():
    nd, rain = data()
    nd.loc[nd["year"] >= 2019, "ndvi"] = 0.95
    result = analyze_mystery(nd, rain, "area_a")
    assert result["model_status"] == "insufficient_evidence"
    assert result["anomalies"] == []


def test_duplicate_year_rejected():
    nd, rain = data()
    nd.loc[1, "year"] = nd.loc[0, "year"]
    with pytest.raises(ValueError, match="duplicate"):
        analyze_mystery(nd, rain, "area_a")


def test_negative_rain_rejected():
    nd, rain = data()
    rain.loc[0, "rainfall_mm"] = -3
    with pytest.raises(ValueError, match="negative"):
        analyze_mystery(nd, rain, "area_a")
