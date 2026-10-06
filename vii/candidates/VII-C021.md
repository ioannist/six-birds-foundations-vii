# VII-C021 — Reachability, guard activity, and horizon law

**Grade:** `UNPROVED_FOUNDATIONS_VII_CANDIDATE`  
**Priority:** `P0`  
**Chapter:** `Ch08`  

## Proposed conclusion

Lawfulness, non-vacuity, reachability, firing, and occurrence are separate; finite-horizon non-occurrence licenses only horizon-qualified conclusions unless reachability and guard power are independently established.

## Setup and hypotheses

- Fix the inherited SBT theory package(s), carrier, interfaces, quotient/readout, and audit scope.
- Declare all source, transition, budget, observer, and temporal records used by the candidate.
- Restrict the conclusion to the stated finite or explicitly quantified carrier until a stronger proof is supplied.
- All records are well typed and source-located.
- No undeclared operation, source, or observer resource is used.
- Inherited results are transported only through accepted bridge/reuse records.

## Proof obligations

- Define guard-activity and reachability witnesses.
- Prove sound-unreachable and reachable-nonoccurring models.
- State exhaustive closed-family conditions for stronger negatives.

## Detector / null / falsifier

- **Signal:** A source-typed witness satisfying the Reachability, guard activity, and horizon law record and its declared audit.
- **Null:** A matched case with the principal witness removed while all unrelated fields are held fixed.
- **Falsifier:** A well-typed model satisfying the hypotheses but violating the proposed conclusion for Reachability, guard activity, and horizon law.

## Finite models and countermodels

- Positive: TTW-S19
- Nulls: TTW-S20, TTW-S21
- Countermodels: CM-08, CM-09, CM-18

## Source trace

- Supporting claims: 38
- Boundary claims: 26
- Open obligations: 14
- Exact deduplicated source rows: 78
- Bridges: BR-CITE-0197, BR-CITE-0236
- Prior laws/no-gos: none

## Nonclaims

- Non-occurrence alone is not impossibility.
- This Step-3 dossier is not a proof of the candidate.
- Finite reference-world success does not universalize the statement.
