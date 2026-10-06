# External Lean replay — final Foundations VII science release

The release is currently pinned to `leanprover/lean4:v4.28.0`. A different compatible Lean 4 release may be selected by editing `lean-toolchain`, recording the change in Git, and running the same cumulative replay.

From the repository root:

```sh
bash scripts/run_fvii_sci05_external_lean.sh
```

The script requires `python3`, `lean`, and `lake` on `PATH`. It performs:

1. deterministic regeneration of all Python finite baselines for FVII-SCI-01 through FVII-SCI-05;
2. `lake clean` and a build of the final public root;
3. execution of all five Lean finite runners;
4. exact Lean/Python comparison for the 24 frozen scenarios, 27 named countermodels, all Phase-2/3/4 envelopes, and all eleven final Phase-5 envelopes;
5. `#print axioms` capture for every final public theorem;
6. update of the final build and differential receipts only after every check passes;
7. strict final validation with `--require-lean-results`;
8. regeneration of final reports and the delivery checksum ledger.

Expected final receipts include:

- `formalization/foundations_vii_lab/phase5/results/lean_results.jsonl`;
- `formalization/foundations_vii_lab/phase5/results/cross_implementation_status.json`;
- `formalization/foundations_vii_lab/phase5/results/lean_axioms.txt`;
- `formalization/lean/BUILD_STATUS_FINAL.json`.

Those receipts have passed: the replay was executed locally on `leanprover/lean4:v4.28.0`, so the
truthful formal grade is now **Lean kernel verified (local replay)**. Static import and trust
reachability analysis is still not a substitute for kernel elaboration or executed `#print axioms`
output — it is the executed receipts, not the static audit, that carry the grade. If any source
changes, the grade reverts to source-complete until this script is re-run.
