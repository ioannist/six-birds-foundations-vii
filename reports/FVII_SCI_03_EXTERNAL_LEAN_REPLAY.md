# FVII-SCI-03 external Lean replay

Current repository pin: `leanprover/lean4:v4.28.0`. The owner permits a different compatible Lean 4 version when that is easier, provided the change is recorded and the complete cumulative replay passes.

```bash
bash scripts/run_fvii_sci03_external_lean.sh
```

The script rebuilds the cumulative library, executes the Phase-1 51-case runner, Phase-2 nine-envelope runner, and Phase-3 eleven-envelope plus assigned-fixture runner; captures all three axiom surfaces; compares Lean outputs to independent Python results; and invokes the strict Phase-3 validator.

Until that script succeeds, `NOT_RUN_LOCAL_ENVIRONMENT` is the truthful kernel status.
