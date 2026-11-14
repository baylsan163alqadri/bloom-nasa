
"""Additional UI-data boundary tests (no satellite values needed)."""

import pytest
import sys

from types import ModuleType

from modules.ui_data import (
    synthetic_demo,
    load_ui_context
)


def test_synthetic_data_are_explicitly_demo():
    ctx = load_ui_context(
        "demo",
        "area_a",
        2005,
        2024
    )

    assert ctx.is_demo

    assert (
        ctx.metadata["verification_status"]
        == "synthetic_demo"
    )

    assert len(ctx.ndvi_df) == 40
    assert len(ctx.rainfall_df) == 40
    assert ctx.geojson == {}


def test_demo_values_are_valid():
    nd, rain = synthetic_demo()

    assert nd["ndvi"].between(-1, 1).all()
    assert (rain["rainfall_mm"] >= 0).all()

    assert not nd.duplicated(
        ["year", "area_id"]
    ).any()


def test_year_filter_only_affects_display():
    ctx = load_ui_context(
        "demo",
        "area_b",
        2018,
        2021
    )

    assert ctx.area_data("ndvi")[
        "year"
    ].tolist() == [
        2018,
        2019,
        2020,
        2021
    ]

    assert len(
        ctx.area_data(
            "ndvi",
            full_period=True
        )
    ) == 20


def test_real_mode_never_switches_to_synthetic(
    tmp_path,
    monkeypatch
):
    fake = ModuleType(
        "modules.data_loader"
    )

    def unavailable(data_dir=None):
        raise FileNotFoundError(
            "Missing NASA data exports: ndvi_annual.csv"
        )

    fake.load_datasets = unavailable

    monkeypatch.setitem(
        sys.modules,
        "modules.data_loader",
        fake
    )

    ctx = load_ui_context(
        "verified",
        "area_a",
        2005,
        2024,
        data_dir=tmp_path
    )

    assert not ctx.ready
    assert not ctx.is_demo

    assert "Missing NASA data exports" in (
        ctx.error or ""
    )


def test_unknown_source_is_rejected():
    with pytest.raises(ValueError):
        load_ui_context(
            "fake-real",
            "area_a",
            2005,
            2024
        )
