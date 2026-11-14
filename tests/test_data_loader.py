from modules.data_loader import load_datasets

def test_data_loader_signature():
    ndvi, rainfall, areas, metadata = load_datasets()
    assert list(ndvi.columns) == ["year", "area_id", "ndvi", "valid_observations"] or {"year", "area_id", "ndvi"}.issubset(ndvi.columns)
    assert {"year", "area_id", "rainfall_mm"}.issubset(rainfall.columns)
    assert areas.get("type") == "FeatureCollection"
    assert isinstance(metadata, dict)
