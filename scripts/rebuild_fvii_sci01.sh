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

python3 "$ROOT/scripts/build_fvii_sci01_fixtures.py"
python3 "$ROOT/scripts/build_fvii_sci01_lean_fixtures.py"
python3 "$ROOT/scripts/build_fvii_sci01_adapters.py"
python3 "$ROOT/scripts/build_fvii_sci01_registry.py"
python3 -m fvii_lab.cli run --output "$ROOT/formalization/foundations_vii_lab/results"

# First acceptance pass creates the machine-readable validation surface consumed
# by the human-readable report builder.  The second pass verifies the resulting
# complete Phase-1 surface.
python3 "$ROOT/scripts/validate_fvii_sci01.py"
python3 "$ROOT/scripts/build_fvii_sci01_reports.py"
python3 "$ROOT/scripts/validate_fvii_sci01.py"

# Historical planning/readiness validators intentionally are not replayed here:
# several of their exit conditions assert that no Foundations VII implementation
# exists.  Their committed reports remain the audit record for their own tagged
# stages.  Phase 1 instead verifies imported-scaffold immutability, source-corpus
# non-modification, no-paper-work, and later-phase nonexecution inside the
# controlling FVII-SCI-01 validator above.

cleanup
python3 "$ROOT/scripts/build_delivery_manifest.py"
python3 "$ROOT/scripts/verify_delivery_manifest.py"
printf '%s\n' 'FVII-SCI-01 rebuild: PASS'
