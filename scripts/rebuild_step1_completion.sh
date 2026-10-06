#!/usr/bin/env bash
# Rebuild the cumulative formalization-aware Step-1 repository from frozen inputs.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

# Set REFRESH_TEXT=1 to rerun latexpand/pandoc from the frozen source.  The
# committed derived text is used by default for a fast deterministic rebuild.
if [[ "${REFRESH_TEXT:-0}" == "1" ]]; then
  scripts/extract_plain_text.sh
fi

# Original Step-1 corpus and semantic products.
python scripts/build_plain_fallbacks.py
python scripts/build_step1_inventory.py
python scripts/build_paper_dependency_reconnaissance.py >/dev/null
python scripts/build_survey_cards.py
python scripts/build_law_registries.py
python scripts/build_core_registries.py
python scripts/build_version_report.py
python scripts/build_version_line_delta.py >/dev/null
python scripts/build_wishlist_registry.py
python scripts/build_wishlist_convergence.py
python scripts/build_deep_notes.py
python scripts/build_source_exception_report.py
python scripts/build_step1_metrics.py >/dev/null

# Prior-proof scaffolds.  Both frozen source archives are retained in the
# cumulative repository; active imported subtrees are rebuilt byte-for-byte.
python scripts/import_foundations_vi_scaffold.py
python scripts/import_foundations_v_scaffold.py
python scripts/build_formalization_indexes.py >/dev/null

# Post-integration Step-1 reconciliation.  The paper-side pass establishes the
# grade/fidelity vocabulary; the Foundations V pass then indexes the complete
# D/E theorem base and repairs only its upstream E16 root/manifest omissions in
# VII-owned adapters.
python scripts/build_step1_formal_completion.py >/dev/null
python scripts/build_foundations_v_integration.py >/dev/null
python scripts/run_formalization_baseline.py

# Cumulative gates.  The completion validators also reject accidental Step-2
# records or Foundations VII declarations.
python scripts/validate_plan.py > generated/plan_validation.txt
python scripts/validate_step1.py > generated/step1_validation.txt
python scripts/validate_formalization_scaffold.py > generated/formalization_validation.txt
python scripts/validate_foundations_v_integration.py > generated/foundations_v_validation.txt
python scripts/validate_step1_completion.py > generated/step1_completion_validation.txt

find . -type d \( -name __pycache__ -o -name .pytest_cache \) -prune -exec rm -rf {} +
python scripts/build_delivery_manifest.py
python scripts/verify_delivery_manifest.py

cat generated/step1_completion_validation.txt
