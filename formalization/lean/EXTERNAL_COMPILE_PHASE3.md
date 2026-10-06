# External Lean replay — FVII-SCI-03

The cumulative source is pinned to `leanprover/lean4:v4.28.0`. A different compatible Lean 4 release may be selected by editing `lean-toolchain` and committing the change before replay.

From the repository root, run:

```sh
bash scripts/run_fvii_sci03_external_lean.sh
```

The script requires `lean`, `lake`, and `python3` on `PATH`. It performs:

1. deterministic regeneration of the Phase-1, Phase-2, and Phase-3 Python baselines;
2. `lake clean` followed by the cumulative `lake build`;
3. execution of the 51-case Phase-1 runner;
4. execution of all nine Phase-2 finite envelopes;
5. execution of the eleven Phase-3 envelopes, twelve assigned scenarios, and fourteen assigned countermodels;
6. `#print axioms` replay for every Phase-1, Phase-2, and Phase-3 public theorem surface;
7. exact Lean/Python differential checks;
8. the strict FVII-SCI-03 validator with `--require-lean-results`.

A successful replay updates only execution-status and generated validation/report surfaces. It does not change theorem statements or finite-family definitions. Commit the replay receipts and any toolchain-pin change.

## Expected outputs

- `formalization/foundations_vii_lab/results/lean_results.jsonl`
- `formalization/foundations_vii_lab/phase2/results/lean_envelopes.jsonl`
- `formalization/foundations_vii_lab/phase3/results/lean_results.jsonl`
- `formalization/foundations_vii_lab/phase3/results/cross_implementation.json`
- `formalization/foundations_vii_lab/phase3/results/lean_axioms.txt`
- `formalization/lean/BUILD_STATUS_PHASE3.json`

Until those receipts exist and pass the strict validator, the truthful grade is source-complete with external kernel replay pending.
