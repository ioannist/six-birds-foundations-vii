# External cumulative Lean replay — FVII-SCI-02

The repository currently pins `leanprover/lean4:v4.28.0` in `lean-toolchain`.
Lean and Lake were unavailable in the phase-execution environment, so this
release does not claim local kernel elaboration, executed `#print axioms`, or
Lean/Python runtime agreement. The owner authorized this as a nonblocking
execution boundary.

A different compatible Lean 4 release may be selected when that is the
least-resistance route. Commit any `lean-toolchain` edit before replay so the
actual trusted environment remains auditable.

## One-command replay

From the repository root, with `lean`, `lake`, and Python 3 on `PATH`:

```bash
bash scripts/run_fvii_sci02_external_lean.sh
```

The script performs a cumulative replay:

1. records the exact toolchain, Lean, and Lake versions;
2. regenerates the Phase-1 51-case and Phase-2 nine-envelope Python baselines;
3. runs `lake clean` and `lake build` over the complete Foundations I–VII import graph;
4. executes `fvii_reference_world` and checks all 51 Phase-1 fixtures;
5. executes `fvii_phase2_envelopes` and checks all nine bounded family counts;
6. captures `#print axioms` for the Phase-1 and Phase-2 public theorem surfaces;
7. performs exact Python/Lean differentials for both executable layers;
8. upgrades machine-readable build status only after all checks pass;
9. runs the strict Phase-2 acceptance validator with `--require-lean-results`;
10. rebuilds reports and the delivery checksum ledger.

## Manual kernel commands

```bash
cd formalization/lean
lake clean
lake build
lake exe fvii_reference_world \
  > ../foundations_vii_lab/results/lean_results.jsonl
lake exe fvii_phase2_envelopes \
  > ../foundations_vii_lab/phase2/results/lean_envelopes.jsonl
lake env lean FoundationsVII/Trust/PrintAxioms.lean \
  > ../foundations_vii_lab/results/lean_axioms.txt 2>&1
lake env lean FoundationsVII/Trust/PrintAxiomsPhase2.lean \
  > ../foundations_vii_lab/phase2/results/lean_axioms.txt 2>&1
```

Use the automated script afterward to perform the differential comparisons and
record the result. Successful replay upgrades only the exact declarations and
the two declared finite families. It does not universalize bounded enumeration
or execute any Phase-3, Phase-4, or Phase-5 science.
