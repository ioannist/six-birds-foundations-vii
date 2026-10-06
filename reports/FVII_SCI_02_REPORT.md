# FVII-SCI-02 — admission, access, provenance, bootstrap, and negative force

**Execution date:** 2026-07-26
**Stage:** `FVII-SCI-02_COMPLETE_WITH_EXTERNAL_LEAN_REPLAY_PENDING`
**Paper or paper-preparation work:** none

Phase 2 closes the operational-domain side of the Foundations VII science program. It supplies typed admission transitions, path replay, access-coordinate separation, bootstrap and provisioning laws, provenance/non-transfer results, prospective commitment, horizon-qualified negative force, observer occupancy, and five exact no-go fronts. It does not implement contact/join, enablement/descent, dynamics, or final cross-family corollaries.

## Delivered formal surface

- 237 public Phase-2 declarations, including 130 theorem/lemma/corollary declarations.
- 9 terminal candidate assets: VII-C001, VII-C002, VII-C003, VII-C004, VII-C005, VII-C006, VII-C021, VII-C022, VII-C029.
- 5 no-go fronts, each with exact scope, a structural proof source, and at least one named positive escape.
- 8 formalization targets closed or cumulatively advanced; FT18 is explicitly only the admission half.
- 9 bounded exhaustive families: 1332 raw, 1076 canonical, 470 accepted, and 606 rejected cases.
- 15 canonical bounded witnesses retained with content hashes.
- Primary fixture replay: 10/10 scenarios and 9/9 countermodels pass.
- Acceptance gate: PASS (31/31 checks).

## Terminal candidate assets

| Candidate | Asset | Definitions | Theorems | Bounded witnesses | Kernel status |
|---|---|---|---|---|---|
| VII-C001 | FVII-SCI02-C001-ACCESS-NORMAL-FORM | 25 | 23 | P2-W01, P2-W02, P2-W06 | external replay pending |
| VII-C002 | FVII-SCI02-C002-ADMISSION-TRANSITIONS | 14 | 27 |  | external replay pending |
| VII-C003 | FVII-SCI02-C003-BOOTSTRAP-OBSTRUCTION | 14 | 17 | P2-W12 | external replay pending |
| VII-C004 | FVII-SCI02-C004-NEUTRAL-PROVISIONING | 23 | 21 |  | external replay pending |
| VII-C005 | FVII-SCI02-C005-ORIGIN-ACCESS-NONTRANSFER | 18 | 16 | P2-W09, P2-W10, P2-W14 | external replay pending |
| VII-C006 | FVII-SCI02-C006-PROSPECTIVE-COMMITMENT | 12 | 14 | P2-W13 | external replay pending |
| VII-C021 | FVII-SCI02-C021-REACHABILITY-NEGATIVE-FORCE | 18 | 27 | P2-W07, P2-W08, P2-W11 | external replay pending |
| VII-C022 | FVII-SCI02-C022-ACCESS-RIGIDITY | 25 | 23 | P2-W03, P2-W04, P2-W05 | external replay pending |
| VII-C029 | FVII-SCI02-C029-OBSERVER-OCCUPANCY | 12 | 17 | P2-W15 | external replay pending |

## Five no-go fronts

| No-go | Scope | Failure control | Positive controls | Escape theorem count |
|---|---|---|---|---|
| NGVII-01 | Declared closed admission regime and declared permitted-first-extension family. | TTW-S01 | TTW-S02 | 3 |
| NGVII-03 | An explicit event-precedence relation; no global clock assumption. | TTW-S04 | TTW-S03 | 1 |
| NGVII-04 | Total source lens transported to a partial target without a certified adapter. | TTW-S23 | TTW-S08 | 1 |
| NGVII-05 | Native/endogenous credit with positive occupancy that exceeds charged occupancy. | TTW-S22 | TTW-S02 | 2 |
| NGVII-11 | Operational profiles satisfying the declared execution/reachability/firing implication spine. | TTW-S20 | TTW-S21 | 1 |

## Scientific conclusions fixed by this phase

- Expressibility, presence, exposure, recoverability, admissibility, reachability, and occurrence are typed separately. Only the declared implication spine is imposed; converse collapses have explicit witnesses.
- Rule soundness, executability, reachability, firing, and occurrence are distinct. Reachability alone cannot certify occurrence.
- Admission, expiry, revocation, retraction, and rollback are typed operations. Lawful rollback and revocation preserve source, budget, and audit history.
- A closed declared regime without an admitted seed or reachable generator has no lawful first extension. Admitted seeds, reachable generators, and open-family recorded external provision are explicit escapes.
- Neutral provisioning requires prospective, task-blind, outcome-independent, source-audited provision. Post-hoc stocking and system-generated source laundering fail the certificate.
- Common origin, carrier, or instrument does not imply shared access; shared access does not imply source independence.
- Total-lens transfer requires a total source, a self-owned target, and—when the target is partial—a certified adapter.
- Finite-horizon non-occurrence is horizon-qualified unless family closure, detector power, and no-later-occurrence are separately certified.
- Hidden observer occupancy invalidates native/endogenous credit; correctly priced external observation and genuine zero occupancy remain explicit escapes.

## Lean execution boundary

Lean and Lake were unavailable locally. The repository therefore claims source-complete theorem assets, static import/trust closure, and executed Python evidence, but not kernel elaboration or runtime Lean/Python agreement. The owner authorized this external replay boundary as nonblocking.

Run `bash scripts/run_fvii_sci02_external_lean.sh` in a Lean-capable environment. A compatible toolchain may replace the current pin if the edit is committed and the cumulative replay succeeds.

## Boundaries retained

- The nine finite envelopes are exhaustive only over their declared bounded universes.
- Static source validation is not a substitute for Lean kernel checking.
- Adapter metadata does not establish semantic equivalence or theorem transport.
- Phase 2 does not define or prove strict join, certified non-interaction, enablement, descent, confluence, holonomy/arrow separation, or final corollaries.
- No paper text or paper-preparation artifact was created.

## Authoritative surfaces

- `science/registry/phase2_public_declarations.jsonl` and `phase2_theorem_catalog.jsonl`
- `science/registry/phase2_candidate_closure.jsonl`
- `science/registry/phase2_no_go_closure.jsonl`
- `science/registry/phase2_formalization_targets.jsonl`
- `science/traceability/phase2_asset_trace.jsonl` and `phase2_statement_hashes.sha256`
- `formalization/foundations_vii_lab/phase2/results/`
- `reports/FVII_SCI_02_VALIDATION.md`
