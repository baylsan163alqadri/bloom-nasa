
"""SYNTHETIC data only. Not observed NASA results."""
import numpy as np
import pandas as pd
import pytest
from modules.trend_analysis import analyze_trend


def series(values, column="ndvi"):
    return pd.DataFrame({
        "year": np.arange(2005, 2005 + len(values)),
        "area_id": "area_a",
        column: values
    })


def test_increasing():
    result = analyze_trend(series(np.linspace(0.1, 0.4, 20)), "ndvi", 2005, 2024)
    assert result["direction"] == "increasing" and result["significant"]
    assert result["slope_per_decade"] == pytest.approx(result["slope_per_year"] * 10)


def test_decreasing():
    result = analyze_trend(series(np.linspace(0.4, 0.1, 20)), "ndvi", 2005, 2024)
    assert result["direction"] == "decreasing" and result["significant"]


def test_constant():
    result = analyze_trend(series([0.3] * 20), "ndvi", 2005, 2024)
    assert result["direction"] == "not_significant" and result["r_squared"] is None


def test_missing_not_zero_filled():
    v = [0.1 + i * 0.01 for i in range(20)]
    v[5] = None
    result = analyze_trend(series(v), "ndvi", 2005, 2024)
    assert result["n_observations"] == 19


def test_insufficient():
    result = analyze_trend(series([0.1] * 8), "ndvi", 2005, 2024)
    assert result["direction"] == "insufficient_data" and result["significant"] is None


def test_duplicate_years_rejected():
    df = series([0.1] * 20)
    df.loc[1, "year"] = 2005
    with pytest.raises(ValueError, match="duplicate"):
        analyze_trend(df, "ndvi", 2005, 2024)


def test_negative_rainfall_rejected():
    with pytest.raises(ValueError, match="negative"):
        analyze_trend(
            series([10.] * 19 + [-1.], "rainfall_mm"),
            "rainfall_mm",
            2005,
            2024
        )


def test_mixed_areas_rejected():
    df = series([0.1] * 20)
    df.loc[0, "area_id"] = "area_b"
    with pytest.raises(ValueError, match="one area"):
        analyze_trend(df, "ndvi", 2005, 2024)


def test_out_of_bounds_ndvi_rejected():
    with pytest.raises(ValueError, match="NDVI"):
        analyze_trend(series([1.5] * 20), "ndvi", 2005, 2024)
