# External Lean replay — FVII-SCI-01

The delivered repository pins `leanprover/lean4:v4.28.0` in
`formalization/lean/lean-toolchain`. No usable Lean/Lake executable was available in
the phase-execution environment, so the delivery does **not** claim a local
kernel build. The owner explicitly authorized this environmental boundary.

A compatible Lean 4 version may be selected instead when that is the
least-resistance route. Record any `lean-toolchain` edit in Git and rerun the
complete replay; do not treat static source checks as a kernel proof.

## One-command replay

From the repository root, with `lean`, `lake`, and Python 3 available:

```bash
bash scripts/run_fvii_sci01_external_lean.sh
```

The script performs, in order:

1. records the actual toolchain, Lean, and Lake versions;
2. regenerates the independent Python baseline;
3. runs `lake clean` and `lake build`;
4. executes the Lean finite reference-world runner, producing 51 JSONL rows;
5. runs every generated `#print axioms` command;
6. compares the Lean rows against the independent Python evaluator;
7. upgrades the machine-readable kernel/trust status only after exact agreement;
8. removes `.lake` and Python cache artifacts;
9. runs the strict Phase-1 validator with `--require-lean-results`;
10. regenerates the human-readable reports.

## Manual equivalent

```bash
cd formalization/lean
lake clean
lake build
lake exe fvii_reference_world \
  > ../foundations_vii_lab/results/lean_results.jsonl
lake env lean FoundationsVII/Trust/PrintAxioms.lean \
  > ../foundations_vii_lab/results/lean_axioms.txt 2>&1
cd ../..
PYTHONPATH=formalization/foundations_vii_lab \
  python3 -m fvii_lab.cli run \
  --output formalization/foundations_vii_lab/results
PYTHONPATH=formalization/foundations_vii_lab \
  python3 -m fvii_lab.cli compare \
  formalization/foundations_vii_lab/results/lean_results.jsonl \
  --output formalization/foundations_vii_lab/results/cross_implementation.json
```

The automated script should then be used to record the successful status and
run the strict validator. A successful replay upgrades only the exact source
declarations and the finite 51-case agreement. It does not promote any
Phase-2, Phase-3, or Phase-4 scientific candidate.

## Cumulative note

After FVII-SCI-02, prefer `bash scripts/run_fvii_sci02_external_lean.sh`. It
replays this Phase-1 surface and the Phase-2 surface in one kernel build.
