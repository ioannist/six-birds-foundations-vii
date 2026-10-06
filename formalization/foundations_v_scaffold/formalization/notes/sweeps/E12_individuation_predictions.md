# E12 Individuation Law — Toy-Lab Predictions (Round A, pre-registration)

Written before any sweep implementation exists. Round B implements against this document; it does not
redesign the fixture after seeing results. All arithmetic is exact (`fractions.Fraction`); no
randomness. The carrier reuses `lab/sixbirds_foundations_v/worlds/repair_world.py`'s ring-kernel style
(as E3 does), extended with fresh dataclasses for `Subcarrier`/`Candidates`/the six status-case checks
that do not yet exist in the Python fixture layer — these mirror
`lean/SixBirdsFoundationsV/Laws/E12Individuation.lean`'s definitions directly, not a paraphrase.

## 1. Toy-Lab Configuration

### Ring carrier

`Z = {0, 1, ..., 29}` (30 states — expanded from the original 24 in a disclosed post-hoc addition, see
"Post-registration addition" below), `supp_k(z, z') := z' == (z + 1) mod 30` — a ring kernel matching
E3's `ring_kernel` precedent. `tau(n) = n mod 30`, `nStart = 0`. Repair moves are single-step
transitions `z -> z+1 mod 30`, gated the same way E3's `RepairAction`/`is_lawful_action` gates them
(defect + audit record + `CorePromotionGatesPass`-equivalent D4 admissibility).

### Post-registration addition (disclosed correction, forced by step-5 methodology review)

The original Round A registration (states 0-23) tested every claimed boundary as already
`SufficiencyClosureCertified`, and every maximality check against a declared candidate that had no
competing declared superset. Neither of E12.md's own `Δ_bound` (boundary genuinely insufficient, not
merely non-coarsest) nor `Δ_max` (a strictly larger *declared* candidate blocking maximality)
falsifiers was ever the actual, load-bearing reason a registered candidate failed — a real methodology
gap, caught by the mandatory step-5 review (LANDING_PLAN.md §6.1), not a post-hoc fit to observed
results. The fix is two new candidates plus a ring expansion to give them disjoint fresh states
(states 17, 19, and 20 were already committed to `cand_coarsest_control`/`cand_unlinked_control` in the
original registration and are not reused):

- `cand_bound_control = {24, 25}`: genuine repair (`24 → 25`), feasible own-policy budget witness,
  own-policy record witness, and a genuine E3 self-maintenance witness (`source_state = 24`) — every
  closure and the self-maintenance clause hold. Its *only* attempted boundary quotient collapses two
  states with different declared viability-probe readouts into the same class, so
  `SufficiencyClosureCertified = False` for that quotient (no other quotient is attempted for this
  candidate) — `ViabilitySufficientBoundary` fails for the `Δ_bound` reason specifically, not for lack
  of a witness.
- `cand_max_sub = {26, 27}` and `cand_max_sup = {26, 27, 28}`: both independently satisfy every
  closure and boundary/self-maintenance condition on their own. `cand_max_sup` is declared as a
  strictly larger candidate covering `cand_max_sub`'s states plus one more (`28`). `cand_max_sub`
  therefore satisfies `Individuates` but fails `MaximalIndividuating`'s universal clause specifically
  because the declared `cand_max_sup` is a strict superset that also individuates — the `Δ_max`
  falsifier, exercised directly.

### Declared candidate subcarriers (`Candidates`)

Each candidate is a named, frozen subset of ring states. Only subsets on this list are eligible for
`MaximalIndividuating`/`OverlapsAnotherMaximal`/`FederatedEvidence` evaluation — this is the round-2
`Candidates`-restriction fix, and its own control (§4) checks an *undeclared* fragment is never
evaluated at all.

| candidate | states | intended demonstration |
| --- | --- | --- |
| `cand_integrated` | `{0, 1, 2}` | standalone maximal individuating candidate — `IntegratedCase` |
| `cand_subsidiary` | `{3, 4}` | repair+record closed, budget external — `SubsidiaryCase` |
| `cand_platform_dependent` | `{5, 6}` | all three closures hold, boundary maintained by another carrier — `PlatformDependentCase` |
| `cand_shadow` | `{7, 8}` | repair+budget closed, records closed elsewhere — `ShadowCase` |
| `cand_fed_a` | `{9}` | fails alone, closes only as part of `cand_coalition` — `FederatedCase` (coalition disjunct) |
| `cand_fed_b` | `{10}` | fails alone, closes only as part of `cand_coalition` — `FederatedCase` (coalition disjunct) |
| `cand_coalition` | `{9, 10}` | genuinely `MaximalIndividuating` — the coalition `cand_fed_a`/`cand_fed_b` join |
| `cand_overlap_x` | `{11, 12}` | independently `MaximalIndividuating`, overlaps `cand_overlap_y` — `FederatedCase` (overlap disjunct) |
| `cand_overlap_y` | `{12, 13}` | independently `MaximalIndividuating`, overlaps `cand_overlap_x` — `FederatedCase` (overlap disjunct) |
| `cand_non_individuated` | `{14}` | no attributed activity, no boundary candidate — `NonIndividuatedCase` |
| `cand_vacuous_attempt` | `{15}` | no attributed repair/budget/record witness at all — non-vacuity control |
| `cand_coarsest_control` | `{17, 18}` | genuine closure, but tested against a strictly finer boundary candidate too — coarsest-direction control |
| `cand_unlinked_control` | `{19}` | tests `AttributedToI`'s `tau n0` linkage against a decoy same-`rhoOf` state |
| `cand_bound_control` | `{24, 25}` | all closures + self-maintenance hold, but the only attempted boundary quotient is not sufficient — `Δ_bound` control (post-registration addition) |
| `cand_max_sub` | `{26, 27}` | individuates alone, but a strictly larger declared candidate also closes — `Δ_max` control (post-registration addition) |
| `cand_max_sup` | `{26, 27, 28}` | the strictly larger declared candidate that blocks `cand_max_sub`'s maximality — genuinely `integrated` itself |

`cand_overlap_x`/`cand_overlap_y` are deliberately **not** siblings inside one coalition (neither is a
proper subset of the other, and no third declared candidate `{11,12,13}` exists) — this is what makes
them the *overlap* disjunct demonstration rather than a second coalition-only demonstration. State `16`
is reserved as the undeclared "arbitrary fragment" (`{0}` reused, see §4) — it is deliberately **not**
added to `Candidates`.

### Repair/budget/record activity, per candidate

For each candidate above, the fixture constructs a small, explicit, finite list of attributed
occurrences (not a universal quantification over all ring transitions) — closure predicates are
existentials-then-universals over these constructed lists, exactly matching
`RepairClosedOn`/`BudgetClosedOn`/`RecordClosedOn`'s Lean shape:

| candidate | repair witness (source→target) | budget witness (feasible? funding entry carried under own policy?) | record witness (entry carried under own policy?) |
| --- | --- | --- | --- |
| `cand_integrated` | `0 → 1` (target in candidate) | feasible, funding entry carried under `cand_integrated`'s own policy | carried under own policy |
| `cand_subsidiary` | `3 → 4` (target in candidate) | feasible, but funding entry carried under an **external/parent** policy | carried under own policy |
| `cand_platform_dependent` | `5 → 6` (target in candidate) | feasible, carried under own policy | carried under own policy |
| `cand_shadow` | `7 → 8` (target in candidate) | feasible, carried under own policy | carried under an **external** policy |
| `cand_fed_a` | none attributed | none attributed | none attributed |
| `cand_fed_b` | none attributed | none attributed | none attributed |
| `cand_coalition` | `9 → 10` (target in candidate) | feasible, carried under own policy | carried under own policy |
| `cand_overlap_x` | `11 → 12` (target in candidate) | feasible, carried under own policy | carried under own policy |
| `cand_overlap_y` | `12 → 13` (target in candidate) | feasible, carried under own policy | carried under own policy |
| `cand_non_individuated` | none attributed | none attributed | none attributed |
| `cand_vacuous_attempt` | none attributed | none attributed | none attributed |
| `cand_coarsest_control` | `17 → 18` (target in candidate) | feasible, carried under own policy | carried under own policy |
| `cand_unlinked_control` | none needed (control is budget-only) | attributed via a `PolicyCarriedAt` occurrence at `n0` whose `tau n0 = 19` (in candidate), with a decoy state `20` (not in candidate) sharing the same `rhoOf` value | n/a |
| `cand_bound_control` | `24 → 25` (target in candidate) | feasible, carried under own policy | carried under own policy |
| `cand_max_sub` | `26 → 27` (target in candidate) | feasible, carried under own policy | carried under own policy |
| `cand_max_sup` | `26 → 27` (target in candidate) | feasible, carried under own policy | carried under own policy |

### Boundary candidates and viability probes

A single declared viability-probe family `viabilityProbes` is shared across all candidates: two probes
`v_lo`, `v_hi` that jointly distinguish exactly the coarse partition `{states < 12} / {states >= 12}`
plus a per-candidate refinement (each candidate's own two-class boundary quotient collapses "inside
candidate" vs "outside candidate"). For each candidate with a claimed boundary:

- `SufficiencyClosureCertified` holds for the candidate's own two-class quotient (both `v_lo`/`v_hi`
  descend through it, by construction).
- `CoarsestQuotientCertified` holds for the candidate's own two-class quotient **except** for
  `cand_coarsest_control`, which is also tested against a strictly finer three-class quotient (splitting
  "inside candidate" into two sub-classes) — the finer quotient is also sufficient, but the coarser
  two-class quotient must (and does) factor through it, confirming the fixed factorization direction
  (§6, falsifier 9).
- `cand_bound_control`'s *only* attempted boundary quotient collapses state `24` and state `25` (which
  have distinct declared `v_lo`/`v_hi` readouts) into the same class — `SufficiencyClosureCertified` is
  `False` for this quotient, and no other quotient is attempted, so `ViabilitySufficientBoundary` fails
  purely because of `Δ_bound`, with every other closure/self-maintenance condition genuinely holding
  (§6, falsifier 10).

### Self-maintenance (E3 reuse)

For every candidate with a claimed boundary except `cand_platform_dependent`, a genuine
`MaintenanceReinstatementRecord` is constructed (mirroring E3's own `MaintenanceReinstatementRecord`
dataclass fields exactly: `time, source_state, target_state, operator_record, pre_app_record,
post_app_record, output_record, reinstatement_ledger_entry`) whose `source_state` lies **inside** the
candidate. For `cand_platform_dependent`, the reinstatement record's `source_state` is pinned to state
`23` (a reserved "external platform operator" state, outside `{5,6}`) — `SelfMaintainedBoundary` fails
by construction because `I record.sourceState` fails, giving `PlatformDependentCase`.

### E4 forward interface

Not exercised in this landing's registered predictions — `ConstitutiveCase`/E4-compiled status is out
of scope for E12's own toy-lab (E4 has not landed; E12's certified `E4CompiledInstitutionalRewrite`
forward interface is exercised, if at all, only as a documented forward obligation, matching E11's own
treatment of its E4 forward reference).

## 2. Registered Theorem-Facing Predictions

### `E12_Individuation` / `E12_StatusPartition`, per candidate

```text
candidates = [cand_integrated, cand_subsidiary, cand_platform_dependent, cand_shadow,
              cand_fed_a, cand_fed_b, cand_coalition, cand_overlap_x, cand_overlap_y,
              cand_non_individuated, cand_vacuous_attempt, cand_coarsest_control,
              cand_bound_control, cand_max_sub, cand_max_sup]
```

| candidate | RepairClosedOn | BudgetClosedOn | RecordClosedOn | ViabilitySufficientBoundary | SelfMaintainedBoundary | registered status |
| --- | --- | --- | --- | --- | --- | --- |
| `cand_integrated` | True | True | True | True | True | `integrated` |
| `cand_subsidiary` | True | False | True | True | — | `subsidiary` |
| `cand_platform_dependent` | True | True | True | True | False | `platform_dependent` |
| `cand_shadow` | True | True | False | True | — | `shadow` |
| `cand_fed_a` | False | False | False | False | False | `federated` (coalition disjunct) |
| `cand_fed_b` | False | False | False | False | False | `federated` (coalition disjunct) |
| `cand_coalition` | True | True | True | True | True | `integrated` (this is the coalition itself, not federated — it is the maximal witness `cand_fed_a`/`cand_fed_b` join into) |
| `cand_overlap_x` | True | True | True | True | True | `federated` (overlap disjunct — `MaximalIndividuating` alone, but overlaps `cand_overlap_y`) |
| `cand_overlap_y` | True | True | True | True | True | `federated` (overlap disjunct — `MaximalIndividuating` alone, but overlaps `cand_overlap_x`) |
| `cand_non_individuated` | False | False | False | False | False | `non_individuated` |
| `cand_vacuous_attempt` | False (non-vacuity conjunct fails) | False (non-vacuity conjunct fails) | False (non-vacuity conjunct fails) | False | False | `non_individuated` |
| `cand_coarsest_control` | True | True | True | True (only for the coarsest quotient) | True | `integrated` |
| `cand_bound_control` | True | True | True | False (`Δ_bound`: attempted quotient is not sufficient) | True | `non_individuated` |
| `cand_max_sub` | True | True | True | True | True | `non_individuated` (`Individuates=True` but `MaximalIndividuating=False` — `Δ_max`: blocked by declared `cand_max_sup`) |
| `cand_max_sup` | True | True | True | True | True | `integrated` (the strictly larger declared candidate that blocks `cand_max_sub`) |

For `cand_coalition`: registering it as `integrated` (not a seventh status) is deliberate — E12.md's own
six-way partition has no "is a coalition" status distinct from `integrated`; a coalition, once it itself
closes maximally, individuates in the ordinary sense. `cand_fed_a`/`cand_fed_b` are the ones that read
as `federated` precisely because *they* fail to close alone while `cand_coalition` (a different,
separately-declared candidate) closes on their combined support.

## 3. Consolidation-Accounting Demonstration (recognized-instance anchor)

THEOREMS.md's own Recognition source cites "consolidation rules in accounting (when subsidiaries
consolidate = federation vs individuality, an existing formal codification of exactly this partition)."
`cand_fed_a`/`cand_fed_b`/`cand_coalition` is this instance directly: two candidate subsidiaries that
do not individually close, consolidated into a coalition that does — the accounting reading is
"consolidate the two subsidiaries' books; only the consolidated entity passes an individuation test,"
matching `FederatedCase`'s coalition disjunct exactly.

| regime | candidate | `Individuates` alone | `MaximalIndividuating` coalition exists | registered status |
| --- | --- | --- | --- | --- |
| unconsolidated | `cand_fed_a` | False | True (`cand_coalition`) | `federated` |
| unconsolidated | `cand_fed_b` | False | True (`cand_coalition`) | `federated` |
| consolidated | `cand_coalition` | True | — (it is itself the maximal witness) | `integrated` |

## 4. Null and Control Predictions

### Non-vacuity control (`cand_vacuous_attempt`)

No repair, budget, or record activity is attributed to `cand_vacuous_attempt` at all — no constructed
witness exists. `RepairClosedOn`/`BudgetClosedOn`/`RecordClosedOn` must each fail their own non-vacuity
existential conjunct (added during six-field review round 2 in response to a caught vacuity gap), not
vacuously hold. Registered: all three closures `False`, status `non_individuated`.

### Arbitrary-fragment exclusion control (undeclared `{0}`)

State `{0}` alone (a proper, undeclared subset of `cand_integrated`) is **not** a member of
`Candidates`. It is never evaluated by `OverlapsAnotherMaximal`/`FederatedEvidence`'s existentials
(both range over `candidates.members` only) — confirming the round-2 fix that an arbitrary fragment of
an already-integrated candidate cannot be independently classified `federated` (or anything else). No
status is registered for `{0}` because it is not a candidate; the control is that the sweep's own
candidate-enumeration loop skips it by construction, not that it evaluates to some particular status.

**External-review-gate addition (v22 CHANGE-REQUEST fix):** the enumeration-skip control above shows
the sweep's own registered-comparison loop never visits `{0}`, but it does not by itself show the
*classifier* would reject a constructed attempt to certify a status for it. External review v22 found
this gap: `Candidates`-restriction was threaded into `MaximalIndividuating`/`OverlapsAnotherMaximal`/
`FederatedEvidence`, but not into `IndividuationStatusOccurrenceFor` or the lower-priority case
predicates, so a host that supplied a fully carried, well-formed `IndividuationStatusRecord` for an
undeclared subcarrier could in principle still have it recognized. Fixed by adding
`I ∈ candidates.members` as `IndividuationStatusOccurrenceFor`'s own first conjunct — this propagates
to all six `...Holds` predicates and both theorems, since none of them can be satisfied without a
genuine occurrence witness. A dedicated regression
(`test_e12_status_occurrence_rejects_carried_undeclared_fragment`) now constructs exactly such a
carried, well-formed status record for `{0}` — satisfying every other check (carried occurrence,
ledger/audit membership, admissible source tag, `generatedByS=true`, `inScope=true`) — and confirms
`IndividuationStatusOccurrenceFor`/`individuation_status_occurrence_for` reject it solely because it is
not a declared candidate. This did not change any of the 19 registered comparisons' outcomes, since
every registered candidate is already declared.

### Coarsest-quotient direction control (`cand_coarsest_control`)

Two boundary-quotient candidates are checked for `cand_coarsest_control = {17, 18}`: the genuine
two-class quotient (`inside` vs `outside`) and a strictly finer three-class quotient (splitting
`inside` into `{17}` and `{18}` separately). Both are `SufficiencyClosureCertified` (both let the
declared probes descend). Only the two-class quotient is `CoarsestQuotientCertified` — the finer
three-class quotient must **fail** `CoarsestQuotientCertified` (it is sufficient but not coarsest, since
it does not factor through the two-class quotient the way the two-class quotient factors through it).
Registered: two-class quotient's `CoarsestQuotientCertified = True`, three-class quotient's
`CoarsestQuotientCertified = False`.

### Unlinked-evidence / `tau n0` linkage control (`cand_unlinked_control`)

A `PolicyCarriedAt` occurrence is carried at index `n0` with `tau n0 = 19` (inside
`cand_unlinked_control = {19}`). A decoy state `20` (outside the candidate) is constructed so that
`accessPolicyRecord.rhoOf 20 == accessPolicyRecord.rhoOf 19` (same policy value, different state) — the
exact scenario the round-1 Lean review caught as an unlinked-evidence bug. Registered:
`AttributedToI` evaluates `I (tau n0) = I 19 = True` (the genuine carried state), **not** `I 20` (the
decoy) — attribution succeeds because the fix correctly reads the real carried state, and the control
would have wrongly succeeded either way here (both are memberships that happen to hold), so a second
sub-case is also registered: a mirrored construction where `tau n0 = 20` (outside the candidate) and
the decoy state is `19` (inside) — here attribution **must fail** (`I 20 = False`), and would have
wrongly *succeeded* under the pre-fix definition (which checked the decoy `sourceState` via
`rhoOf`-equality, not `tau n0` directly). This second sub-case is the falsifying one; both are
registered as `AttributedToI` values in §6's falsification list.

## 5. Scope Note: Actual Carried Candidate vs. Existential Feasible Subcarrier

Following E1/E2/E3/E11's own precedent, the sweep must check status against `ActualCarriedCandidate`
(a genuinely constructed, attributed, carried-record-backed subcarrier from the fixture's own finite
inventory) and never substitute `ExistentialFeasibleSubcarrier` (some subset that merely *could*
satisfy closure in principle, without genuine constructed occurrence evidence). Every closure witness
in §1's activity table is a concretely constructed dataclass instance with real field values, not an
assumed/hypothetical one — this is the same discipline E3's `MaintenanceReinstatementRecord` and E11's
`InstitutionalStructuralEffect` fixtures already enforce.

## 6. Falsification Conditions

1. `E12_Individuation`/`E12_StatusPartition` is falsified for `cand_integrated` if any of
   `RepairClosedOn`/`BudgetClosedOn`/`RecordClosedOn`/`ViabilitySufficientBoundary`/
   `SelfMaintainedBoundary` is computed `False` from the constructed witnesses, or if
   `IntegratedHolds` is not the unique `...Holds` predicate reported true.
2. Falsified for `cand_subsidiary` if `BudgetClosedOn` is computed `True` (the funding entry is
   deliberately carried under an external policy — it must fail `EntryClosedOn`), or if
   `SubsidiaryHolds` is not the unique `...Holds` predicate reported true.
3. Falsified for `cand_platform_dependent` if `SelfMaintainedBoundary` is computed `True` (the
   reinstatement record's `sourceState = 23` is deliberately outside `{5,6}`), or if
   `PlatformDependentHolds` is not the unique `...Holds` predicate reported true.
4. Falsified for `cand_shadow` if `RecordClosedOn` is computed `True` (the ledger entry is deliberately
   carried under an external policy), or if `ShadowHolds` is not the unique `...Holds` predicate
   reported true.
5. Falsified for `cand_fed_a`/`cand_fed_b` if either is reported `IntegratedHolds`, or if
   `FederatedHolds` is reported via the *overlap* disjunct rather than the *coalition* disjunct, or if
   `cand_coalition` itself is not reported `IntegratedHolds`.
6. Falsified for `cand_overlap_x`/`cand_overlap_y` if either is reported `IntegratedHolds` (both are
   individually `MaximalIndividuating`, so this failure mode is the one the round-2
   `OverlapsAnotherMaximal` fix specifically targets), or if `FederatedHolds` is reported via the
   *coalition* disjunct rather than the *overlap* disjunct.
7. Falsified for `cand_non_individuated`/`cand_vacuous_attempt` if any `...Holds` predicate other than
   `NonIndividuatedHolds` is reported true, or if `cand_vacuous_attempt`'s closure predicates are
   computed `True` despite no constructed activity witness existing (a reintroduction of the six-field
   review's own caught vacuity gap).
8. Falsified if the undeclared fragment `{0}` is ever assigned any status at all, or if
   `OverlapsAnotherMaximal`/`FederatedEvidence`'s coalition existential is satisfied by a witness not
   drawn from `candidates.members`.
9. Falsified if `cand_coarsest_control`'s finer three-class quotient is computed
   `CoarsestQuotientCertified = True`, or if the coarser two-class quotient is computed
   `CoarsestQuotientCertified = False`.
10. Falsified if `cand_unlinked_control`'s `AttributedToI` check is computed using the decoy state's
    identity rather than `tau n0`'s actual value in either sub-case (i.e. if attribution ever succeeds
    when `tau n0` lies outside the candidate, regardless of a same-`rhoOf` decoy inside it).
11. **(post-registration addition)** Falsified for `cand_bound_control` if `ViabilitySufficientBoundary`
    is computed `True` (its one attempted quotient is deliberately not
    `SufficiencyClosureCertified`), if any other closure or `SelfMaintainedBoundary` is computed `False`
    (the control must isolate `Δ_bound` as the *only* failing condition), or if the final status is
    anything other than `non_individuated`.
12. **(post-registration addition)** Falsified for `cand_max_sub`/`cand_max_sup` if `cand_max_sub` is
    computed `MaximalIndividuating = True` (it must fail specifically because `cand_max_sup` is a
    declared strict superset that also individuates), if `Individuates cand_max_sub` is computed
    `False` (the control must isolate `Δ_max` — maximality, not base closure — as the failing
    condition), or if `cand_max_sup` is not reported `integrated`.
13. Falsified if any candidate's registered status is asserted without a genuine carried
    `IndividuationStatusRecord` occurrence backing it (an `ExistentialFeasibleSubcarrier`-style
    shortcut, per §5).
14. Falsified if the total registered comparison count reported by the sweep does not match this
    document's own candidate count (15 candidates, plus the 2 quotient variants inside
    `cand_coarsest_control` and the 2 sub-cases inside `cand_unlinked_control` — 19 total registered
    checks).
