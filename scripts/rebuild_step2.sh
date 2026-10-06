#!/usr/bin/env bash
# Deterministically rebuild the Step-2 claim corpus and bridge atlas from the
# frozen, validated Step-1 source and formalization spine.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

# The default path intentionally does not replay the expensive prior finite
# labs or the Step-1 validators that reject the presence of Step-2 products.
# The retained Step-1/formalization imports have their own historical rebuild
# scripts and byte-identity manifests.  REFRESH_TEXT=1 may be used when the
# TeX host tools are available and a full source-expansion replay is desired.
if [[ "${REFRESH_TEXT:-0}" == "1" ]]; then
  scripts/extract_plain_text.sh
  python scripts/build_plain_fallbacks.py
fi

python scripts/build_step2_claims.py
python scripts/build_step2_claim_bridge_atlas.py
python scripts/build_step2_reports.py

mkdir -p generated
python scripts/validate_plan.py > generated/plan_validation.txt
# The prior formal-spine validators and their recorded test baselines are
# retained from Step 1.  They include intentionally expensive finite-test
# replays, so the default Step-2 rebuild does not rerun them.  Set
# REVALIDATE_PRIOR=1 to request those historical gates explicitly.
if [[ "${REVALIDATE_PRIOR:-0}" == "1" ]]; then
  python scripts/validate_formalization_scaffold.py > generated/formalization_validation.txt
  python scripts/validate_foundations_v_integration.py > generated/foundations_v_validation.txt
fi
python scripts/validate_step2.py > generated/step2_validation.txt

find . -type d \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} +
find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
python scripts/build_delivery_manifest.py
python scripts/verify_delivery_manifest.py

cat generated/step2_validation.txt
