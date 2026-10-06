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

# Preserve the frozen Phase-1 fixtures and imported scaffolds. Recompute only the
# cumulative Python baselines and the new Phase-2 generated science surfaces.
python3 -m fvii_lab.cli run --output "$ROOT/formalization/foundations_vii_lab/results"
python3 "$ROOT/scripts/build_fvii_sci02_lab.py"
python3 "$ROOT/scripts/build_fvii_sci02_registry.py"
python3 "$ROOT/scripts/validate_fvii_sci02_lean_static.py"

# The first pass writes the mechanical validation surface consumed by reports;
# the second pass verifies the resulting complete release surface.
python3 "$ROOT/scripts/validate_fvii_sci02.py"
python3 "$ROOT/scripts/build_fvii_sci02_reports.py"
python3 "$ROOT/scripts/validate_fvii_sci02.py"

cleanup
python3 "$ROOT/scripts/build_delivery_manifest.py"
python3 "$ROOT/scripts/verify_delivery_manifest.py"
printf '%s\n' 'FVII-SCI-02 rebuild: PASS'
