"""BLOOM Jericho Map — interactive visualization of real study polygons.

Stable integration contract:
    render_map(study_areas: dict, selected_area_id: str) -> None

Extra optional keyword parameters support verified NASA annual observations.
Reference place markers are NOT area boundaries and do NOT assign area IDs.
"""
from __future__ import annotations

from html import escape
from math import isfinite
from typing import Any

import folium
from folium.plugins import Draw, Fullscreen, MeasureControl, MiniMap, MousePosition, Search

AREA_NAMES = {"area_a": "Area A — Study polygon", "area_b": "Area B — Study polygon"}
# Independent reference sites. Never equate these to area_a/area_b without verified geometry.
REFERENCE_SITES = {
    "tell_sultan": {
        "name": "Tell es-Sultan | تل السلطان", "lat": 31.8713056, "lon": 35.4440556,
        "source": "UNESCO World Heritage Centre", "url": "https://whc.unesco.org/en/list/1687",
    },
    "al_auja": {
        "name": "Al-Auja | العوجا", "lat": 31.95069, "lon": 35.46756,
        "source": "GeoNames", "url": "https://www.geonames.org/285112/al-awja.html",
    },
}
COLORS = {"forest": "#163D2E", "leaf": "#4C8B63", "amber": "#D99A56"}
BASEMAPS = ("Streets", "Satellite")
MODES = ("Boundaries", "Annual NDVI")


def _coord(value: Any) -> tuple[float, float] | None:
    """Convert one [longitude, latitude] coordinate into (latitude, longitude)."""
    if not isinstance(value, (list, tuple)) or len(value) < 2:
        return None
    lon, lat = value[:2]
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in (lon, lat)):
        return None
    if not all(map(isfinite, (lon, lat))) or not (-180 <= lon <= 180 and -90 <= lat <= 90):
        return None
    return (float(lat), float(lon))


def _polygon_points(geometry: Any) -> list[tuple[float, float]] | None:
    """Check coordinate structure. This is NOT a provenance/topology certification."""
    if not isinstance(geometry, dict):
        return None
    kind, coords = geometry.get("type"), geometry.get("coordinates")
    if kind == "Polygon":
        polygons = [coords]
    elif kind == "MultiPolygon":
        polygons = coords
    else:
        return None
    if not isinstance(polygons, list) or not polygons:
        return None
    result = []
    for polygon in polygons:
        if not isinstance(polygon, list) or not polygon:
            return None
        for ring in polygon:
            if not isinstance(ring, list) or len(ring) < 4:
                return None
            converted = [_coord(p) for p in ring]
            if any(p is None for p in converted):
                return None
            if converted[0] != converted[-1] or len(set(converted[:-1])) < 3:
                return None
            # Review envelope around Jericho; catches accidental far-away polygons.
            if any(not (31.6 <= lat <= 32.2 and 35.2 <= lon <= 35.75)
                   for lat, lon in converted):
                return None
            result.extend(converted)
    return result


def _valid_features(geojson: Any) -> list[dict]:
    if not isinstance(geojson, dict) or geojson.get("type") != "FeatureCollection":
        return []
    features = geojson.get("features")
    if not isinstance(features, list):
        return []
    result, seen = [], set()
    for feature in features:
        if not isinstance(feature, dict) or feature.get("type") != "Feature":
            continue
        props = feature.get("properties")
        if not isinstance(props, dict):
            continue
        area_id = props.get("area_id")
        geom = feature.get("geometry")
        if area_id not in AREA_NAMES or area_id in seen or _polygon_points(geom) is None:
            continue
