# Foundations VII finite reference laboratories

This directory contains independent executable evidence layers and corresponding Lean finite implementations under `../lean/FoundationsVII/Models/Finite/`. Finite enumeration is never substituted for a universal theorem.

## FVII-SCI-01 reference world

The frozen Phase-1 family contains 24 Two-Theory World scenarios and 27 countermodels under the closed `FVII-SCI-01.3` JSON contract. The Python evaluator validates the complete structural envelope; the Lean runner independently checks its finite semantic projection.

## FVII-SCI-02 admission laboratory

`phase2.py` enumerates nine declared bounded universes: access normal forms, operational transitions, bootstrap/provisioning, commitments, source access, totality transfer, negative force, observer occupancy, and failed-admission settlement.

Deterministic census: 1,332 raw, 1,076 canonical, 470 accepted, 606 rejected, and 15 witnesses. The assigned fixtures replay 10/10 scenarios and 9/9 countermodels.

## FVII-SCI-03 contact/join laboratory

`phase3.py` enumerates eleven bounded universes covering contact/composite status, strict join, source independence, payment/capacity, retention/refinement, residuals/needles, non-interaction, categorical special cases, and contact-measure controls.

Deterministic census: 141,112 raw, 73,528 canonical, 34,532 accepted, 38,996 rejected, and 27 witnesses. The assigned fixtures replay 12/12 scenarios and 14/14 countermodels.

## FVII-SCI-04 enablement/dynamics laboratory

`phase4.py` enumerates twelve bounded universes:

- attribution;
- endogenous credit;
- birth classification;
- transmission/descent fidelity;
- enablement/descent/sufficiency separation;
- enablement composition and residual debt;
- critical-pair confluence;
- seed dependence;
- interaction holonomy;
- arrow certification;
- cross-time contact;
- primitive-algebra readiness.

Deterministic census: 55,168 raw/canonical, 14,832 accepted, 40,336 rejected, and 32 witnesses. The assigned fixtures replay 9/9 scenarios and 8/8 countermodels.

## Local execution

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=formalization/foundations_vii_lab \
python3 -m fvii_lab.cli run \
  --output formalization/foundations_vii_lab/results

python3 scripts/build_fvii_sci02_lab.py
python3 scripts/build_fvii_sci03_lab.py
python3 scripts/build_fvii_sci04_lab.py

PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=formalization/foundations_vii_lab \
python3 -m unittest discover \
  -s formalization/foundations_vii_lab/tests -p 'test*.py' -v
```

All 62 cumulative Python tests pass. For the cumulative Lean kernel, axiom, and differential replay, run:

```bash
bash scripts/run_fvii_sci04_external_lean.sh
```
