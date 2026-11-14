
"""Backward-compatible launch path for the premium BLOOM frontend.

Run: python -m streamlit run tests/ui_preview.py
This launches the same seven-page interface as ui_app.py.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui_app import main  # noqa: E402

main()
