
/**
 * BLOOM — NASA Earth Engine exports for Jericho, 2005–2024.
 * IMPORTANT: Keep the existing imported `areaA` MultiPolygon (2 polygons).
 * Polygon 0 (right/east on map) = area_a; polygon 1 (left/west) = area_b.
 * Confirm this order visually before exporting.
 */

// 1. Separate the two *real, drawn* polygons in imported areaA.
var polygons = ee.List(areaA.coordinates());
var studyA = ee.Geometry.Polygon(polygons.get(0));
var studyB = ee.Geometry.Polygon(polygons.get(1));

// 2. Stable IDs shared by map, CSV files, and statistical analysis.
var areas = ee.FeatureCollection([
  ee.Feature(studyA, {
    area_id: 'area_a',
    description: 'Agricultural study area'
  }),
  ee.Feature(studyB, {
    area_id: 'area_b',
    description: 'Mixed agricultural comparison area'
  })
]);

var years = ee.List.sequence(2005, 2024);
var modisScale = 250;
var gpmScale = 11132;

Map.centerObject(areas, 12);
Map.addLayer(studyA, {color: '00FF00'}, 'Area A (green)');
Map.addLayer(studyB, {color: '0000FF'}, 'Area B (blue)');
print('Polygon count (must be 2):', polygons.size());
print('Study areas:', areas);

// 3. NASA MODIS NDVI, 16-day observations, 250 m.
// Only use SummaryQA == 0 (high-quality pixels).
var modis = ee.ImageCollection('MODIS/061/MOD13Q1')
  .filterDate('2005-01-01', '2025-01-01')
  .filterBounds(areas.geometry())
  .select(['NDVI', 'SummaryQA']);

// 4. NASA GPM IMERG Monthly V07: monthly mean rate in mm/hour.
var gpm = ee.ImageCollection('NASA/GPM_L3/IMERG_MONTHLY_V07')
  .filterDate('2005-01-01', '2025-01-01')
  .filterBounds(areas.geometry())
  .select('precipitation');

function ndviYearArea(year, feature) {
  year = ee.Number(year);
  feature = ee.Feature(feature);
  var start = ee.Date.fromYMD(year, 1, 1);
  var end = start.advance(1, 'year');
  var subset = modis.filterDate(start, end);

  var measurements = ee.FeatureCollection(
    subset.toList(subset.size()).map(function(item) {
      var image = ee.Image(item);
      var good = image.select('SummaryQA').eq(0);
      var mean = image.select('NDVI')
        .multiply(0.0001)
        .updateMask(good)
        .reduceRegion({
          reducer: ee.Reducer.mean(),
          geometry: feature.geometry(),
          scale: modisScale,
          maxPixels: 1e8,
          tileScale: 4
        }).get('NDVI');
      return ee.Feature(null, {ndvi: mean});
    })
  ).filter(ee.Filter.notNull(['ndvi']));

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
  var months = ee.List.sequence(1, 12);

  var monthly = ee.FeatureCollection(months.map(function(month) {
    var first = ee.Date.fromYMD(year, month, 1);
    var next = first.advance(1, 'month');
    var images = gpm.filterDate(first, next);
    var imageCount = images.size();

    // The zero image is ONLY an internal computation fallback.
    // The month's output is NULL unless there is exactly one image.
    var precipitationRate = ee.Image(ee.Algorithms.If(
      imageCount.eq(1),
      images.first(),
      ee.Image.constant(0).rename('precipitation')
    ));

    var hours = next.difference(first, 'hour');
    var mm = precipitationRate.select('precipitation')
      .multiply(hours)
      .rename('rainfall_mm')
      .reduceRegion({
        reducer: ee.Reducer.mean(),
        geometry: feature.geometry(),
        scale: gpmScale,
        maxPixels: 1e8,
        tileScale: 4
      }).get('rainfall_mm');

    return ee.Feature(null, {
      rainfall_mm: ee.Algorithms.If(imageCount.eq(1), mm, null)
    });
  }));

  var valid = monthly.filter(ee.Filter.notNull(['rainfall_mm']));
  var validMonths = valid.size();
  return ee.Feature(null, {
    year: year,
    area_id: feature.get('area_id'),
    rainfall_mm: ee.Algorithms.If(
      validMonths.eq(12), valid.aggregate_sum('rainfall_mm'), null
    ),
    valid_months: validMonths
  });
}

// 5. Annual time series for each of the two study areas.
var areaList = areas.toList(areas.size());
var ndviTable = ee.FeatureCollection(years.map(function(year) {
  return ee.FeatureCollection(areaList.map(function(area) {
    return ndviYearArea(year, ee.Feature(area));
  }));
})).flatten();

var rainfallTable = ee.FeatureCollection(years.map(function(year) {
  return ee.FeatureCollection(areaList.map(function(area) {
    return rainYearArea(year, ee.Feature(area));
  }));
})).flatten();

print('NDVI preview (check numbers):', ndviTable.limit(5));
print('Rainfall preview (check numbers):', rainfallTable.limit(5));
print('Missing values remain NULL, not zero. Annual rain requires 12 valid months.');

// 6. Start all three exports manually in the Tasks panel.
Export.table.toDrive({
  collection: ndviTable,
  description: 'BLOOM_ndvi_annual',
  fileNamePrefix: 'ndvi_annual',
  fileFormat: 'CSV',
  selectors: ['year', 'area_id', 'ndvi', 'valid_observations']
});

Export.table.toDrive({
  collection: rainfallTable,
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
