# Canonical SBT glossary and VII provisional vocabulary

Preferred terms are controlled by the deepest explicit definitions in Foundations II–VI. Rows marked `wishlist-provisional` are not silently promoted to established SBT vocabulary.

## theory package
**Status:** canonical.  
A typed package `(Z, f, Σ_f, E, A)` comprising carrier, declared lens, induced definability structure, packaging/completion endomap, and audit. Variants may add dynamics or records but must not silently replace these fields.

- **Source:** P030, lines/section `302-312`, `def:theory-package`.
- **Aliases/history:** package; closure package.
- **Do not collapse:** A theory package is not merely a model description; formation claims require fixed-point and audit records.

## carrier
**Status:** canonical.  
The underlying finite state/content domain `Z` on which the package is defined.

- **Source:** P030, lines/section `302-312`, `def:theory-package`.
- **Aliases/history:** substrate; state space.
- **Do not collapse:** Carrier identity, theory identity, and layer identity are distinct.

## lens
**Status:** canonical.  
A declared map/interface `f` specifying what distinctions are available to the package.

- **Source:** P030, lines/section `302-312`, `def:theory-package`.
- **Aliases/history:** readout; coarse graining; interface.
- **Do not collapse:** A lens may be partial in future VII work, but the existing canonical package does not by itself supply a partial-domain calculus.

## definability structure
**Status:** canonical.  
`Σ_f`, the family/algebra of distinctions expressible through the declared lens.

- **Source:** P030, lines/section `302-312`, `def:theory-package`.
- **Aliases/history:** definability algebra; observable algebra.
- **Do not collapse:** Definability is lens-relative; hidden carrier distinctions are not automatically layer facts.

## completion / packaging endomap
**Status:** canonical.  
The endomap `E` whose fixed points supply packaged candidates and whose idempotence/defect is audited.

- **Source:** P031, lines/section `460-590`, `def:closed-points; def:D-IC-02`.
- **Aliases/history:** completion; packaging operator.
- **Do not collapse:** Iterating one fixed idempotent does not generate an open-ended ladder.

## audit
**Status:** canonical.  
The record/check functional `A` and surrounding provenance discipline under which a package or claim is accepted.

- **Source:** P027, lines/section `671-920`, `def:audited; def:admissible-claim`.
- **Aliases/history:** bookkeeping; ledger; provenance.
- **Do not collapse:** Audit is constitutive of admissibility, but SBT is not reducible to audit.

## formed object
**Status:** canonical.  
A declared fixed point of completion with its associated formation, record, and audit conditions included in the package.

- **Source:** P030, lines/section `302-312`, `def:theory-package`.
- **Aliases/history:** object; packaged object.
- **Do not collapse:** Fixed-point syntax alone is not sufficient when formation records or audits are absent.

## objecthood / stability certificate
**Status:** canonical synthesis.  
Evidence that a candidate survives the declared packaging/completion operation, exactly or within a declared defect tolerance.

- **Source:** P031, lines/section `359-590`, `def:closure-operator; def:closed-points; def:D-IC-02`.
- **Aliases/history:** closure certificate.
- **Do not collapse:** Objecthood is separate from novelty and directionality.

## strict extension / novelty certificate
**Status:** canonical.  
A refinement/new package retains the lower readout and separates at least one lower-indistinguishable pair; equivalently, the new readout does not factor through the old.

- **Source:** P028, lines/section `1963`, `lem:F8`.
- **Aliases/history:** strictness; nonfactorization.
- **Do not collapse:** Strictness alone does not imply closure, promotion acceptance, endogeny, or drive.

## directionality certificate
**Status:** canonical synthesis.  
An accepted P6-side audit of time-reversal asymmetry or non-exact affinity that survives the declared observation/protocol conditions.

- **Source:** P031, lines/section `710-920`, `arrow/affinity section`.
- **Aliases/history:** arrow; drive.
- **Do not collapse:** Route mismatch or holonomy alone is not directionality.

## P6_drive
**Status:** canonical specialization.  
The affinity-carrying, detailed-balance-breaking face of P6 used for honest directionality claims.

- **Source:** P027, lines/section `295-303`, `rem:p6-drive`.
- **Aliases/history:** drive face.
- **Do not collapse:** It is a specialization of P6, not a seventh role and not a replacement for general audit.

## closure ladder
**Status:** canonical.  
An ordered sequence of closures/packages in which later stages are strictly stronger; open-endedness requires changing or enlarging operators/interfaces rather than repeated application of one idempotent.

- **Source:** P031, lines/section `393-450`, `def:closure-ladder`.
- **Aliases/history:** layer ladder.
- **Do not collapse:** Finite fixed interfaces have bounded definability and cannot support an infinite strict ladder.

## level trichotomy
**Status:** canonical.  
Behavioral status, verification/certificate, and structural-categorical support are three lossy levels for each primitive role.

- **Source:** P027, lines/section `305-352`, `def:level-trichotomy`.
- **Aliases/history:** behavioral/verification/structural levels.
- **Do not collapse:** Lifts upward require added data and are selected, not unique.

## FATCD
**Status:** canonical scoped domain.  
The finite audited typed closure-description domain over which Foundations II proves its scoped exact-six theorem.

- **Source:** P027, lines/section `1030-1160`, `def:fatcd`.
- **Aliases/history:** finite audited typed closure descriptions.
- **Do not collapse:** Membership does not require all six role projections to be active.

## role channel
**Status:** canonical.  
One of exactly six typed slots in a decomposition/exhaustion record; a channel may be inactive, below threshold, collapsed, absent-with-record, or out of scope.

- **Source:** P027, lines/section `1419; 2379`, `rem:channel-vs-activation-reminder`.
- **Aliases/history:** primitive channel.
- **Do not collapse:** Channel presence is not role activation.

## active role projection
**Status:** canonical.  
An honestly supported interpretation of raw features as one P-role, carrying threshold, witness, level, evidence, collapse, loss/lift, and nonclaim data.

- **Source:** P027, lines/section `1208-1245`, `def:role-projection`.
- **Aliases/history:** activation.
- **Do not collapse:** A FATCD description may activate none, some, or all six channels.

## scoped exact-six
**Status:** canonical theorem scope.  
Within FATCD and an explicit recognition hypothesis, every admissible description has an existential, non-unique decomposition/exhaustion record with six role channels and no required seventh irreducible role in the covered scope.

- **Source:** P027, lines/section `2715-3030`, `thm:scoped-exact-six`.
- **Aliases/history:** exact six.
- **Do not collapse:** Not a universal algebra, uniqueness theorem, empirical realization, or claim that every description activates all six.

## BirdInt_fin^aud
**Status:** canonical calculus.  
The finite audited typed interaction record/calculus carrying packages, instruments, profiles, witnesses, updates, defects, judgments, statuses, gates, dependencies, audits, visibility, sources, nonclaims, and model realizations.

- **Source:** P026, lines/section `800-816; 1452-1478`.
- **Aliases/history:** BirdInt; finite audited interaction calculus.
- **Do not collapse:** It is not a category, algebra, or closure operator. The body’s 19-field declaration controls an inconsistent 16-field appendix shorthand.

## directed cell
**Status:** canonical.  
A typed judgment `P_i ← P_j` in which actor `P_i` consumes informant witness data from `P_j` through a typed update under package, profile, visibility, threshold, defect, and audit records.

- **Source:** P026, lines/section `1538-1600`.
- **Aliases/history:** cell action.
- **Do not collapse:** Pair order matters; a cell action does not make the unordered pair observable real.

## pair observable
**Status:** canonical.  
A separate unordered-pair judgment with joint source-of-truth and branch-compatibility obligations.

- **Source:** P026, lines/section `1626-1666`.
- **Aliases/history:** pair record.
- **Do not collapse:** A real/action cell does not imply a real pair observable; fallback/proxy sources are at most provisional unless explicitly upgraded.

## promotion bridge
**Status:** canonical.  
A finite typed bridge from a source package to a target package, classified only after required gates and audit records are present.

- **Source:** P026, lines/section `1670-1745`.
- **Aliases/history:** promotion.
- **Do not collapse:** Strict bridge data is separate from target closure and drive.

## status family
**Status:** canonical.  
A typed classifier codomain tied to one judgment family; BirdInt keeps Role, Cell, Pair, Promotion, Claim, Gate, and Square statuses separate.

- **Source:** P026, lines/section `180-194; 1518-1666`.
- **Aliases/history:** status.
- **Do not collapse:** Status values cannot be transported between families by name resemblance.

## access quotient
**Status:** canonical.  
The coarsest quotient carrying the observations declared by an instrument/interface.

- **Source:** P028, lines/section `714`, `thm:F10`.
- **Aliases/history:** observable quotient.
- **Do not collapse:** Layer claims must factor through the access quotient unless extra apparatus is declared.

## adequacy / no-overread
**Status:** canonical law.  
An exact current-layer claim must be constant on access fibers and therefore factor through the access quotient.

- **Source:** P028, lines/section `839`, `thm:F11`.
- **Aliases/history:** adequacy.
- **Do not collapse:** A true carrier fact may still be inadmissible as a current-layer claim.

## no-free-distinction
**Status:** canonical law.  
A strict visible distinction cannot be produced from the existing access quotient alone; additional memory, bridge, residual budget, scope, or calibration data must be declared.

- **Source:** P028, lines/section `952`, `thm:F12`.
- **Aliases/history:** anti-smuggling.
- **Do not collapse:** This is adjacent to, but does not yet settle, a VII no-free-access theorem.

## descent obstruction
**Status:** canonical.  
The split-pair set of lower-equivalent points whose transported/readout values disagree; emptiness is equivalent to descent.

- **Source:** P028, lines/section `2307`, `thm:F2`.
- **Aliases/history:** split-pair obstruction.
- **Do not collapse:** Canonical repairs are source refinement or minimal target coarsening.

## common quotient / objectivity
**Status:** canonical law.  
A public quotient universal across declared access quotients; objectivity means a readout is common across accesses and determined by that public quotient.

- **Source:** P028, lines/section `3676`, `thm:F17`.
- **Aliases/history:** public quotient.
- **Do not collapse:** Common source and common quotient are not the same as common access or a strict join.

## common refinement / unification
**Status:** canonical law.  
A theory/package refining multiple lower packages under declared bridge conditions.

- **Source:** P028, lines/section `F51`.
- **Aliases/history:** unification.
- **Do not collapse:** A common refinement is not automatically an interaction, strict join, or shared-access certificate.

## lawhood descent
**Status:** canonical law.  
A candidate law is lawful at a layer exactly when it factors through the available access quotient.

- **Source:** P028, lines/section `3893`, `thm:F18`.
- **Aliases/history:** layer lawfulness.
- **Do not collapse:** Application of a named law still requires a bridge from application objects to theorem objects.

## record
**Status:** canonical.  
A typed, source-located, auditable association between events/claims and provenance; F20 supplies formed-record discipline.

- **Source:** P028, lines/section `F20`.
- **Aliases/history:** event record.
- **Do not collapse:** Passive logs and unowned analyst annotations need not be formed records.

## repair join
**Status:** canonical endogenous definition.  
For quotients on a common carrier, the coarsest quotient refining both. It supplies distinctions but not source, cost, utility, access, or interaction admissibility.

- **Source:** P030, lines/section `458-467`.
- **Aliases/history:** quotient join.
- **Do not collapse:** Do not confuse this vertical/common-carrier operation with the desired VII join between formed theories.

## predictive surplus
**Status:** canonical endogenous definition.  
Declared reduction in closure deficit from current quotient to predictive baseline, or a certified residual surrogate.

- **Source:** P030, lines/section `471-488`.
- **Aliases/history:** surplus.
- **Do not collapse:** Relative to declared futures; not intrinsic hidden meaning, intelligence, or fitness.

## carried record / instrument
**Status:** canonical endogenous definition.  
A carrier coordinate updated on-kernel whose accepted source is generated by the system trajectory; a carried instrument satisfies the same condition for visibility, thresholds, and checks.

- **Source:** P030, lines/section `492-508`.
- **Aliases/history:** internalized record.
- **Do not collapse:** Physical location inside a boundary is insufficient for carriedness.

## E-system
**Status:** canonical endogenous definition.  
A formed package plus carried instrument, carried ledger, and carried P1–P5 repair generator, with lawful occurrence separately requiring permission, ledger membership, admissibility, on-kernel realization, and re-audit.

- **Source:** P030, lines/section `512-528`.
- **Aliases/history:** endogenous closure system.
- **Do not collapse:** An organism or agent is not thereby an E-system; P6 is governance, not a repair payload.

## closed-loop scope
**Status:** canonical endogenous definition.  
A challenge history with complete audit inventory in which every repair occurrence is carried; external repair makes the history subsidized rather than self-repairing.

- **Source:** P030, lines/section `532-546`.
- **Aliases/history:** self-repair scope.
- **Do not collapse:** Choosing a larger carrier may change the verdict and must be declared.

## probe economy
**Status:** canonical endogenous definition.  
A finite probe catalog, carried active family, exposure budget, and allocation/acquisition/retirement moves; acquisition is strict only against same-family saturation.

- **Source:** P030, lines/section `550-564`.
- **Aliases/history:** exposure economy.
- **Do not collapse:** Exposure is not free and selection is not licensed as an unqualified argmax.

## currency
**Status:** canonical cross-paper notion.  
A low-dimensional carried quantity with a declared constraint, ledger, potential, or shadow-price role.

- **Source:** P030, lines/section `350-357`.
- **Aliases/history:** budget; price.
- **Do not collapse:** Correlation with outcomes makes a proxy, not a currency.

## adequacy residual
**Status:** canonical.  
A positive-semidefinite leftover measuring what a dissolving/target probe family sees beyond a native family under a declared audit energy.

- **Source:** P004, lines/section `436-628`, `definition/theorems`.
- **Aliases/history:** blind-spot currency.
- **Do not collapse:** Residuals are interface- and bridge-relative; exact adequacy is not generic.

## needle
**Status:** canonical family notion.  
A localized obstruction or unresolved direction that survives the currently admitted probe family/budget.

- **Source:** P009, lines/section `975`.
- **Aliases/history:** blind spot.
- **Do not collapse:** Dissolution is framework-bound; not every obstruction is removable by ascent.

## dynamic/run-level law
**Status:** canonical.  
A law whose statement quantifies over histories, horizons, moving covers, accumulated budgets, adversaries, or transport through time, rather than only static package structure.

- **Source:** P029, lines/section `catalog introduction`.
- **Aliases/history:** G-law.
- **Do not collapse:** G-laws must not be collapsed into static F-laws by dropping temporal hypotheses.

## bootstrap obstruction
**Status:** wishlist-provisional.  
A dependency cycle in which every rule capable of extending access or enabling a capability requires a premise available only after that extension/capability has already occurred.

- **Source:** WISHLIST, lines/section `various`.
- **Aliases/history:** self-bootstrap failure.
- **Do not collapse:** Not yet a canonical SBT theorem in the supplied corpus; Step 3 must decide its exact carrier and fixed-point form.

## expressible / present / reachable / occurrent
**Status:** wishlist-provisional.  
Four distinct statuses: stateable in the vocabulary; mechanism instantiated; attainable by a lawful path; observed within a declared horizon.

- **Source:** WISHLIST_from_mm_arc, lines/section `107-148`.
- **Aliases/history:** possibility ladder.
- **Do not collapse:** Existing SBT status machinery motivates this split but does not yet supply this exact four-way VII theorem.

## join between theories
**Status:** wishlist-provisional.  
A proposed audited contact event/object between independently formed theory packages, with shared evaluation domain, source/provenance, compatibility, and an irreducibility or anti-product witness.

- **Source:** WISHLIST, lines/section `132-185`.
- **Aliases/history:** interaction join.
- **Do not collapse:** Must not be identified by fiat with repair join, categorical product, common refinement, common source, or message exchange.

## enablement
**Status:** wishlist-provisional.  
A proposed relation in which one package/event makes another formation reachable without necessarily causing, containing, determining, or descending to it.

- **Source:** WISHLIST_foundations_vii_manager, lines/section `159-173`.
- **Aliases/history:** birth enablement.
- **Do not collapse:** Must be typed against causation, descent, sufficiency, and theorist/carrier/co-trigger attribution.
