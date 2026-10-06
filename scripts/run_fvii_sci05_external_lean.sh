#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEAN_DIR="$ROOT/formalization/lean"
LAB="$ROOT/formalization/foundations_vii_lab"
R1="$LAB/results"
R2="$LAB/phase2/results"
R3="$LAB/phase3/results"
R4="$LAB/phase4/results"
R5="$LAB/phase5/results"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$LAB"

run_with_heartbeat() {
  local label="$1"
  shift
  "$@" &
  local command_pid=$!
  while kill -0 "$command_pid" 2>/dev/null; do
    sleep "${FVII_LEAN_HEARTBEAT_SECONDS:-30}"
    if kill -0 "$command_pid" 2>/dev/null; then
      printf 'Still running: %s\n' "$label"
    fi
  done
  wait "$command_pid"
}

for cmd in python3 lean lake; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    echo "Install a compatible Lean 4 toolchain, or edit formalization/lean/lean-toolchain and commit the change." >&2
    exit 2
  fi
done

lean_version="$(lean --version | head -n 1)"
lake_version="$(lake --version | head -n 1)"
toolchain="$(tr -d '\r\n' < "$LEAN_DIR/lean-toolchain")"
elan_available=false
if command -v elan >/dev/null 2>&1; then elan_available=true; fi
printf 'Toolchain file: %s\nLean: %s\nLake: %s\nElan available: %s\n' \
  "$toolchain" "$lean_version" "$lake_version" "$elan_available"

python3 -m fvii_lab.cli run --output "$R1"
python3 "$ROOT/scripts/build_fvii_sci02_lab.py"
python3 "$ROOT/scripts/build_fvii_sci03_lab.py"
python3 "$ROOT/scripts/build_fvii_sci04_lab.py"
python3 "$ROOT/scripts/build_fvii_sci05_lab.py"
python3 -m unittest discover -s "$LAB/tests" -p 'test*.py' -v

(
  cd "$LEAN_DIR"
  lake clean
  if [[ "${FVII_LEAN_LOW_MEMORY:-0}" == "1" ]]; then
    run_with_heartbeat "Phase-3 finite envelope prebuild" \
      lake build +FoundationsVII.Models.Finite.Phase3.ContactJoinEnvelope
    run_with_heartbeat "Phase-4 finite envelope prebuild" \
      lake build +FoundationsVII.Models.Finite.Phase4.DynamicsEnvelope
    run_with_heartbeat "Phase-5 finite envelope prebuild" \
      lake build +FoundationsVII.Models.Finite.Phase5.ClosureEnvelope
  fi
  run_with_heartbeat "cumulative Lean build" lake build
  lake exe fvii_reference_world > "$R1/lean_results.jsonl"
  lake exe fvii_phase2_envelopes > "$R2/lean_envelopes.jsonl"
  lake exe fvii_phase3_envelopes > "$R3/lean_results.jsonl"
  lake exe fvii_phase4_envelopes > "$R4/lean_results.jsonl"
  lake exe fvii_phase5_envelopes > "$R5/lean_results.jsonl"
  lake env lean FoundationsVII/Trust/PrintAxiomsFinal.lean > "$R5/lean_axioms.txt" 2>&1
)

python3 -m fvii_lab.cli compare "$R1/lean_results.jsonl" --output "$R1/cross_implementation.json"
python3 "$ROOT/scripts/compare_fvii_sci05_lean.py" \
  --phase FVII-SCI-02 --python-envelopes "$R2/envelopes.jsonl" \
  --lean-results "$R2/lean_envelopes.jsonl" --output "$R2/cross_implementation.json"
python3 "$ROOT/scripts/compare_fvii_sci05_lean.py" \
  --phase FVII-SCI-03 --python-envelopes "$R3/envelopes.jsonl" \
  --python-scenarios "$R3/primary_scenario_results.jsonl" \
  --python-countermodels "$R3/primary_countermodel_results.jsonl" \
  --lean-results "$R3/lean_results.jsonl" --output "$R3/cross_implementation.json"
python3 "$ROOT/scripts/compare_fvii_sci05_lean.py" \
  --phase FVII-SCI-04 --python-envelopes "$R4/envelopes.jsonl" \
  --python-scenarios "$R4/primary_scenario_results.jsonl" \
  --python-countermodels "$R4/primary_countermodel_results.jsonl" \
  --lean-results "$R4/lean_results.jsonl" --output "$R4/cross_implementation.json"
python3 "$ROOT/scripts/compare_fvii_sci05_lean.py" \
  --phase FVII-SCI-05 --python-envelopes "$R5/envelopes.jsonl" \
  --python-scenarios "$R5/all_scenario_results.jsonl" \
  --python-countermodels "$R5/all_countermodel_results.jsonl" \
  --lean-results "$R5/lean_results.jsonl" --output "$R5/cross_implementation_status.json"

python3 - "$ROOT" "$toolchain" "$lean_version" "$lake_version" "$elan_available" <<'PY'
import json, re, sys
from pathlib import Path
root=Path(sys.argv[1]); toolchain,lean_version,lake_version,elan_text=sys.argv[2:6]
lab=root/'formalization'/'foundations_vii_lab'; lean=root/'formalization'/'lean'
paths=[lab/'results'/'cross_implementation.json',lab/'phase2'/'results'/'cross_implementation.json',lab/'phase3'/'results'/'cross_implementation.json',lab/'phase4'/'results'/'cross_implementation.json',lab/'phase5'/'results'/'cross_implementation_status.json']
for path in paths:
    payload=json.loads(path.read_text())
    if payload.get('all_pass') is not True:
        raise SystemExit(f'failed differential: {path}: {payload}')
axioms=lab/'phase5'/'results'/'lean_axioms.txt'
if not axioms.is_file() or axioms.stat().st_size == 0:
    raise SystemExit('missing final axiom receipt')
expected=sum(1 for line in (lean/'FoundationsVII'/'Trust'/'PrintAxiomsFinal.lean').read_text().splitlines() if line.startswith('#print axioms '))
text=axioms.read_text(errors='replace')
if 'declaration uses \'sorry\'' in text or 'sorryAx' in text:
    raise SystemExit('final axiom receipt reports a sorry dependency')
# Lean output formats vary, so the strict source count is recorded next to the raw receipt.
receipt={'phase':'FVII-SCI-05','status':'PASS_RAW_AXIOM_RECEIPT_CAPTURED','theorem_count_requested':expected,'receipt_bytes':axioms.stat().st_size,'sorry_dependency_detected':False,'toolchain':toolchain,'lean_version':lean_version,'lake_version':lake_version}
(lab/'phase5'/'results'/'lean_axiom_receipt_summary.json').write_text(json.dumps(receipt,sort_keys=True,separators=(',',':'))+'\n')
status={'build_command':'cd formalization/lean && lake clean && lake build','cross_implementation_status':'PASS_ALL_FIVE_PHASE_RUNNERS','elan_available':elan_text.lower()=='true','external_directions':'formalization/lean/EXTERNAL_COMPILE_FINAL.md','kernel_build_status':'PASS','lake_available':True,'lake_version':lake_version,'lean_available':True,'lean_version':lean_version,'phase':'FVII-SCI-05','reason':'Local cumulative replay completed the public kernel build, all finite differentials, and the final #print axioms capture.','toolchain':toolchain}
(lean/'BUILD_STATUS_FINAL.json').write_text(json.dumps(status,indent=2,sort_keys=True)+'\n')
execution={'authorization':'LOCAL_REPLAY_EXECUTED','blocking':False,'phase':'FVII-SCI-05','reason':status['reason'],'status':'LEAN_BUILD_AXIOM_AND_DIFFERENTIAL_REPLAY_PASS','toolchain':toolchain,'lean_version':lean_version,'lake_version':lake_version}
(lab/'phase5'/'results'/'lean_execution_status.json').write_text(json.dumps(execution,sort_keys=True,separators=(',',':'))+'\n')
manifest_path=root/'science_plan'/'manifest.json'; manifest=json.loads(manifest_path.read_text()); manifest['status']='FINAL_SCIENCE_RELEASE_LOCAL_LEAN_REPLAY_PASS'; manifest['final_kernel_status']='PASS_LOCAL_REPLAY'; manifest_path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
PY

python3 "$ROOT/scripts/build_fvii_sci05_registry.py"
python3 "$ROOT/scripts/build_phase_declaration_rebinding.py"
rm -rf "$LEAN_DIR/.lake"
find "$ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$ROOT" -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '*.olean' -o -name '*.ilean' \) -delete
python3 "$ROOT/scripts/validate_fvii_sci05_lean_static.py"
python3 "$ROOT/scripts/validate_fvii_sci05.py" --require-lean-results
python3 "$ROOT/scripts/build_fvii_sci05_reports.py"
python3 "$ROOT/scripts/validate_fvii_sci05.py" --require-lean-results
python3 "$ROOT/scripts/build_delivery_manifest.py"
python3 "$ROOT/scripts/verify_delivery_manifest.py"
printf '%s\n' 'Foundations VII final external Lean replay: PASS'
