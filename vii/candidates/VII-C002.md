# VII-C002 — Lawful admission transition system

**Grade:** `UNPROVED_FOUNDATIONS_VII_CANDIDATE`  
**Priority:** `P0`  
**Chapter:** `Ch03`  

## Proposed conclusion

Admission, expiry, revocation, retraction, and rollback are typed transitions whose execution requires source, budget, guard, and audit witnesses distinct from rule text.

## Setup and hypotheses

- Fix the inherited SBT theory package(s), carrier, interfaces, quotient/readout, and audit scope.
- Declare all source, transition, budget, observer, and temporal records used by the candidate.
- Restrict the conclusion to the stated finite or explicitly quantified carrier until a stronger proof is supplied.
- All records are well typed and source-located.
- No undeclared operation, source, or observer resource is used.
- Inherited results are transported only through accepted bridge/reuse records.

## Proof obligations

- Give transition typing and ledger-update laws.
- Separate soundness, executability, reachability, firing, and occurrence.
- Specify lawful rollback without erasing history.

## Detector / null / falsifier

- **Signal:** A source-typed witness satisfying the Lawful admission transition system record and its declared audit.
- **Null:** A matched case with the principal witness removed while all unrelated fields are held fixed.
- **Falsifier:** A well-typed model satisfying the hypotheses but violating the proposed conclusion for Lawful admission transition system.

## Finite models and countermodels

- Positive: TTW-S19
- Nulls: TTW-S20, TTW-S21
- Countermodels: CM-08, CM-09, CM-18

## Source trace

- Supporting claims: 63
- Boundary claims: 46
- Open obligations: 23
- Exact deduplicated source rows: 132
- Bridges: BR-CITE-0190, BR-CITE-0003, BR-CITE-0004, BR-CITE-0005, BR-CITE-0006, BR-CITE-0007, BR-CITE-0008, BR-CITE-0010, BR-CITE-0011, BR-CITE-0129, BR-LAW-0021, BR-LAW-0026, BR-LAW-0033, BR-CITE-0116, BR-CITE-0032, BR-CITE-0159, BR-CITE-0239, BR-CITE-0075, BR-CITE-0080, BR-CITE-0207, BR-CITE-0109, BR-CITE-0154, BR-CITE-0096, BR-CITE-0213, BR-CITE-0098, BR-CITE-0197, BR-CITE-0236
- Prior laws/no-gos: E3, E8, E15, F20, F3, F9

## Nonclaims

- A well-formed rule need not be executable.
- A reachable transition need not fire.
- This Step-3 dossier is not a proof of the candidate.
- Finite reference-world success does not universalize the statement.
