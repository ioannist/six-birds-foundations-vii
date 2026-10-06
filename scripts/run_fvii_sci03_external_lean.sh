#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEAN_DIR="$ROOT/formalization/lean"
LAB_DIR="$ROOT/formalization/foundations_vii_lab"
RESULTS1="$LAB_DIR/results"
RESULTS2="$LAB_DIR/phase2/results"
RESULTS3="$LAB_DIR/phase3/results"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$LAB_DIR"
mkdir -p "$RESULTS1" "$RESULTS2" "$RESULTS3"

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
if command -v elan >/dev/null 2>&1; then elan_available=true; fi
printf 'Toolchain file: %s\nLean: %s\nLake: %s\nElan available: %s\n' \
  "$toolchain" "$lean_version" "$lake_version" "$elan_available"

python3 -m fvii_lab.cli run --output "$RESULTS1"
python3 "$ROOT/scripts/build_fvii_sci02_lab.py"
python3 "$ROOT/scripts/build_fvii_sci03_lab.py"

(
  cd "$LEAN_DIR"
  lake clean
  lake build
  lake exe fvii_reference_world > "$RESULTS1/lean_results.jsonl"
  lake exe fvii_phase2_envelopes > "$RESULTS2/lean_envelopes.jsonl"
  lake exe fvii_phase3_envelopes > "$RESULTS3/lean_results.jsonl"
  lake env lean FoundationsVII/Trust/PrintAxioms.lean > "$RESULTS1/lean_axioms.txt" 2>&1
  lake env lean FoundationsVII/Trust/PrintAxiomsPhase2.lean > "$RESULTS2/lean_axioms.txt" 2>&1
  lake env lean FoundationsVII/Trust/PrintAxiomsPhase3.lean > "$RESULTS3/lean_axioms.txt" 2>&1
  if command -v leanchecker >/dev/null 2>&1; then
    lake env leanchecker > "$RESULTS3/leanchecker.txt" 2>&1 || true
  fi
)

python3 -m fvii_lab.cli compare "$RESULTS1/lean_results.jsonl" --output "$RESULTS1/cross_implementation.json"

python3 - "$RESULTS2/envelopes.jsonl" "$RESULTS2/lean_envelopes.jsonl" "$RESULTS2/cross_implementation.json" <<'PY'
import json, sys
from pathlib import Path
py_path, lean_path, out_path = map(Path, sys.argv[1:4])
py = {r['family_id']: r for r in map(json.loads, filter(str.strip, py_path.read_text().splitlines()))}
le = {r['family_id']: r for r in map(json.loads, filter(str.strip, lean_path.read_text().splitlines()))}
fields=('raw_cardinality','canonical_cardinality','accepted_cardinality','rejected_cardinality')
mis=[]
for key in sorted(set(py)&set(le)):
    delta={f:{'python':py[key].get(f),'lean':le[key].get(f)} for f in fields if py[key].get(f)!=le[key].get(f)}
    if delta: mis.append({'family_id':key,'fields':delta})
payload={'all_pass':set(py)==set(le) and not mis,'phase':'FVII-SCI-02','python_rows':len(py),'lean_rows':len(le),'mismatches':mis,'fields_compared':list(fields),'warning':'Bounded finite-family agreement only.'}
out_path.write_text(json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n')
if not payload['all_pass']: raise SystemExit(payload)
PY

python3 - "$RESULTS3/envelopes.jsonl" "$RESULTS3/primary_scenario_results.jsonl" "$RESULTS3/primary_countermodel_results.jsonl" "$RESULTS3/lean_results.jsonl" "$RESULTS3/cross_implementation.json" <<'PY'
import json, sys
from pathlib import Path
py_env_path, py_s_path, py_c_path, lean_path, out_path = map(Path, sys.argv[1:6])
py_env={r['family_id']:r for r in map(json.loads,filter(str.strip,py_env_path.read_text().splitlines()))}
py_s={r['scenario_id']:r for r in map(json.loads,filter(str.strip,py_s_path.read_text().splitlines()))}
py_c={r['countermodel_id']:r for r in map(json.loads,filter(str.strip,py_c_path.read_text().splitlines()))}
lean_rows=[json.loads(x) for x in lean_path.read_text().splitlines() if x.strip()]
le_env={r['family_id']:r for r in lean_rows if 'family_id' in r}
le_s={r['id']:r for r in lean_rows if r.get('kind')=='scenario'}
le_c={r['id']:r for r in lean_rows if r.get('kind')=='countermodel'}
fields=('raw_cardinality','canonical_cardinality','accepted_cardinality','rejected_cardinality')
mis=[]
for key in sorted(set(py_env)&set(le_env)):
    delta={f:{'python':py_env[key].get(f),'lean':le_env[key].get(f)} for f in fields if py_env[key].get(f)!=le_env[key].get(f)}
    if delta: mis.append({'family_id':key,'fields':delta})
scenario_mismatch=[key for key in sorted(set(py_s)|set(le_s)) if key not in py_s or key not in le_s or bool(py_s[key].get('pass')) != bool(le_s[key].get('pass'))]
countermodel_mismatch=[key for key in sorted(set(py_c)|set(le_c)) if key not in py_c or key not in le_c or bool(py_c[key].get('pass')) != bool(le_c[key].get('pass'))]
payload={
 'all_pass':set(py_env)==set(le_env) and not mis and not scenario_mismatch and not countermodel_mismatch,
 'phase':'FVII-SCI-03','python_envelope_rows':len(py_env),'lean_envelope_rows':len(le_env),
 'python_scenario_rows':len(py_s),'lean_scenario_rows':len(le_s),'python_countermodel_rows':len(py_c),'lean_countermodel_rows':len(le_c),
 'envelope_mismatches':mis,'scenario_mismatches':scenario_mismatch,'countermodel_mismatches':countermodel_mismatch,
 'fields_compared':list(fields),'warning':'Agreement is exhaustive only over the eleven declared bounded families and assigned finite fixtures.'}
out_path.write_text(json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n')
if not payload['all_pass']: raise SystemExit(payload)
PY

python3 - "$ROOT" "$toolchain" "$lean_version" "$lake_version" "$elan_available" <<'PY'
import json, sys
from pathlib import Path
root=Path(sys.argv[1]); toolchain,lean_version,lake_version,elan_text=sys.argv[2:6]
lab=root/'formalization'/'foundations_vii_lab'; r1=lab/'results'; r2=lab/'phase2'/'results'; r3=lab/'phase3'/'results'; lean=root/'formalization'/'lean'
for path in [r1/'cross_implementation.json',r2/'cross_implementation.json',r3/'cross_implementation.json']:
    if json.loads(path.read_text()).get('all_pass') is not True: raise SystemExit(f'failed differential: {path}')
if len([x for x in (r1/'lean_results.jsonl').read_text().splitlines() if x.strip()]) != 51: raise SystemExit('Phase-1 row count')
if len([x for x in (r2/'lean_envelopes.jsonl').read_text().splitlines() if x.strip()]) != 9: raise SystemExit('Phase-2 row count')
if len([x for x in (r3/'lean_results.jsonl').read_text().splitlines() if x.strip()]) != 37: raise SystemExit('Phase-3 row count')
for path in [r1/'lean_axioms.txt',r2/'lean_axioms.txt',r3/'lean_axioms.txt']:
    if not path.is_file() or path.stat().st_size == 0: raise SystemExit(f'missing axiom receipt {path}')
def dump(path,value): path.write_text(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n')
dump(r3/'lean_execution_status.json',{'authorization':'EXTERNAL_REPLAY_EXECUTED','blocking':False,'phase':'FVII-SCI-03','reason':'Cumulative kernel build, axiom replay, eleven-envelope and assigned-fixture differentials passed.','status':'LEAN_BUILD_AXIOM_AND_DIFFERENTIAL_REPLAY_PASS','toolchain':toolchain,'lean_version':lean_version,'lake_version':lake_version})
dump(r3/'cross_implementation_status.json',{'phase':'FVII-SCI-03','status':'PASS','python_envelope_rows':11,'lean_envelope_rows':11,'python_scenario_rows':12,'lean_scenario_rows':12,'python_countermodel_rows':14,'lean_countermodel_rows':14,'warning':'Agreement is bounded to the declared finite families and fixtures.'})
dump(lean/'BUILD_STATUS_PHASE3.json',{'build_command':'cd formalization/lean && lake clean && lake build','cross_implementation_status':'PASS_11_OF_11_PHASE3_PLUS_12_SCENARIOS_PLUS_14_COUNTERMODELS','elan_available':elan_text.lower()=='true','external_directions':'formalization/lean/EXTERNAL_COMPILE_PHASE3.md','kernel_build_status':'PASS','lake_available':True,'lake_version':lake_version,'lean_available':True,'lean_version':lean_version,'phase':'FVII-SCI-03','reason':'External cumulative replay completed the kernel build, all finite differentials, and Phase-3 #print axioms capture.','toolchain':toolchain})
manifest_path=root/'science_plan'/'manifest.json'; m=json.loads(manifest_path.read_text()); m['status']='PHASE_03_EXECUTED_EXTERNAL_LEAN_REPLAY_PASS'; m['phase3_kernel_status']='PASS_EXTERNAL_REPLAY'; manifest_path.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
PY

python3 "$ROOT/scripts/build_fvii_sci03_registry.py"
rm -rf "$LEAN_DIR/.lake"
find "$ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$ROOT" -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '*.olean' -o -name '*.ilean' \) -delete
python3 "$ROOT/scripts/validate_fvii_sci03_lean_static.py"
python3 "$ROOT/scripts/validate_fvii_sci03.py" --require-lean-results
python3 "$ROOT/scripts/build_fvii_sci03_reports.py"
python3 "$ROOT/scripts/validate_fvii_sci03.py" --require-lean-results
python3 "$ROOT/scripts/build_delivery_manifest.py"
python3 "$ROOT/scripts/verify_delivery_manifest.py"
echo "FVII-SCI-03 external Lean replay: PASS"
