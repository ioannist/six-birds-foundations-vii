#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

# Set REFRESH_TEXT=1 to rerun latexpand/pandoc for all papers from the frozen source.
# The committed derived text is retained by default so a normal rebuild is fast and deterministic.
if [[ "${REFRESH_TEXT:-0}" == "1" ]]; then
  scripts/extract_plain_text.sh
fi

python scripts/build_plain_fallbacks.py
python scripts/build_step1_inventory.py
python scripts/build_survey_cards.py
python scripts/build_law_registries.py
python scripts/build_core_registries.py
python scripts/build_version_report.py
python scripts/build_wishlist_registry.py
python scripts/build_wishlist_convergence.py
python scripts/build_deep_notes.py
python scripts/build_source_exception_report.py
python scripts/build_step1_metrics.py >/dev/null
python scripts/validate_plan.py > generated/plan_validation.txt
python scripts/validate_step1.py > generated/step1_validation.txt
find . -type d -name __pycache__ -prune -exec rm -rf {} +
python scripts/build_delivery_manifest.py
python scripts/verify_delivery_manifest.py
cat generated/step1_validation.txt
