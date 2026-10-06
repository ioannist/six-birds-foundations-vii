# VII-C007 — Join-entry record normal form

**Grade:** `UNPROVED_FOUNDATIONS_VII_CANDIDATE`  
**Priority:** `P0`  
**Chapter:** `Ch04`  

## Proposed conclusion

Entry to the join calculus requires parent packages, typed contact surface, witnessed contact or pending status, source and licensing ledgers, budget, obstruction semantics, and an append-only audit record.

## Setup and hypotheses

- Fix the inherited SBT theory package(s), carrier, interfaces, quotient/readout, and audit scope.
- Declare all source, transition, budget, observer, and temporal records used by the candidate.
- Restrict the conclusion to the stated finite or explicitly quantified carrier until a stronger proof is supplied.
- All records are well typed and source-located.
- No undeclared operation, source, or observer resource is used.
- Inherited results are transported only through accepted bridge/reuse records.

## Proof obligations

- Prove field sufficiency for retrospective verification.
- Separate pending, failed, obstructed, and completed statuses.
- Show omission of source/contact/budget fields permits false positives.

## Detector / null / falsifier

- **Signal:** A source-typed witness satisfying the Join-entry record normal form record and its declared audit.
- **Null:** A matched case with the principal witness removed while all unrelated fields are held fixed.
- **Falsifier:** A well-typed model satisfying the hypotheses but violating the proposed conclusion for Join-entry record normal form.

## Finite models and countermodels

- Positive: TTW-S06
- Nulls: TTW-S08, TTW-S12
- Countermodels: CM-02, CM-03, CM-14

## Source trace

- Supporting claims: 60
- Boundary claims: 49
- Open obligations: 13
- Exact deduplicated source rows: 117
- Bridges: BR-CITE-0128, BR-CITE-0030, BR-CITE-0054, BR-CITE-0212, BR-CITE-0115, BR-CITE-0053, BR-CITE-0083, BR-CITE-0084, BR-CITE-0085, BR-CITE-0086, BR-CITE-0022, BR-CITE-0010, BR-CITE-0024, BR-CITE-0031, BR-CITE-0055, BR-CITE-0087, BR-CITE-0088, BR-CITE-0089, BR-CITE-0004, BR-CITE-0025, BR-CITE-0026, BR-CITE-0027, BR-CITE-0028, BR-CITE-0029, BR-CITE-0032, BR-CITE-0153, BR-CITE-0058, BR-CITE-0099, BR-CITE-0016, BR-CITE-0124, BR-CITE-0126, BR-CITE-0127, BR-CITE-0129, BR-CITE-0130, BR-CITE-0131, BR-CITE-0132, BR-CITE-0135, BR-CITE-0046
- Prior laws/no-gos: NG_FORCE_FOREST, NG_FORCE_NULL, NG_LADDER_BOUNDED_INTERFACE, NG_PROTOCOL_TRAP, NG_ARROW_DPI, NG_LADDER_IDEM, NG_MACRO_CLOSURE_DEFICIT, NG_OBJECT_CONTRACTIVE

## Nonclaims

- Record completeness does not prove a join exists.
- This Step-3 dossier is not a proof of the candidate.
- Finite reference-world success does not universalize the statement.
