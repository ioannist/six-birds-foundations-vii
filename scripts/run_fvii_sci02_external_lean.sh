#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEAN_DIR="$ROOT/formalization/lean"
LAB_DIR="$ROOT/formalization/foundations_vii_lab"
RESULTS1="$LAB_DIR/results"
RESULTS2="$LAB_DIR/phase2/results"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$LAB_DIR"
mkdir -p "$RESULTS1" "$RESULTS2"

for command_name in lean lake python3; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    echo "Install/select a compatible Lean 4 toolchain, or edit formalization/lean/lean-toolchain and record the change in Git." >&2
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

# Recompute both independent Python baselines before Lean execution.
python3 -m fvii_lab.cli run --output "$RESULTS1"
python3 "$ROOT/scripts/build_fvii_sci02_lab.py"

(
  cd "$LEAN_DIR"
  lake clean
  lake build
  lake exe fvii_reference_world > "$RESULTS1/lean_results.jsonl"
  lake exe fvii_phase2_envelopes > "$RESULTS2/lean_envelopes.jsonl"
  lake env lean FoundationsVII/Trust/PrintAxioms.lean > "$RESULTS1/lean_axioms.txt" 2>&1
  lake env lean FoundationsVII/Trust/PrintAxiomsPhase2.lean > "$RESULTS2/lean_axioms.txt" 2>&1
)

python3 -m fvii_lab.cli compare \
  "$RESULTS1/lean_results.jsonl" \
  --output "$RESULTS1/cross_implementation.json"

python3 - "$RESULTS2/envelopes.jsonl" "$RESULTS2/lean_envelopes.jsonl" "$RESULTS2/cross_implementation.json" <<'PY'
import json
import sys
from pathlib import Path

python_path, lean_path, output_path = map(Path, sys.argv[1:4])
python_rows = {
    row["family_id"]: row
    for row in (json.loads(line) for line in python_path.read_text(encoding="utf-8").splitlines() if line.strip())
}
lean_rows = {
    row["family_id"]: row
    for row in (json.loads(line) for line in lean_path.read_text(encoding="utf-8").splitlines() if line.strip())
}
fields = (
    "raw_cardinality",
    "canonical_cardinality",
    "accepted_cardinality",
    "rejected_cardinality",
)
missing_from_lean = sorted(set(python_rows) - set(lean_rows))
missing_from_python = sorted(set(lean_rows) - set(python_rows))
mismatches = []
for family_id in sorted(set(python_rows) & set(lean_rows)):
    differing = {
        field: {"python": python_rows[family_id].get(field), "lean": lean_rows[family_id].get(field)}
        for field in fields
        if python_rows[family_id].get(field) != lean_rows[family_id].get(field)
    }
    if differing:
        mismatches.append({"family_id": family_id, "fields": differing})
payload = {
    "all_pass": not missing_from_lean and not missing_from_python and not mismatches,
    "phase": "FVII-SCI-02",
    "python_rows": len(python_rows),
    "lean_rows": len(lean_rows),
    "missing_from_lean": missing_from_lean,
    "missing_from_python": missing_from_python,
    "mismatches": mismatches,
    "fields_compared": list(fields),
    "warning": "Agreement is exhaustive only over the nine declared bounded families; it is not a universal theorem.",
}
output_path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
if not payload["all_pass"]:
    raise SystemExit(f"Phase-2 Lean/Python differential failed: {payload}")
PY

python3 - "$ROOT" "$toolchain" "$lean_version" "$lake_version" "$elan_available" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
toolchain, lean_version, lake_version, elan_available_text = sys.argv[2:6]
elan_available = elan_available_text.lower() == "true"
lab = root / "formalization" / "foundations_vii_lab"
results1 = lab / "results"
results2 = lab / "phase2" / "results"
lean_dir = root / "formalization" / "lean"

cross1 = json.loads((results1 / "cross_implementation.json").read_text(encoding="utf-8"))
cross2 = json.loads((results2 / "cross_implementation.json").read_text(encoding="utf-8"))
rows1 = [line for line in (results1 / "lean_results.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
rows2 = [line for line in (results2 / "lean_envelopes.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
if not (
    cross1.get("all_pass") is True
    and cross2.get("all_pass") is True
    and len(rows1) == 51
    and len(rows2) == 9
    and (results1 / "lean_axioms.txt").stat().st_size > 0
    and (results2 / "lean_axioms.txt").stat().st_size > 0
):
    raise SystemExit("Cumulative Lean replay did not close")

def dump(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

dump(results1 / "lean_execution_status.json", {
    "authorization": "EXTERNAL_REPLAY_EXECUTED",
    "blocking": False,
    "phase": "FVII-SCI-01",
    "reason": "Cumulative Phase-2 replay rebuilt the library, captured axioms, and passed the 51-case Phase-1 differential.",
    "status": "LEAN_BUILD_AND_DIFFERENTIAL_REPLAY_PASS",
    "toolchain": toolchain,
    "lean_version": lean_version,
    "lake_version": lake_version,
})
dump(results1 / "cross_implementation_status.json", {
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
    "external_directions": "formalization/lean/EXTERNAL_COMPILE_PHASE2.md",
    "kernel_build_status": "PASS",
    "lake_available": True,
    "lake_version": lake_version,
    "lean_available": True,
    "lean_version": lean_version,
    "reason": "Cumulative external replay completed the kernel build, Phase-1 differential, and axiom capture.",
    "toolchain": toolchain,
})
dump(results2 / "lean_execution_status.json", {
    "authorization": "EXTERNAL_REPLAY_EXECUTED",
    "blocking": False,
    "phase": "FVII-SCI-02",
    "reason": "Lean kernel build, Phase-2 axiom replay, and nine-envelope differential passed.",
    "status": "LEAN_BUILD_AXIOM_AND_DIFFERENTIAL_REPLAY_PASS",
    "toolchain": toolchain,
    "lean_version": lean_version,
    "lake_version": lake_version,
})
dump(results2 / "cross_implementation_status.json", {
    "phase": "FVII-SCI-02",
    "status": "PASS",
    "python_envelope_rows": 9,
    "lean_envelope_rows": 9,
    "warning": "Agreement is bounded to the nine declared Phase-2 families.",
})
dump(lean_dir / "BUILD_STATUS_PHASE2.json", {
    "build_command": "cd formalization/lean && lake clean && lake build",
    "cross_implementation_status": "PASS_9_OF_9_PHASE2_AND_PASS_51_OF_51_PHASE1",
    "elan_available": elan_available,
    "external_directions": "formalization/lean/EXTERNAL_COMPILE_PHASE2.md",
    "kernel_build_status": "PASS",
    "lake_available": True,
    "lake_version": lake_version,
    "lean_available": True,
    "lean_version": lean_version,
    "phase": "FVII-SCI-02",
    "reason": "External replay completed the cumulative kernel build, both finite differentials, and Phase-2 #print axioms capture.",
    "toolchain": toolchain,
})
manifest_path = root / "science_plan" / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["status"] = "PHASE_02_EXECUTED_EXTERNAL_LEAN_REPLAY_PASS"
manifest["phase2_kernel_status"] = "PASS_EXTERNAL_REPLAY"
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

# Registries and reports become kernel-aware only after replay status is recorded.
python3 "$ROOT/scripts/build_fvii_sci02_registry.py"
rm -rf "$LEAN_DIR/.lake"
find "$ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$ROOT" -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '*.olean' -o -name '*.ilean' \) -delete
python3 "$ROOT/scripts/validate_fvii_sci02.py" --require-lean-results
python3 "$ROOT/scripts/build_fvii_sci02_reports.py"
python3 "$ROOT/scripts/validate_fvii_sci02.py" --require-lean-results
python3 "$ROOT/scripts/build_delivery_manifest.py"
python3 "$ROOT/scripts/verify_delivery_manifest.py"

echo "FVII-SCI-02 external Lean replay: PASS"
