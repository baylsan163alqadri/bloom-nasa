/**
 * BLOOM — NASA/GEE scientific data export, Jericho, 2005–2024.
 * REQUIRED: Draw two REAL polygons in the Earth Engine Code Editor,
 * and name imports exactly areaA and areaB. Do not invent geometries.
 * The polygon shapes MUST be reviewed for land-use homogeneity.
 * Export CSV files to Google Drive, then add them to data/.
 */

// Imports: areaA (Geometry Polygon), areaB (Geometry Polygon).
// No placeholder polygons are included intentionally.
var areas = ee.FeatureCollection([
  ee.Feature(areaA, {area_id: 'area_a', description: 'Agricultural study area'}),
  ee.Feature(areaB, {area_id: 'area_b', description: 'Comparison study area'})
]);
var years = ee.List.sequence(2005, 2024);
var modisScale = 250;
var gpmScale = 11132;

Map.centerObject(areas, 11);
Map.addLayer(areas, {color: 'yellow'}, 'BLOOM study areas');
print('Study polygons (verify boundaries)', areas);

// MOD13Q1 V6.1: NDVI integer stored with scale factor 0.0001.
// SummaryQA=0 corresponds to 'Good data'.
var modis = ee.ImageCollection('MODIS/061/MOD13Q1')
  .filterDate('2005-01-01', '2025-01-01')
  .select(['NDVI', 'SummaryQA']);

// IMERG Monthly V07 precipitation is an average rate in mm/hour.
var gpm = ee.ImageCollection('NASA/GPM_L3/IMERG_MONTHLY_V07')
  .filterDate('2005-01-01', '2025-01-01')
  .select('precipitation');

function ndviYearArea(year, feature) {
  year = ee.Number(year);
  feature = ee.Feature(feature);
  var roi = feature.geometry();
  var start = ee.Date.fromYMD(year, 1, 1);
  var end = start.advance(1, 'year');
  var subset = modis.filterDate(start, end);
  // Each acceptable composite contributes one spatial mean.
  // Annual NDVI is the arithmetic mean of valid composite means.
  var measurements = ee.FeatureCollection(subset.toList(subset.size()).map(function(item) {
    var image = ee.Image(item);
    var mask = image.select('SummaryQA').eq(0);
    var value = image.select('NDVI').updateMask(mask).multiply(0.0001)
      .reduceRegion({
        reducer: ee.Reducer.mean(),
        geometry: roi,
        scale: modisScale,
        maxPixels: 1e8,
        tileScale: 4
      }).get('NDVI');
    return ee.Feature(null, {ndvi: value});
  })).filter(ee.Filter.notNull(['ndvi']));
  var count = measurements.size();
  return ee.Feature(null, {
    year: year,
    area_id: feature.get('area_id'),
    ndvi: ee.Algorithms.If(count.gt(0), measurements.aggregate_mean('ndvi'), null),
    valid_observations: count
  });
}

function rainYearArea(year, feature) {
  year = ee.Number(year);
  feature = ee.Feature(feature);
  var roi = feature.geometry();
  var start = ee.Date.fromYMD(year, 1, 1);
  var months = ee.List.sequence(1, 12);
  var monthly = ee.FeatureCollection(months.map(function(month) {
    var first = ee.Date.fromYMD(year, month, 1);
    var next = first.advance(1, 'month');
    var collection = gpm.filterDate(first, next);
    // IMERG normally has exactly one image per month. Check completeness.
    var n = collection.size();
    var rate = ee.Image(ee.Algorithms.If(
      n.eq(1), collection.first(), ee.Image.constant(0).rename('precipitation')
    )).select('precipitation');
    var hours = next.difference(first, 'hour');
    var total = rate.multiply(hours).rename('rainfall_mm')
      .reduceRegion({
        reducer: ee.Reducer.mean(),
        geometry: roi,
        scale: gpmScale,
        maxPixels: 1e8,
        tileScale: 4
      }).get('rainfall_mm');
    return ee.Feature(null, {
      rainfall_mm: ee.Algorithms.If(n.eq(1), total, null),
      valid_month: n.eq(1)
    });
  }));
  var good = monthly.filter(ee.Filter.notNull(['rainfall_mm']))
                    .filter(ee.Filter.eq('valid_month', true));
  var count = good.size();
  return ee.Feature(null, {
    year: year,
    area_id: feature.get('area_id'),
    // Never export a partial-year total as a full annual rainfall value.
    rainfall_mm: ee.Algorithms.If(count.eq(12), good.aggregate_sum('rainfall_mm'), null),
    valid_months: count
  });
}

var areaList = areas.toList(areas.size());
var ndviTable = ee.FeatureCollection(years.map(function(y) {
  return ee.FeatureCollection(areaList.map(function(a) {
    return ndviYearArea(y, ee.Feature(a));
  }));
})).flatten();
var rainTable = ee.FeatureCollection(years.map(function(y) {
  return ee.FeatureCollection(areaList.map(function(a) {
    return rainYearArea(y, ee.Feature(a));
  }));
})).flatten();

print('NDVI preview', ndviTable.limit(5));
print('Rainfall preview', rainTable.limit(5));
print('WARNING: NULL values are missing data, not zero. Check valid_months == 12.');

Export.table.toDrive({
  collection: ndviTable,
  description: 'BLOOM_ndvi_annual',
  fileNamePrefix: 'ndvi_annual',
  fileFormat: 'CSV',
  selectors: ['year', 'area_id', 'ndvi', 'valid_observations']
});
Export.table.toDrive({
  collection: rainTable,
  description: 'BLOOM_rainfall_annual',
  fileNamePrefix: 'rainfall_annual',
  fileFormat: 'CSV',
  selectors: ['year', 'area_id', 'rainfall_mm', 'valid_months']
});
Export.table.toDrive({
  collection: areas,
  description: 'BLOOM_study_areas',
  fileNamePrefix: 'study_areas',
  fileFormat: 'GeoJSON'
});
