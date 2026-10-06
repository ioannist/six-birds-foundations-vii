# Foundations VII semantic models report

Toolchain: Lean 4.28.0, library `FoundationsVII`, no Mathlib. The semantic extension is confined to new `FoundationsVII/Semantics/*` modules and append-only imports in `FoundationsVII/All.lean`; this report records both the earlier and task M results.

## Declarations and mathematical statements

### `Semantics/Rewriting.lean`

| Declaration | Statement or meaning |
|---|---|
| `Star`, `Star.refl`, `Star.cons` | Reflexive transitive closure of an arbitrary one-step relation. |
| `Star.single`, `Star.trans` | One step is a path; paths concatenate. |
| `Joinable` | Two states have a common reachable successor. |
| `LocallyConfluent` | Every one-step peak is joinable. |
| `Confluent` | Every finite-path peak is joinable. |
| `Terminates` | The converse of one-step reduction is well founded. |
| `Normal` | A state has no outgoing step. |
| `join_of_stars` (private), `newman` | Well-founded induction propagates local joins to arbitrary peaks; termination and local confluence imply confluence. |
| `normal_star_eq` | A path from a normal state has length zero. |
| `normal_forms_unique` | Any two normal descendants of a common state coincide under confluence; termination is not needed for uniqueness. |
| `reaches_normal` (private) | Every state in a terminating system reaches a normal state. |
| `unique_reachable_normal` | Under termination and confluence, each state reaches exactly one normal state. |
| `allSubsets`, `filter_mem_allSubsets` | Enumerate every sublist; filtering any Boolean predicate gives one of them. |
| `finiteClosedCheck`, `finiteClosedCheck_correct` | Decide whether a candidate set is closed under every enumerated one-step edge. |
| `finiteReachCheck`, `finiteReachCheck_correct` | Search all candidate closed sets. A state is reachable exactly when it belongs to every forward-closed set containing the start. |
| `finitePeakCheck`, `finitePeakCheck_correct` | The original peak scan remains available with an explicit joinability decider. |
| `finiteJoinCheck`, `finiteJoinCheck_correct`, `finiteJoinDecision` | Search the carrier for a common reachable successor and thereby decide joinability. |
| `finitePeakCheckComplete`, `finitePeakCheckComplete_correct` | Decide local confluence from a covering list, decidable equality, and decidable one-step relation alone. |
| `finitePeakCheckFin`, `finitePeakCheckFin_correct` | The same criterion for `Fin n` needs only the decidable step relation; its carrier list and equality decider are canonical. |
| `Four`, `fourStep`, its `DecidableRel` instance | Four states with precisely `b→a`, `b→c`, `c→b`, `c→d`. |
| `four_local`, `four_not_confluent` | This system is locally confluent but not confluent. |

### `Semantics/Admission.lean`

| Declaration | Statement or meaning |
|---|---|
| `AdmissionRules` | A prerequisite relation and audit map on finite lists of pending items; an item is admitted when removed from the list. |
| `AdmissionRules.Enabled`, `AdmissionRules.Step` | An item can be removed if pending and every prerequisite is already absent. |
| `AdmissionRules.step_preserves_nodup`, `AdmissionRules.star_preserves_nodup` | If the initial pending list represents a finite set (no duplicates), every admission path preserves that invariant. |
| `AdmissionRules.terminates` | Every step shortens the pending list, hence no infinite admission run exists. |
| `AdmissionRules.enabled_after_other` (private) | Removing another pending item preserves an enabled admission. |
| `AdmissionRules.commuting_admissions` | Two admissions from one state either coincide or commute to an equal list by one further step each. |
| `AdmissionRules.locallyConfluent`, `AdmissionRules.confluent` | Commutation gives local confluence; Newman gives confluence. |
| `AdmissionRules.unique_fixed_point` | From any starting list every maximal admission order reaches the same normal list, with the same audit label. |
| `TwoItem`, `freeRules`, `free_example` | Two unconstrained items can both be admitted, reaching the empty fixed point. |
| `disablingStep`, `disabling_terminates` | A guarded two-item system where admitting `a` disables `b`; it still terminates. |
| `disabling_not_local`, `disabling_two_fixed_points` | Its initial peak cannot be joined; two orders reach distinct terminal lists `[b]` and `[]`, with different length audits. |

### `Semantics/Join.lean`

| Declaration | Statement or meaning |
|---|---|
| `TheoryPackage`, `SemanticJoin`, `PackageJoin` | A carrier with an observable map; a join carrier with maps to both parent carriers. |
| `Factors` | Global factorization: `f = g ∘ q` for some map `g` on the entire codomain of `q`. |
| `FactorsOnImage` | Factorization by a map defined on the reached image of `q`. |
| `factors_implies_onImage` | Global factorization restricts to the reached image. |
| `SplitPair` | Two join states have equal `q` values but different `f` values. |
| `factorsOnImage_iff_no_split` | Factorization on the reached image is equivalent to absence of split pairs. |
| `FiniteSplitCheck`, `finiteSplitCheck_correct` | For a covering finite list and decidable value equality, the Boolean scan detects exactly the split pairs. |
| `CommonRefinement` | A map `q : J → R` retains the pair of parental observations via `R → A × B`. |
| `factors_through_pair_of_refinement` | A factorization through the parental pair also factors through every such refinement. |
| `StrictObservable`, `strict_iff_split_pairs` | Strictness means nonfactorization on the reached image through either parent or the pair; equivalently each map has a split pair. |
| `cubeJoin`, `cubeObservable`, `boolPackage`, `cubePackageJoin` | A three-Boolean join whose parent maps read the first two coordinates and whose observable reads the third. |
| `cube_strict`, `cube_first_not_strict` | The third coordinate is strict; the first coordinate is not. |
| `identity_refinement_recovers_cube` | The identity map is a common refinement and recovers the cube observable, despite cube strictness. |
| `RelabelOnly`, `SchedulingOnly`, `CoarseningOnly` | Relabelling means the observable factors through a bijective recoding of the parental pair; scheduling means it factors through a declared schedule coordinate; coarsening means it factors through a map out of either parent. |
| `split_composition`, `strict_not_relabel`, `strict_not_coarsening` | A split pair survives postcomposition, so strictness rules out relabelling and parent coarsening. |
| `semanticFlag`, `semanticFlag_true`, `semanticFlag_false` | Evaluate a semantic proposition into a Boolean; proofs of truth or falsity determine the flag. |
| `SemanticStrictEvidence` | A proof bundle containing strictness, a genuine common-refinement witness, refinement nonfactorization, and schedule nonfactorization. |
| `strictCertificate`, `strictCertificate_valid` | Construction requires that proof bundle; every Boolean flag evaluates its corresponding semantic predicate. The bundle proves full `Valid`. |
| `cubeEvidence` (private), `cubeCertificate_valid` | The cube supplies the proof bundle and a valid certificate when the declared refinement is the parental pair and the schedule coordinate is the first parent. |

## Build and trust

Command: `cd formalization/lean && lake build FoundationsVII`.

Build result: **PASS** (171 jobs), after the review fixes. The three new modules also built separately. `git diff --check` passed. No `sorry`, `axiom`, `admit`, or `native_decide` occurs in the new sources.

Every new theorem, including private helpers, was checked with `#print axioms`. Exact output:

```text
'FoundationsVII.Semantics.Star.single' does not depend on any axioms
'FoundationsVII.Semantics.Star.trans' does not depend on any axioms
'FoundationsVII.Semantics.newman' does not depend on any axioms
'FoundationsVII.Semantics.normal_star_eq' does not depend on any axioms
'FoundationsVII.Semantics.normal_forms_unique' does not depend on any axioms
'FoundationsVII.Semantics.unique_reachable_normal' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.filter_mem_allSubsets' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.finiteClosedCheck_correct' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.finiteReachCheck_correct' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.finitePeakCheck_correct' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.finiteJoinCheck_correct' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.finitePeakCheckComplete_correct' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.finitePeakCheckFin_correct' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.four_local' depends on axioms: [propext]
'FoundationsVII.Semantics.four_not_confluent' depends on axioms: [propext]
'FoundationsVII.Semantics.AdmissionRules.step_preserves_nodup' depends on axioms: [propext]
'FoundationsVII.Semantics.AdmissionRules.star_preserves_nodup' depends on axioms: [propext]
'FoundationsVII.Semantics.AdmissionRules.terminates' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.AdmissionRules.commuting_admissions' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'FoundationsVII.Semantics.AdmissionRules.locallyConfluent' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.AdmissionRules.confluent' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.AdmissionRules.unique_fixed_point' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.free_example' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.disabling_terminates' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.disabling_not_local' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.disabling_two_fixed_points' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.factors_implies_onImage' does not depend on any axioms
'FoundationsVII.Semantics.factorsOnImage_iff_no_split' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.finiteSplitCheck_correct' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.factors_through_pair_of_refinement' depends on axioms: [propext]
'FoundationsVII.Semantics.strict_iff_split_pairs' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.cube_strict' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.cube_first_not_strict' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.identity_refinement_recovers_cube' does not depend on any axioms
'FoundationsVII.Semantics.split_composition' does not depend on any axioms
'FoundationsVII.Semantics.strict_not_relabel' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.strict_not_coarsening' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.semanticFlag_true' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.semanticFlag_false' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.strictCertificate_valid' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.cubeCertificate_valid' depends on axioms: [propext, Classical.choice, Quot.sound]
'_private._stdin.0.FoundationsVII.Semantics.join_of_stars' does not depend on any axioms
'_private._stdin.0.FoundationsVII.Semantics.reaches_normal' depends on axioms: [propext, Classical.choice, Quot.sound]
'_private._stdin.0.FoundationsVII.Semantics.AdmissionRules.enabled_after_other' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'_private._stdin.0.FoundationsVII.Semantics.cubeEvidence' depends on axioms: [propext, Classical.choice, Quot.sound]
```

`Classical.choice` in `finiteReachCheck_correct` is used only in the proof to identify the set of semantically reachable states; the Boolean checker itself exhaustively enumerates candidate subsets and uses decidable equality and step. Choice in `reaches_normal` selects a successor of an abstract terminating relation. Choice in `factorsOnImage_iff_no_split` selects a representative of each reached fibre. The admission theorems inherit `Classical.choice` from Lean core's `List.erase` lemmas. `semanticFlag` uses classical proposition decidability to translate the semantic predicate into the existing Boolean certificate format. The only reported axioms are `propext`, `Quot.sound`, and `Classical.choice`.

## Scope and needed hypotheses

- The finite search uses a covering list and decidable equality; for `Fin n`, equality and the covering list are supplied automatically. Its runtime can be exponential because it enumerates all sublists.
- Strictness against the two parents and their pairing does not imply nonfactorization through every richer common refinement. The cube's identity refinement is a checked counterexample. `strictCertificate_valid` therefore requires both `CommonRefinement` and a separate nonfactorization proof for the declared refinement.
- `SchedulingOnly` is relative to an explicitly declared schedule coordinate. An arbitrary coordinate, including identity on the join carrier, can recover an observable; the full certificate requires a proof that the declared schedule does not.
- The admission fixed point is relative to the starting pending list and prerequisite rules. Cyclic prerequisites can leave a nonempty terminal list. Equal terminal lists have equal audit labels for any audit map on states.

## Task M: semantic replacements

### M1 — C015, downward selection

`Semantics/Selection.lean` models a lower state as a predicate on facts. A selection step intersects the current facts with a keep predicate. Induction over the actual reflexive transitive transition relation proves that every fact after any finite selection run was present before. Inserting a fact into the empty state is a concrete counterexample when the step is allowed to insert. **Grade: instantiated weakly; a scoped run invariant for an intersection-only selection class.** It says nothing about transformations outside that class.

### M2 — C035, no free join

`Semantics/Precedence.lean` defines a lawful finite event run by appending only events whose requirements are initially available or produced by an earlier listed event. If a join requires capability `c`, `c` is not initially available, and only that join produces `c`, induction on the run proves the join is absent everywhere in it. A one-event run becomes lawful when `c` is initially supplied. **Grade: general finite precedence theorem with explicit sole-producer and no-external-source premises.** Concurrency and capability revocation are outside this model.

### M3 — semantic separations

`Semantics/Separations.lean` exhibits an actual formation transition from `false` to `true`; the state observable cannot descend through a map that collapses both states. For the existing cube join, both the parental-pair map and identity map are common refinements. The third-coordinate observable fails to factor through the former and factors through the latter. **Grade: instantiated weakly; observable factorization countermodels only.** This does not establish full join preservation under refinement or two-theory enablement.

### M4 — C021/C033, finite search

`Semantics/Search.lean` defines bounded reachability from a transition relation and a list-scanning detector. A sound enumeration makes positive detection yield an actual bounded witness; coverage makes a negative scan exclude every bounded witness. If every longer reachable state is already within the declared horizon, the null extends globally. One Boolean system reaches contact after one step but not at horizon zero. A second has a genuine contact state in its carrier but no transition to it, and its global no-contact conclusion follows from coverage and closure. **Grade: conditional search methodology, instantiated weakly in the original one-theory examples; the global null requires proved horizon closure.** A bounded null alone is not global.

## Task M build and axiom receipt

`cd formalization/lean && lake build FoundationsVII` **PASS** (175 jobs). `#print axioms` was run for every new theorem (25 total):

```text
'FoundationsVII.Semantics.selection_step_preserves' does not depend on any axioms
'FoundationsVII.Semantics.selection_run_preserves' does not depend on any axioms
'FoundationsVII.Semantics.insertion_creates_fact' does not depend on any axioms
'FoundationsVII.Semantics.insertion_not_selection' does not depend on any axioms
'FoundationsVII.Semantics.sole_producer_join_absent' depends on axioms: [propext]
'FoundationsVII.Semantics.external_source_allows_join' does not depend on any axioms
'FoundationsVII.Semantics.external_source_join_occurs' depends on axioms: [propext]
'FoundationsVII.Semantics.formation_enabled' does not depend on any axioms
'FoundationsVII.Semantics.enabled_observable_not_descended' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.coarse_refinement_loses_cube' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.fine_refinement_retains_cube' does not depend on any axioms
'FoundationsVII.Semantics.detector_sound' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.detector_coverage' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.beyond_horizon_null' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.no_contact_in_covered_family' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.zero_horizon_coverage' depends on axioms: [propext]
'FoundationsVII.Semantics.zero_horizon_null' does not depend on any axioms
'FoundationsVII.Semantics.later_witness' does not depend on any axioms
'FoundationsVII.Semantics.one_horizon_sound' does not depend on any axioms
'FoundationsVII.Semantics.one_horizon_detects_contact' does not depend on any axioms
'FoundationsVII.Semantics.detected_contact_witness' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.all_bool_covered' depends on axioms: [propext]
'FoundationsVII.Semantics.stuck_reach_only_false' does not depend on any axioms
'FoundationsVII.Semantics.stuck_closed_at_zero' does not depend on any axioms
'FoundationsVII.Semantics.concrete_no_contact' depends on axioms: [propext, Quot.sound]
```

No new theorem uses `sorry`, `axiom`, `admit`, or `native_decide`. The reported dependencies are Lean's standard `propext`, `Classical.choice`, and `Quot.sound` where shown.

## Task M, round 2

### R1 — two-theory enablement without descent

`Semantics/Enablement.lean` gives lower theory A the states `Fin 3` and strict-order transitions. Upper theory B has exactly the reachable-state vectors formed from A seeds; the correspondence between a vector entry and one-step lower reachability is proved. The formation map is bijective onto these three reachable-state vectors, so B has exactly three distinct states. The upper transition agrees with the lower transition on formed states. An upper transition is induced by a lower transition, and the transition from the vector at 0 to the vector at 1 exists and changes state. The lower quotient reads whether state 1 is reachable, and the upper quotient commutes with formation; the observable reads whether state 0 is reachable. The two formed states have the same quotient value and different observable values, giving a split pair and refuting factorization on the quotient image. Fibre constancy gives a general sufficient condition for positive descent. **Grade: concrete two-theory semantic separation for formation enablement and observable descent.** It does not formalize every notion of causal enablement or full theory-package descent.

### R2 — joint-state rendezvous under a step budget

`Semantics/ChannelSearch.lean` gives each Boolean theory a genuine `false → true` transition. One channel use advances exactly one side; the use count is the `ReachWithin` horizon. Contact means reaching a pair related by the channel, here `(true, true)`. Structural coverage proves that within one use only `(false, false)`, `(true, false)`, and `(false, true)` can occur. The detector scans that list and returns false; `no_contact_in_covered_family` derives no contact within budget one. Two uses produce a related pair. **Grade: joint-state, step-budget example (instantiated weakly).** Each step advances one component independently, and "contact" is only the joint state `(true, true)`; there is no crossing event and no channel that carries contact between the two theories. It is therefore a bounded rendezvous example, a partial model of C033's contact channels, not a non-interaction theorem for them. No global non-interaction follows from the one-use result.

### R3 — corrected scope and trust

The round-one grades for M1, M3, and M4 above are downgraded as requested. M3's cube result concerns observable factorization only. Task M round 2 changed no existing theorem statements.

`cd formalization/lean && lake build FoundationsVII` **PASS** (177 jobs). `#print axioms` was run for all 18 round-two theorems:

```text
'FoundationsVII.Semantics.lower_reachable_iff' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.lower_supplies_upper' does not depend on any axioms
'FoundationsVII.Semantics.upper_requires_lower' does not depend on any axioms
'FoundationsVII.Semantics.form_injective' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.form_surjective' does not depend on any axioms
'FoundationsVII.Semantics.upper_step_iff_lower' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.three_distinct_upper_states' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.nontrivial_upper_formation' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.quotient_commutes_with_formation' depends on axioms: [propext]
'FoundationsVII.Semantics.enabled_not_descended' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.observable_descends_of_fibre_constant' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'FoundationsVII.Semantics.quotient_observable_descends' depends on axioms: [propext, Classical.choice, Quot.sound]
'FoundationsVII.Semantics.zero_channel_reach_eq' does not depend on any axioms
'FoundationsVII.Semantics.one_channel_coverage' depends on axioms: [propext]
'FoundationsVII.Semantics.one_channel_negative_scan' does not depend on any axioms
'FoundationsVII.Semantics.no_contact_with_one_use' depends on axioms: [propext, Quot.sound]
'FoundationsVII.Semantics.two_channel_uses_reach_contact' does not depend on any axioms
'FoundationsVII.Semantics.contact_with_two_uses' does not depend on any axioms
```

Only Lean's standard `propext`, `Quot.sound`, and `Classical.choice` occur in this receipt.
