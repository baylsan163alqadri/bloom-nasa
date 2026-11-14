# BLOOM — Task ownership after Phase 1

## Team member 1: Data & GIS — `feature/nasa-data`
Own: `scripts/export_nasa_data.js`, `data/`, `modules/data_loader.py`, `tests/test_data_loader.py`.
Deliver: two documented real study polygons around Jericho; annual QA-filtered NASA MODIS NDVI; annual NASA GPM rainfall converted to mm/year; metadata. Ensure actual geography and provenance, avoid unverified coordinate guesses.

## Team member 2: Trend & Mystery — `feature/statistics`
Own: `modules/trend_analysis.py`, `modules/mystery_engine.py`, `tests/test_trends.py`, `tests/test_mystery.py`.
Deliver: slope per year/decade, Mann–Kendall p-value and honest direction, enough-data validation, rainfall-based model with chronological holdout and error metrics, explainable residual flagging, inconclusive mode.

## Team member 3: User Interface — `feature/ui`
Own: `modules/map_view.py`, `modules/dashboard.py`, assets.
Deliver: Streamlit case selection, GeoJSON map, NDVI/rainfall charts, metric summaries, empty/error states; no hard-coded study findings.

## Team member 4: Integration & Presentation — `feature/integration`
Own: `app.py`, `modules/report_generator.py`, `requirements.txt`, `README.md`, integration tests, deployment and demo.
Deliver: unify imports/parameters, enforce area/date selection, report downloads, verify maths on real data, Streamlit Cloud deployment, brief demo video.

## Merge acceptance checklist
1. Feature branch builds and tests pass.
2. Export file or module uses docs/CONTRACT.md names unchanged.
3. No fake NASA measurements or unexplained claims.
4. Pull request is reviewed by integrator before merge.
5. Main branch is runnable after each merge.

## Phase 1 completion
- Repository created and shared
- This skeleton uploaded to `main`
- Each teammate knows ownership/branch
- `streamlit run app.py` starts successfully
