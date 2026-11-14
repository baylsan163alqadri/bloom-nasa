# BLOOM NASA Data — Starter Files (not verified observational data)

This package provides Earth Engine extraction code, a Python data loader,
unit tests, and a metadata TEMPLATE. **No NASA observations or study polygons
are included. Never relabel example test fixtures as NASA observations.**

## Workflow
1. Clone https://github.com/heba-mustafa59/bloom-nasa and checkout `feature/nasa-data`.
2. Compare files in this package against your existing `docs/CONTRACT.md` before copying.
3. Copy `scripts/export_nasa_data.js`, `modules/data_loader.py`,
   `tests/test_data_loader.py`, and `data/metadata_TEMPLATE.json` into the repo.
4. Open https://code.earthengine.google.com/ ; draw **real** Polygon imports
   named `areaA` and `areaB` in Jericho; check land-use and boundaries.
5. Paste the export script into Code Editor and press Run. Inspect previews.
6. Start the three tasks in the Earth Engine Tasks tab. Download exported
   `ndvi_annual.csv`, `rainfall_annual.csv`, `study_areas.geojson` from Drive.
7. Inspect `valid_observations > 0` and `valid_months == 12` for all rows.
   Investigate any nulls (do not fill with zero), odd polygons, outliers,
   units, spatial resolution and date coverage.
8. Fill the metadata template using real documented information, save as
   `data/metadata.json` and set `verification_status` to `verified` **only after
   manual checks of the real observations and boundaries**.
9. Run `python -m pip install pandas pytest` and `python -m pytest -q`.
10. Run `python -c "from modules.data_loader import load_datasets; print([len(x) if hasattr(x, '__len__') else type(x) for x in load_datasets()])"`.
11. Commit, push, open PR to main.

## Git commands in VS Code terminal
```bash
git clone https://github.com/heba-mustafa59/bloom-nasa.git
cd bloom-nasa
git switch -c feature/nasa-data
git add scripts/export_nasa_data.js modules/data_loader.py tests/test_data_loader.py data/
git commit -m "Add verified NASA data pipeline and validation"
git push -u origin feature/nasa-data
```
If branch already exists remotely, use `git fetch origin` then
`git switch --track origin/feature/nasa-data` instead of `switch -c`.
Only commit after verifying the actual exports.

## Important methodological caveats
- The annual NDVI in this starter is an **unweighted average of valid
  composite spatial means**, not an area-weighted pixel-time average.
- The rainfall number is a **spatial mean of monthly rates converted to
  calendar-month depths, summed only if 12 valid months exist**.
- NASA MODIS and GPM native resolutions differ radically; do not claim
  sub-kilometre precision for rainfall or infer causation from NDVI alone.
- The Earth Engine script has **not been run on your actual Earth Engine
  account**. Inspect first exports carefully before publishing.
