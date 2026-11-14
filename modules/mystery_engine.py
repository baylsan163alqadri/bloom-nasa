
"""BLOOM rainfall-based exploratory vegetation anomaly detector.

Chronological holdout: 2005-2018 train, 2019-2024 validation if available.
Gate: validation R² > 0 and MAE < training-mean baseline MAE, with at
least 10 training and 3 validation observations. Outlier threshold: absolute
residual > 2 * training residual sample SD; an exploratory flag only.
No inference of irrigation, causality, or source-data accuracy is made.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from .trend_analysis import analyze_trend


def _prepare(df, area_id, field):
    required = {"year", "area_id", field}
    if not isinstance(df, pd.DataFrame) or not required.issubset(df.columns):
        raise ValueError(f"expected DataFrame containing {sorted(required)}")
    selected = df.loc[df["area_id"] == area_id, ["year", "area_id", field]].copy()
    if selected.empty:
        return selected
    years = pd.to_numeric(selected["year"], errors="coerce")
    if years.isna().any() or not np.isfinite(years.to_numpy(dtype=float)).all() or (years % 1 != 0).any():
        raise ValueError("years must be integers")
    selected["year"] = years.astype(int)
    if selected["year"].duplicated().any():
        raise ValueError("duplicate years for area")
    vals = pd.to_numeric(selected[field], errors="coerce")
    if (selected[field].notna() & vals.isna()).any() or np.isinf(vals.to_numpy(dtype=float)).any():
        raise ValueError("invalid measurement")
    if field == "ndvi" and ((vals < -1) | (vals > 1)).any():
        raise ValueError("invalid NDVI range")
    if field == "rainfall_mm" and (vals < 0).any():
        raise ValueError("negative rainfall")
    selected[field] = vals
    return selected


def analyze_mystery(ndvi_df, rainfall_df, area_id: str) -> dict:
    """Return MysteryResult envelope with validation and guarded anomalies."""
    result = {
        "area_id": area_id,
        "model_status": "insufficient_evidence",
        "validation_r2": None,
        "validation_mae": None,
        "anomalies": [],
        "opposing_trends": None,
        "verdict": "Insufficient evidence",
        "limitations": [
            "Rainfall alone does not explain vegetation; association does not establish causation.",
            "GPM precipitation pixels may be much coarser than MODIS vegetation pixels."
        ],
    }
    if not isinstance(area_id, str) or not area_id.strip():
        raise ValueError("area_id must be a nonempty string")
    nd = _prepare(ndvi_df, area_id, "ndvi")
    rain = _prepare(rainfall_df, area_id, "rainfall_mm")
    if len(nd) == 0 or len(rain) == 0:
        result["limitations"].append("Area has no NDVI or rainfall observations.")
        return result

    nd_trend = analyze_trend(nd, "ndvi", 2005, 2024)
    rain_trend = analyze_trend(rain, "rainfall_mm", 2005, 2024)
    if nd_trend["significant"] and rain_trend["significant"]:
        result["opposing_trends"] = (nd_trend["direction"] != rain_trend["direction"])

    joined = nd[["year", "ndvi"]].merge(
        rain[["year", "rainfall_mm"]],
        on="year",
        how="inner",
        validate="one_to_one"
    )
    joined = joined.loc[joined["year"].between(2005, 2024)].dropna().sort_values("year")
    train = joined.loc[joined["year"] <= 2018]
    test = joined.loc[joined["year"] >= 2019]

    if len(train) < 10 or len(test) < 3:
        result["limitations"].append(
            "Need >=10 paired training years before 2019 and >=3 paired validation years from 2019 onward."
        )
        return result
    if train["rainfall_mm"].nunique() < 2:
        result["limitations"].append("Rainfall has no training variation.")
        return result

    model = LinearRegression().fit(train[["rainfall_mm"]], train["ndvi"])
    predicted = model.predict(test[["rainfall_mm"]])
    mae = float(mean_absolute_error(test["ndvi"], predicted))
    r2 = float(r2_score(test["ndvi"], predicted))
    baseline = float(mean_absolute_error(
        test["ndvi"],
        np.repeat(train["ndvi"].mean(), len(test))
    ))
    result["validation_mae"] = mae
    result["validation_r2"] = r2 if np.isfinite(r2) else None

    if not np.isfinite(r2) or r2 <= 0 or mae >= baseline:
        result["limitations"].append(
            "Model failed validation gate: R² > 0 and MAE below training-mean baseline MAE."
        )
        return result

    residual_train = train["ndvi"].to_numpy() - model.predict(train[["rainfall_mm"]])
    sd = float(np.std(residual_train, ddof=1))
    if not np.isfinite(sd) or sd <= 1e-12:
        result["limitations"].append(
            "Training residual variance is too small for a defensible anomaly threshold."
        )
        return result

    result["model_status"] = "validated"
    result["verdict"] = (
        "Exploratory model validated; flagged deviations require further investigation."
    )
    result["limitations"].append(
        "Anomalies are validation-period residuals exceeding 2 training residual standard deviations; exploratory, not causal."
    )

    for year, observed, expected in zip(test["year"], test["ndvi"], predicted):
        residual = float(observed - expected)
        if abs(residual) > 2 * sd:
            result["anomalies"].append({
                "year": int(year),
                "observed_ndvi": float(observed),
                "expected_ndvi": float(expected),
                "residual": residual,
                "type": (
                    "unexpected_greening"
                    if residual > 0
                    else "unexpected_browning"
                )
            })
    return result
