#!/usr/bin/env bash
# Deterministically rebuild the Step-3 Foundations VII readiness dossier from
# the frozen Step-2 claim/bridge body and inherited Foundations I–VI scaffold.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

python scripts/build_step3_readiness.py
python scripts/step3_reference_model.py
python scripts/validate_step3.py

find . -type d \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} +
find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
