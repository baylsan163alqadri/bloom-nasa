
"""BLOOM annual time-series trend analysis (one geographic area per call).

The 10-observation minimum and alpha=0.05 are prototype conventions.
The unmodified Mann-Kendall test assumes independent observations; serial
correlation, missing years and multiple testing can affect interpretation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, linregress

try:
    import pymannkendall as mk
except ImportError:
    mk = None

MIN_OBSERVATIONS = 10
ALPHA = 0.05


def analyze_trend(df, value_column: str, start_year: int, end_year: int) -> dict:
    """Estimate yearly/decadal slope and Mann-Kendall trend of ONE area.

    Invalid schema, duplicate years, mixed areas or impossible values raise
    ValueError. Insufficient usable years return the declared result envelope.
    Null measurements are excluded, never replaced by zero.
    """
    if value_column not in ("ndvi", "rainfall_mm"):
        raise ValueError("value_column must be 'ndvi' or 'rainfall_mm'")
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if not isinstance(start_year, (int, np.integer)) or not isinstance(end_year, (int, np.integer)) or start_year > end_year:
        raise ValueError("invalid year range")
    result = {
        "variable": value_column,
        "direction": "insufficient_data",
        "significant": None,
        "slope_per_year": None,
        "slope_per_decade": None,
        "p_value": None,
        "kendall_tau": None,
        "r_squared": None,
        "n_observations": 0,
        "status": "not_analyzed",
    }
    required = {"year", "area_id", value_column}
    if not required.issubset(df.columns):
        raise ValueError(f"missing columns: {sorted(required - set(df.columns))}")
    work = df.copy()
    if work["area_id"].isna().any() or work["area_id"].nunique(dropna=False) > 1:
        raise ValueError("analyze_trend accepts exactly one area_id")
    if work["year"].isna().any():
        raise ValueError("years cannot be missing")
    years = pd.to_numeric(work["year"], errors="coerce")
    if years.isna().any() or (~np.isfinite(years.to_numpy(dtype=float))).any() or (years % 1 != 0).any():
        raise ValueError("years must be finite integers")
    work["year"] = years.astype(int)
    if work["year"].duplicated().any():
        raise ValueError("duplicate years for this study area")
    vals = pd.to_numeric(work[value_column], errors="coerce")
    if (work[value_column].notna() & vals.isna()).any():
        raise ValueError("measurements must be numeric or missing")
    if np.isinf(vals.to_numpy(dtype=float)).any():
        raise ValueError("infinite measurements not allowed")
    if value_column == "ndvi" and ((vals < -1) | (vals > 1)).any():
        raise ValueError("NDVI must be within [-1, 1]")
    if value_column == "rainfall_mm" and (vals < 0).any():
        raise ValueError("rainfall_mm cannot be negative")
    work[value_column] = vals
    work = work.loc[work["year"].between(start_year, end_year)].dropna(subset=[value_column]).sort_values("year")
    result["n_observations"] = len(work)
    if len(work) < MIN_OBSERVATIONS:
        result["status"] = "insufficient_data"
        return result
    x = work["year"].to_numpy(dtype=float)
    y = work[value_column].to_numpy(dtype=float)
    if np.all(y == y[0]):
        result.update(direction="not_significant", significant=False,
                      slope_per_year=0.0, slope_per_decade=0.0,
                      p_value=1.0, kendall_tau=0.0, r_squared=None,
                      status="success")
        return result
    fit = linregress(x, y)
    if mk is not None:
        test = mk.original_test(y)
        p_value, tau = float(test.p), float(test.Tau)
    else:
        # Fallback differs slightly from original Mann-Kendall under ties.
        tau, p_value = (float(z) for z in kendalltau(x, y))
    significant = p_value < ALPHA
    slope = float(fit.slope)
    direction = "not_significant"
    if significant:
        direction = "increasing" if tau > 0 else "decreasing" if tau < 0 else "not_significant"
    result.update(direction=direction, significant=bool(significant),
                  slope_per_year=slope, slope_per_decade=10 * slope,
                  p_value=p_value, kendall_tau=tau,
                  r_squared=float(fit.rvalue ** 2), status="success")
    return result
