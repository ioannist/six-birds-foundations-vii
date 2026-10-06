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

# Rebuild the cumulative finite evidence baselines.  Earlier phase sources and
# fixtures are retained byte-for-byte; each generator is deterministic.
python3 -m fvii_lab.cli run --output "$ROOT/formalization/foundations_vii_lab/results"
python3 "$ROOT/scripts/build_fvii_sci02_lab.py"
python3 "$ROOT/scripts/build_fvii_sci03_lab.py"
python3 "$ROOT/scripts/build_fvii_sci04_lab.py"
python3 "$ROOT/scripts/build_fvii_sci04_registry.py"
python3 "$ROOT/scripts/validate_fvii_sci04_lean_static.py"

# The first acceptance pass writes the machine-readable validation surface
# consumed by the reports.  The second verifies the completed report surface.
python3 "$ROOT/scripts/validate_fvii_sci04.py"
python3 "$ROOT/scripts/build_fvii_sci04_reports.py"
python3 "$ROOT/scripts/validate_fvii_sci04.py"

# Historical validators intentionally are not replayed because their
# stage-boundary checks reject later-phase implementation directories.  The
# controlling Phase-4 validator checks prior sources and imported scaffolds for
# immutability against tag vii-science-03.
cleanup
python3 "$ROOT/scripts/build_delivery_manifest.py"
python3 "$ROOT/scripts/verify_delivery_manifest.py"
printf '%s\n' 'FVII-SCI-04 rebuild: PASS'
