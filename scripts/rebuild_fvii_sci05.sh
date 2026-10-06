#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/formalization/foundations_vii_lab"

cleanup() {
  rm -rf "$ROOT/formalization/lean/.lake"
  find "$ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
  find "$ROOT" -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '*.olean' -o -name '*.ilean' \) -delete
}
trap cleanup EXIT
cleanup

# Rebuild all cumulative finite evidence from the retained source and fixtures.
python3 -m fvii_lab.cli run --output "$ROOT/formalization/foundations_vii_lab/results"
python3 "$ROOT/scripts/build_fvii_sci02_lab.py"
python3 "$ROOT/scripts/build_fvii_sci03_lab.py"
python3 "$ROOT/scripts/build_fvii_sci04_lab.py"
python3 "$ROOT/scripts/build_fvii_sci05_lab.py"
python3 -m unittest discover -s "$ROOT/formalization/foundations_vii_lab/tests" -p 'test*.py' -v

# Rebuild the complete source, theorem, dependency, trust, closure, and finite registries.
python3 "$ROOT/scripts/build_fvii_sci05_registry.py"
python3 "$ROOT/scripts/validate_fvii_sci05_lean_static.py"

# The first report pass creates the complete advertised release surface.  The
# validator writes the canonical JSON/text receipt; the second report pass
# renders that receipt into the human-readable report without rerunning the
# already-completed 70-test acceptance suite.
python3 "$ROOT/scripts/build_fvii_sci05_reports.py"
python3 "$ROOT/scripts/validate_fvii_sci05.py"
python3 "$ROOT/scripts/build_fvii_sci05_reports.py"

# Earlier phase validators intentionally are not replayed because their stage
# boundary checks reject the later final-release directories.  The final
# validator checks inherited scaffold and paper-source immutability against tag
# vii-science-04.
cleanup
python3 "$ROOT/scripts/build_delivery_manifest.py"
python3 "$ROOT/scripts/verify_delivery_manifest.py"
printf '%s\n' 'FVII-SCI-05 final science rebuild: PASS'
