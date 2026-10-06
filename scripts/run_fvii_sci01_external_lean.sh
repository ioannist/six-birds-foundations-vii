#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEAN_DIR="$ROOT/formalization/lean"
LAB_DIR="$ROOT/formalization/foundations_vii_lab"
RESULTS="$LAB_DIR/results"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$RESULTS"

for command_name in lean lake python3; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    echo "Install/select a Lean 4 toolchain, or edit formalization/lean/lean-toolchain to an available compatible version and record that change." >&2
    exit 2
  fi
done

lean_version="$(lean --version | head -n 1)"
lake_version="$(lake --version | head -n 1)"
toolchain="$(tr -d '\r\n' < "$LEAN_DIR/lean-toolchain")"
elan_available=false
if command -v elan >/dev/null 2>&1; then
  elan_available=true
fi
printf 'Toolchain file: %s\nLean: %s\nLake: %s\nElan available: %s\n' \
  "$toolchain" "$lean_version" "$lake_version" "$elan_available"

# Recompute the independent Python baseline before the Lean replay.
PYTHONPATH="$LAB_DIR" python3 -m fvii_lab.cli run --output "$RESULTS"

(
  cd "$LEAN_DIR"
  lake clean
  lake build
  lake exe fvii_reference_world > "$RESULTS/lean_results.jsonl"
  lake env lean FoundationsVII/Trust/PrintAxioms.lean > "$RESULTS/lean_axioms.txt" 2>&1
)

PYTHONPATH="$LAB_DIR" python3 -m fvii_lab.cli compare \
  "$RESULTS/lean_results.jsonl" \
  --output "$RESULTS/cross_implementation.json"

python3 - "$ROOT" "$toolchain" "$lean_version" "$lake_version" "$elan_available" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
toolchain, lean_version, lake_version, elan_available_text = sys.argv[2:6]
elan_available = elan_available_text.lower() == "true"
results = root / "formalization" / "foundations_vii_lab" / "results"
lean_dir = root / "formalization" / "lean"
cross = json.loads((results / "cross_implementation.json").read_text(encoding="utf-8"))
rows = [line for line in (results / "lean_results.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
if not (
    cross.get("all_pass") is True
    and len(rows) == 51
    and not cross.get("missing_from_lean")
    and not cross.get("missing_from_python")
    and not cross.get("mismatches")
    and (results / "lean_axioms.txt").stat().st_size > 0
):
    raise SystemExit(f"Lean/Python replay did not close: rows={len(rows)} cross={cross}")

def dump(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

dump(results / "lean_execution_status.json", {
    "authorization": "EXTERNAL_REPLAY_EXECUTED",
    "blocking": False,
    "phase": "FVII-SCI-01",
    "reason": "Lean kernel build, generated axiom replay, and 51-case differential replay passed.",
    "status": "LEAN_BUILD_AND_DIFFERENTIAL_REPLAY_PASS",
    "toolchain": toolchain,
    "lean_version": lean_version,
    "lake_version": lake_version,
})
dump(results / "cross_implementation_status.json", {
    "phase": "FVII-SCI-01",
    "status": "PASS",
    "python_runtime_rows": 51,
    "lean_runtime_rows": 51,
    "shared_fixture_rows": 51,
    "warning": "Finite agreement over the frozen 51-case family is not a universal theorem.",
})
dump(lean_dir / "BUILD_STATUS.json", {
    "build_command": "cd formalization/lean && lake clean && lake build",
    "cross_implementation_status": "PASS_51_OF_51",
    "elan_available": elan_available,
    "external_directions": "formalization/lean/EXTERNAL_COMPILE.md",
    "kernel_build_status": "PASS",
    "lake_available": True,
    "lake_version": lake_version,
    "lean_available": True,
    "lean_version": lean_version,
    "reason": "External replay completed the kernel build, 51-case differential comparison, and #print axioms capture.",
    "toolchain": toolchain,
})
PY

# Generated registries become kernel-aware only after the replay status is recorded.
python3 "$ROOT/scripts/build_fvii_sci01_registry.py"

# Build caches are execution transients and are not retained in phase archives.
rm -rf "$LEAN_DIR/.lake"
find "$ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$ROOT" -type f -name '*.pyc' -delete

python3 "$ROOT/scripts/validate_fvii_sci01.py" --require-lean-results
python3 "$ROOT/scripts/build_fvii_sci01_reports.py"
python3 "$ROOT/scripts/validate_fvii_sci01.py" --require-lean-results
python3 "$ROOT/scripts/build_delivery_manifest.py"
python3 "$ROOT/scripts/verify_delivery_manifest.py"

echo "FVII-SCI-01 external Lean replay: PASS"
