# FVII-SCI-02 external Lean replay

Current repository pin: `leanprover/lean4:v4.28.0`. The owner permits a different compatible Lean 4 version when that is easier, provided the change is recorded and the complete replay passes.

```bash
bash scripts/run_fvii_sci02_external_lean.sh
```

The script rebuilds the cumulative library, executes the Phase-1 51-case runner and Phase-2 nine-envelope runner, captures both axiom surfaces, compares both Lean outputs to independent Python results, and invokes the strict Phase-2 validator.

Until that script succeeds, `NOT_RUN_LOCAL_ENVIRONMENT` is the truthful kernel status.
