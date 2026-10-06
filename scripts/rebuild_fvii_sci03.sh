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

# Rebuild the cumulative finite evidence baselines without changing the frozen
# Phase-1 fixtures, imported Foundations I–VI scaffolds, or Phase-2 theorem
# sources.  Phase-3 generation is deterministic from those retained inputs.
python3 -m fvii_lab.cli run --output "$ROOT/formalization/foundations_vii_lab/results"
python3 "$ROOT/scripts/build_fvii_sci02_lab.py"
python3 "$ROOT/scripts/build_fvii_sci03_lab.py"
python3 "$ROOT/scripts/build_fvii_sci03_registry.py"
python3 "$ROOT/scripts/validate_fvii_sci03_lean_static.py"

# The first acceptance pass writes the validation surface consumed by the
# report builder.  The second pass verifies the completed release surface.
python3 "$ROOT/scripts/validate_fvii_sci03.py"
python3 "$ROOT/scripts/build_fvii_sci03_reports.py"
python3 "$ROOT/scripts/validate_fvii_sci03.py"

# Historical Phase-1/2 validators intentionally are not replayed here because
# their stage-boundary checks reject later-phase implementation directories.
# The controlling Phase-3 validator instead checks those prior sources and
# inherited scaffolds for byte-level immutability against tag vii-science-02.

cleanup
python3 "$ROOT/scripts/build_delivery_manifest.py"
python3 "$ROOT/scripts/verify_delivery_manifest.py"
printf '%s\n' 'FVII-SCI-03 rebuild: PASS'
