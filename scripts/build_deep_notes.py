#!/usr/bin/env python3
"""Generate curated Step-1 deep-reading notes for the canonical and interpretive spine."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "derived" / "metadata"
OUT = ROOT / "notes" / "deep"
OUT.mkdir(parents=True, exist_ok=True)
CAT = {r["paper_id"]: r for r in csv.DictReader((ROOT / "config" / "paper_catalog.csv").open(encoding="utf-8"))}

N = {
"P031": {
"question": "What is the minimal closure calculus of emergent theory objects, and what evidence is required before objecthood, novelty, or directionality may be claimed?",
"thesis": [
"Foundations I treats a theory as a bounded-access package rather than as an untyped set of propositions. The recurring package has a carrier, a lens/coarse interface and its definable distinctions, a completion or packaging endomap, and an audit. A candidate layer is not licensed by suggestive behavior alone: it must survive the declared closure, contribute a distinction not already available through the old interface, and—when an arrow is claimed—pass an independent directionality audit.",
"The organizing result is the **three-certificate loop**. Objecthood/stability asks whether the candidate is fixed, approximately fixed, or otherwise formed under the declared packaging operation. Novelty/strictness asks for nonfactorization or an equivalent witness that the new interface separates a pair the old one identifies. Directionality asks for time-reversal asymmetry or non-exact affinity that survives the declared protocol and observation map. These obligations are logically independent; none may be inferred from another.",
"The paper unifies order-theoretic closure operators and dynamics-induced idempotent endomaps. A fixed idempotent saturates after one effective application, so open-ended emergence cannot be modeled by repeatedly applying one unchanged closure. Persistent ladders require changing the operator, enlarging the interface, changing the problem domain, or otherwise paying for new closure structure.",
"The arrow section is especially important for later interaction work. Route dependence and cycle residue can indicate missing memory or non-exactness, while a genuine arrow requires a P6-side audit such as path-law versus reversed-path-law divergence. Deterministic coarse-graining obeys data processing, and protocol traps can hide rather than manufacture drive. This establishes the later red line: P3-style holonomy is not itself P6-drive."
],
"imports": [
"Canonical theory-package and closure/fixed-point vocabulary.",
"The three distinct certificates: objecthood, strictness, directionality.",
"Fixed-package saturation and the need for operator/interface change for persistent growth.",
"Path-reversal audit, data processing, and protocol-trap discipline.",
"Bridge/port accounting as an explicit part of a theory package rather than free transport."
],
"nonclaims": [
"The finite forcing analogy is not a set-theoretic independence result.",
"Macro feedback means constrained admissibility or context-indexed dynamics after an explicit coupling; it is not a claim that macro descriptions override micro laws.",
"The paper does not supply a calculus of partially self-owned access, evidenced inter-theory contact, or joins.",
"Foundations I's informal P1–P6 alignments are historical; Foundations II supplies the controlling typed meanings."
],
"vii": [
"Foundations VII must keep the three certificates separate for contact/join objects: a strict joint distinction is not yet a formed joint package or an interaction arrow.",
"Any access-growth or join mechanism that iterates a fixed idempotent without new admissible input faces saturation.",
"Order effects among theories require memory/holonomy analysis plus a separate driven/null audit.",
"The package definition is a starting interface, not proof that total lenses transfer to partial self-owned domains."
],
"anchors": ["three-certificate loop", "Closure ladders and saturation", "Cycle criterion for exactness", "Data processing for path reversal", "Protocol trap", "Discussion and scope boundary", "Bridges, ports, and accounting"]
},
"P027": {
"question": "What do the six primitive roles mean after typing, level separation, admissibility, and scope restrictions are enforced?",
"thesis": [
"Foundations II is the canonical authority for primitive-role semantics. It replaces informal associations with six typed channels: P1 descent/update-versus-quotient compatibility; P2 representability of requested macro specifications; P3 enriched route/coherence mismatch; P4 stage, transition, refinement, and order; P5 quotient packaging; and P6 audit, provenance, replay, and checkability. `P6_drive` is a narrow affinity-carrying face of P6 used for directionality, not a seventh primitive.",
"Each role is stratified across behavioral, verification/certificate, and structural-categorical levels. Upward lifts are selected and data-bearing, not automatic equivalences. Role channels can be inactive, below threshold, collapsed, absent with a record, or outside scope. This prevents the common mistake of reading the six-channel architecture as six simultaneously active mechanisms in every example.",
"The terminal exact-six theorem is deliberately scoped to FATCD, the finite audited typed closure-description domain, and assumes an explicit recognition hypothesis. Its conclusion is existential and non-unique: an admissible description has an exhaustion/decomposition record with six role channels and no required seventh irreducible role in that covered scope. It is not a universal six-symbol algebra, a uniqueness theorem, or an empirical claim that nature realizes six mechanisms.",
"The paper's repaired alignments are load-bearing. A generic transition is not P3; a generic path is not P5; generic semantics is not P1; and route mismatch does not provide drive. These corrections govern how Foundations I and applications are read downstream."
],
"imports": [
"The controlling definitions of P1–P6 and `P6_drive`.",
"Behavioral/verification/structural level trichotomy and selected-lift discipline.",
"Honest bookkeeping, role projections, thresholds, collapse/loss records, and nonclaim closure.",
"FATCD scope and the exact meaning of the scoped exact-six theorem."
],
"nonclaims": [
"No global independence or unique factorization of the six roles.",
"No theorem that every system activates all six channels.",
"No universal category, algebra, or complete calculus of role composition.",
"No empirical bridge is free; recognition and realization remain separate obligations."
],
"vii": [
"Every proposed VII primitive should be tested first as a typed object built from existing roles, but resemblance to one role is not an applicability proof.",
"Access, contact, join, enablement, and occurrence need their own status families; they should not be encoded as overloaded P-labels.",
"If VII declines a six-primitives algebra, it should say that the current selected-lift apparatus does not yet support one.",
"The role-level correction ledger must control citations to earlier papers."
],
"anchors": ["Primitive closure roles", "Corrected alignments", "Drive face", "Behavioral, verification, and structural", "Residual classification", "The scoped exact-six theorem", "What scoped exact-six means", "Limitations and nonclaims"]
},
"P026": {
"question": "What finite typed object records interactions among primitive roles without collapsing actions, pair observables, promotion, source, realization, and audit?",
"thesis": [
"Foundations III supplies `BirdInt_fin^aud`, a finite audited typed interaction record. The controlling body declaration has nineteen components: package family, levels, host, content, instrument, package, profile, witnesses, updates, defects, judgments, statuses, gates, dependencies, audit, visibility, source, nonclaim, and realization. The first eighteen are internal record components; `Real` records model realization. An appendix's older 'sixteen-component' shorthand omits visibility, source, and realization and is treated here as a legacy inconsistency, not the governing definition.",
"The calculus keeps judgment families separate. A directed cell `P_i ← P_j` means the actor consumes an informant witness through a typed update under declared visibility, threshold, defect, source, and audit records. A pair observable is an independent unordered-pair judgment with joint-source and branch-compatibility obligations. A real directed cell therefore does not make a pair observable real. Promotion bridges are another family again; strict promotion proves a nonfactorization relation but does not by itself prove target closure, occurrence, or drive.",
"Seven status families—Role, Cell, Pair, Promotion, Claim, Gate, and Square—prevent status-name transport across types. Dependencies, missing bridges, visibility, and nonclaims are first-class. The countermodel atlas is not ornamental: it separates active package from macro closure, route/holonomy from drive, local packages from global formation, action cells from pair reality, refinement from improved closure, and rotating audit from final same-level self-certification.",
"BirdInt is intentionally not declared to be a category, algebra, or closure operator. It is a typed finite calculus and record schema. This restraint matters for VII: it offers much of the bookkeeping required for contact and join certificates, but it does not already define inter-theory interaction or a join operation."
],
"imports": [
"Nineteen-field controlling interaction record and the body-over-appendix correction.",
"Directed cell, pair observable, promotion bridge, source, visibility, gate, dependency, and nonclaim distinctions.",
"Seven separate status families and type-safe refusal of status transport.",
"Countermodel method: each positive bridge is paired with the nearest missing-bridge failure.",
"Rotating finite audits as useful but not final self-certification."
],
"nonclaims": [
"A directed action does not establish a jointly sourced pair observable.",
"Fallback/proxy evidence is not silently native evidence.",
"Strictness does not imply objecthood, drive, or realization.",
"The calculus is not a categorical composition law and does not prove a universal interaction algebra."
],
"vii": [
"VII should reuse BirdInt's typed record discipline for contact surfaces, source independence, pending joins, detectors, and nonclaims.",
"A join needs a distinct judgment/status family rather than reusing Pair or Promotion by analogy.",
"The body/appendix inconsistency is a concrete reason to adopt normative-spec-over-demonstration priority.",
"Countermodels for cell-without-pair and holonomy-without-drive should be inherited as mandatory nulls."
],
"anchors": ["Paper Scope Statement", "The interaction calculus", "Promotion Bridge Object", "Dependency and No-Go Judgments", "Countermodel Atlas", "Active Route / Holonomy but No Drive", "Directed Cell Active but Pair Observable Blocked", "Rotating-Audit Bridge", "Limitations and Nonclaims"]
},
"P028": {
"question": "Which structural laws hold across layers before any particular substrate is chosen, and what theorem surfaces constrain future interaction laws?",
"thesis": [
"Foundations IV is a catalog rather than a single master theorem. It contains 52 named F-law rows, preserving identifiers F2–F53 including split rows F13a/F13b and F15a/F15b. Each row declares setup, theorem shape, status, relations, layer instantiations, and nonclaims. Step 1 preserves those identifiers because renumbering would break downstream provenance.",
"The catalog's most important access results are quotientality (F10), adequacy/no-overread (F11), no-free-distinction (F12), hiddenness/complementarity, common quotient/objectivity (F17), interface mediation (F22), and finite-interface limits. Transport laws include descent-repair normal form (F2), holonomy-memory repair (F3), local-global obstruction (F4), recombination comparison (F5), composability (F28), and scale descent (F35). Direction and record claims include arrow/record monotonicity (F38), while common-source correlation (F49) and unification/common refinement (F51) are especially easy to overread.",
"The law rows have different formal statuses. F6 and F53 are substrate-delegated anchors; F13a and F14 are partial wrappers; F13b and F15b are obligation-guarded; the remaining rows are direct at the paper's declared layer-agnostic scope. 'Layer-agnostic' means reusable after each target discharges the stated objects and hypotheses, not true everywhere without a bridge.",
"For Foundations VII, F51 is only a common-refinement/unification precedent. F17 provides a common public quotient, F49 a common-source correlation shape, and F5 a recombination comparison. None is a theorem that evidenced contact exists, that a strict join forms, or that independent access is shared. The catalog supplies constraints and nulls for a future interaction calculus, not the calculus itself."
],
"imports": [
"All 52 F-law identifiers, exact names, status grades, and relations.",
"F2/F4/F5 normal forms for descent, globalizability, and recombination.",
"F10–F12 access quotient, no-overread, and anti-smuggling discipline.",
"F17/F18/F22/F28/F35/F37/F38/F49/F51/F53 as the main VII dependency surface."
],
"nonclaims": [
"Common source is not common access or source independence.",
"Common refinement is not automatically a strict or operational join.",
"Layer-agnostic instantiability is not universality without per-instance hypotheses.",
"Static F-laws do not replace Foundations VI's run-level temporal quantifiers."
],
"vii": [
"Candidate interaction laws should use the F-row normal form and status grading.",
"Join and access results must state whether they inherit F-laws directly, need extra hypotheses, or are only analogies.",
"The distinction between source refinement and target coarsening in F2 is a seed for top-down/bottom-up construction routes.",
"F53's closure–reality boundary prevents VII from treating mere formal descriptions as formed interaction objects."
],
"anchors": ["Axis I — Access", "Quotientality", "Adequacy / No-Overread", "No-Free-Distinction", "Descent-Repair Normal Form", "Local-Global Obstruction Normal Form", "Recombination Comparison", "Unification", "Closure–Reality"]
},
"P030": {
"question": "What changes when instruments, ledgers, repairs, and re-audits become carried parts of the system rather than theorist-side operations?",
"thesis": [
"Foundations V makes the endogenous turn. Earlier structural laws let an external theorist declare lenses, detect defects, install repairs, price residuals, and run audits. An endogenous closure system carries instruments, ledgers, repair generators, boundary records, and re-audit machinery on its own carrier. This does not make every self-description trustworthy; it moves provenance and execution obligations inside the modeled system.",
"The D1–D6 definitions are foundational. D1's **repair join** is the coarsest common refinement of declared quotients and supplies distinctions only; it says nothing by itself about source, cost, access, utility, occurrence, or a join of theory objects. D2 quantifies predictive surplus. D3 defines carried records/instruments through carrier coordinates, on-kernel updates, and trajectory-generated sources. D4 packages a formed theory together with carried instrument, ledger, and P1–P5 repair generator; P6 remains governance/audit rather than repair payload. D5 declares closed-loop scope, and D6 introduces finite probe economies and exposure cost.",
"A carried operation's existence is distinct from its lawful occurrence. Permission, ledger state, admissibility, on-kernel execution, and re-audit remain separate. The E1–E16 laws then treat internalization, bounded reflexivity, reclosure, repair compilation, attention, alarm, control price, curiosity, cognitive demarcation, institutional rewrite, individuation, transport, reconsolidation, offline reclosure, and adaptability.",
"This paper is the nearest precursor to endogenous enablement, but it does not prove that every observer-certified extension was born endogenously. It also does not define inter-theory contact or a strict join. Its strongest VII contribution is the demand that 'who performs the operation?' be answered with carried source and runtime evidence, not inferred from a successful external certificate."
],
"imports": [
"D1–D6 exact definitions, especially carried instruments and closed-loop scope.",
"Separation of carried capability, permission, reachability, occurrence, and re-audit.",
"Finite probe economy and exposure budget.",
"E1–E16 identifiers and their endogenous/cognitive law roles."
],
"nonclaims": [
"D1 repair join is not a Foundations-VII theory join.",
"Carried code or a stored rule is not proof that the operation can lawfully fire.",
"External certification does not establish endogenous birth or enablement.",
"P6 is governance/audit; it is not silently folded into the P1–P5 repair generator."
],
"vii": [
"Define enablement attribution using carried-source, execution, and re-audit records.",
"Price commitments, contacts, detectors, and joins within a finite probe economy.",
"Use D1 as a degenerate common-refinement case while defining a stricter interaction join separately.",
"Model the observer/instrument as in-world when it consumes shared resources."
],
"anchors": ["Introduction: the endogenous turn", "D1 — Repair join", "D2 — Quantified predictive surplus", "D3 — Carried records and instruments", "D4 — Endogenous closure systems", "D5 — Closed-loop scope", "D6 — Exposure cost and probe economy", "Null battery", "Nonclaims"]
},
"P029": {
"question": "Which structural laws require quantification over runs, moving covers, accumulated costs, endogenous obstructions, and long-time transport rather than static packages?",
"thesis": [
"Foundations VI separates run-level dynamics from the static laws of Foundations IV and the carried machinery of Foundations V. A statement about one fixed map or package cannot substitute for liveness, eventual certification, amortized cost, transfinite escrow, moving targets, history-generated obstructions, integrated route defects, or long-time transport. The G-series therefore carries explicit temporal quantifiers and run-level hypotheses.",
"The thirteen laws are: G1 Hidden Amortized Solvency; G2 Transfinite Escrow; G3 Amortized Potential Currency; G4 Moving-Cover Exhaustion; G5 Carry-Horizon Confinement; G6 Endogenous Needle Generation; G7 Adversarial Mobility Confinement; G8 Odometer Abelianization; G9 Defect-Evacuation-to-Transport; G10 Lossful Boundary Persistence; G11 Local-Rule Global-Anti-Symmetry; G12 Finite Witness Radiation; and G13 Thin-Orbit Saturation. Their shared lesson is that a bounded local certificate may survive, fail, or accumulate in ways invisible to a static snapshot.",
"The methodology uses eccentric problems as theorem detectors. The Collatz-style flagship attached to G1 is explicitly conditional: ghost convergence/separation assumptions remain unproved, and the paper does not prove Collatz. The sandpile route to G8 is used from the solved end. Negative walkthroughs are also part of the method: candidate laws can be absorbed by existing results or parked when the proof object is not ready.",
"For VII, the key inheritance is quantifier discipline. Reachable, eventually reached, observed by horizon H, and guaranteed on every lawful run are distinct. Interaction order, pending joins, commitment expiry, and a detector's failure to fire all need run-level statements rather than static existence claims."
],
"imports": [
"G1–G13 exact identifiers and theorem surfaces.",
"Run-level distinction between existence, liveness, amortized cost, and long-horizon behavior.",
"G6 as the explicit warning that systems can manufacture new needles.",
"Solved calibration versus conditional flagship versus parked candidate status."
],
"nonclaims": [
"No proof of Collatz or any open flagship whose bridge assumptions remain unproved.",
"Static F-laws cannot be restated as dynamic guarantees without new quantifiers.",
"Finite-horizon non-occurrence does not imply structural impossibility.",
"An observed route residue over time is still not automatically an arrow."
],
"vii": [
"Use run semantics for expressible/present/reachable/occurrent and pending join states.",
"State horizon laws and negative-result quantifiers explicitly.",
"Analyze both obstruction dissolution and obstruction manufacture under access/join dynamics.",
"Keep theorem, schema, calibration-anchored, conditional flagship, and parked statuses visible."
],
"anchors": ["Introduction: the dynamical turn", "Methodology: eccentric problems", "Worked example: Collatz to G1", "Worked example: sandpiles to G8", "Negative walkthrough", "Cluster A", "G6", "Nonclaims"]
},
"P032": {
"question": "Under which exact finite carriers and hypotheses are familiar emergence narratives impossible, and what must change to escape each obstruction?",
"thesis": [
"The no-go paper provides eight theorem fronts, each tied to a specific mathematical carrier: `NG_ARROW_DPI`, `NG_PROTOCOL_TRAP`, `NG_FORCE_FOREST`, `NG_FORCE_NULL`, `NG_MACRO_CLOSURE_DEFICIT`, `NG_OBJECT_CONTRACTIVE`, `NG_LADDER_IDEM`, and `NG_LADDER_BOUNDED_INTERFACE`. Their value is not a general pessimism about emergence; it is the exact statement of what a claimed mechanism cannot do while specified hypotheses remain in force.",
"The arrow results use finite path laws, time reversal, KL divergence, and deterministic pushforward. Coarse observation cannot manufacture path-reversal asymmetry, and an uninformative protocol can erase it. The forcing results concern a particular support-graph/affinity object; the macro-closure result concerns best Markov closure deficits; the object result concerns contractive packaging; and the ladder results concern unchanged idempotents or bounded interfaces. These carriers must not be replaced by merely similar application graphs, workflows, or verbal ladders.",
"Each no-go is paired with escape routes: retain more information, change the protocol, introduce cycles/affinity, enlarge the interface, change the operator, relax contraction, add memory, or leave the declared scope. The escape-route remark is part of the theorem's usefulness because it identifies which assumption a constructive theory must pay to drop.",
"The paper is a template for VII's proposed no-gos. A bootstrap or join impossibility must first define the admission carrier, allowed seeds, source relation, bridge information, cost model, and relevant quantifier. Without that, 'no free join' would be a slogan rather than a theorem."
],
"imports": [
"All eight no-go identifiers, exact carriers, hypotheses, and escape routes.",
"DPI and protocol-trap separation of hidden versus manufactured drive.",
"Requirement that impossibility statements name the quantified family and permitted changes.",
"Negative results as constructive design guidance through escape routes."
],
"nonclaims": [
"A support graph of a Markov kernel is not an arbitrary process-connection graph.",
"A bounded-interface ladder no-go does not rule out growth after interface/operator change.",
"Protocol traps hide drive; they do not show the substrate is undriven.",
"No theorem transfers by analogy alone."
],
"vii": [
"Use the same carrier-first format for bootstrap, resemblance join, one-lineage, unpriced observer, totality transfer, and universal-join candidates.",
"Attach explicit escape routes to every interaction no-go.",
"Treat negative evidence as claim-quantifier dependent.",
"Include protocol/scheduler nulls in interaction-holonomy experiments."
],
"anchors": ["Formal setup and audit definitions", "Data-processing inequality", "Protocol trap", "Force", "Macro closure", "Packaging operators", "bounded interfaces", "Scope and escape routes"]
},
"P006": {
"question": "Can a typed carrier with audit obligations be completed into an audit-closed object, and how should its residual defects be classified?",
"thesis": [
"Audited Operational Realisability (AOR) studies carriers equipped not only with primary mathematical objects but with source ledgers, route registries, residual budgets, statuses, nonclaims, and meta-audit records. A PreSB carrier becomes an AOR carrier when every obligation declared in its scope is discharged internally to that scope. The paper constructs a canonical closure/completion through monotone saturation, framed as a reflection into the audit-closed subcategory.",
"The defect analysis is highly reusable: structural failure is stratified, residual obligations are classified into a thirteen-type atlas, and discharge operations can trigger cascades. Termination and confluence questions are made explicit rather than hidden in an 'audit passed' flag. The paper also studies refinement chains and the limits of finality: richer scopes can reveal residuals invisible to a narrower audit.",
"For VII, AOR gives a meta-level completion discipline for interaction records. It can help define when a join certificate is audit-closed relative to a declared scope and how missing source, reachability, cost, or falsifier obligations propagate. But AOR closure is not itself operational reachability, evidenced contact, or join existence. A perfectly closed audit package may describe a mechanism that never fires.",
"The correct use is therefore two-stage: first define the interaction/access object and its operational semantics; then use AOR-like closure to discharge the record obligations. Reversing those stages would turn a complete dossier into evidence that the underlying event occurred."
],
"imports": [
"PreSB/AOR carrier distinction and scoped audit closure.",
"Monotone saturation/reflection as a canonical completion mechanism.",
"Eight-stratum defect view, thirteen residual types, and discharge cascades.",
"Confluence/termination and scope-relative finality of audits."
],
"nonclaims": [
"Audit completion does not prove runtime reachability or occurrence.",
"No universal final audit closes all richer future scopes.",
"Residual classification does not automatically identify the physical repair.",
"AOR is meta-theory for records, not a replacement for VII's interaction semantics."
],
"vii": [
"Use AOR to close the obligation set of contact/join certificates after defining their semantics.",
"Represent missing source, independence, cost, reachability, and null evidence as typed residuals.",
"Check discharge order/confluence for multi-obligation join audits.",
"Do not call an audit-closed but unreachable mechanism operationally realized."
],
"anchors": ["PreSB carrier", "closure-completion functor", "Structural defect and its eight strata", "thirteen-type", "discharge cascades", "Knaster–Tarski", "Status, scope, and nonclaim boundary"]
},
"P023": {
"question": "How does a reflexive audit consume finite capacity, and when can capacity control rule out localization without pretending that every audit is final on itself?",
"thesis": [
"Reflexive SBT turns localization into an instrument- and package-relative capacity problem. It defines a max-cell localization metric for packaged feasible subspaces, relates it to diagonal/trace quantities, and studies how symmetry, conditioning, sparse route unions, and closure-recovery moves affect the available audit capacity.",
"The strongest structural implication is conditional: under stated capacity-vanishing or trace/diagonal controls, localization is excluded. The paper also supplies failure modes. Cancellation can hide localized components; poor conditioning creates tails; route unions spend capacity; and exact symmetry is a special case rather than a universal background assumption.",
"The philosophical point is bounded reflexivity. An audit apparatus is itself a structured consumer of capacity, and no fixed audit is final on all richer descriptions. This is relevant to VII's observer occupancy and detector-competence questions: an instrument cannot be treated as an outside, free vantage if it uses the same bounded carrier or interface it certifies.",
"The result must not be overextended. Capacity bookkeeping can constrain localization and audit viability, but it does not prove access growth, join existence, source independence, or an endogenous observer. Those require separate operational records."
],
"imports": [
"Localization metric and trace/diagonal capacity bounds.",
"Conditional capacity-to-anti-localization result and its hypotheses.",
"Failure modes from cancellation, conditioning, and route-union cost.",
"Reflexive audit as bounded capacity bookkeeping."
],
"nonclaims": [
"No universal capacity decay or universal anti-localization theorem.",
"A capable detector is not evidence that the target event occurred.",
"The audit's internal representation does not make it final on itself.",
"Capacity bounds do not establish source independence or shared access."
],
"vii": [
"Model observer occupancy and detector resource use explicitly.",
"Require detector competence before interpreting a null or positive.",
"Treat exposure changes as potentially capacity-changing even when determination is unchanged.",
"Preserve scope-relative reflexivity and prohibit self-certifying prediction."
],
"anchors": ["localization metric", "Trace bound", "Diagonal capacity bounds", "route capacity", "capacity vanishing implies anti-localization", "Interpretation: Reflexive SBT as capacity bookkeeping", "failure modes"]
},
"P034": {
"question": "What structural form does incompleteness-like growth take when formal theories are treated as fixed packages on frozen ledgers?",
"thesis": [
"The paper proves a clean saturation fact: an idempotent package reaches its fixed output after one effective closure step, so repeated application of the same frozen package cannot support persistent strict growth. A genuine sequence of strict extensions therefore requires package change—new axioms, interfaces, rules, or admissible data—not merely more iterations of the old closure.",
"On controlled slices, the paper studies transfer of efficiency and package comparison, and it sketches a conditional arithmetic lift whose assumptions are external to the finite structural core. The strongest use for Foundations VII is not a direct Gödel theorem but the bootstrap pattern: a rule set may be sound and closed yet have no lawful first move that creates the capability required for its own extension.",
"This is a structural precursor to bootstrap obstruction, not the finished theorem. VII still needs an operational state space, admission rules, allowed seeds, and a reachability relation. Fixed-package saturation by itself does not tell whether a supplied seed is neutral stocking, rigging, or an admissible prospective commitment.",
"The scope discipline is exemplary: finite package theorems, frozen-slice comparisons, and conditional arithmetic interpretations are kept in different claim lanes."
],
"imports": [
"One-step saturation of a fixed idempotent package.",
"No persistent strict growth without package change.",
"Frozen-slice and cone-equivalence restrictions on transfer.",
"Separation of finite structural result from conditional arithmetic lift."
],
"nonclaims": [
"Not a new proof of Gödel incompleteness.",
"Package change is necessary for persistent growth but does not specify a lawful change mechanism.",
"A fixed-point theorem does not prove runtime reachability.",
"The arithmetic bridge remains assumption-dependent."
],
"vii": [
"Use saturation as one premise in a formal bootstrap obstruction theorem.",
"Define allowed seed/package changes and distinguish stocking from rigging.",
"Do not claim that every non-self-bootstrapping mechanism is impossible; state minimum-seed conditions.",
"Keep existence of an extension separate from a lawful transition that reaches it."
],
"anchors": ["Fixed-package saturation and package change", "One-step saturation", "No persistent growth in a frozen package", "Strict growth requires package change", "Scope discipline", "Out-of-scope claims"]
},
"P053": {
"question": "Which set-theoretic commitments arise from finite membership packaging under a rank audit, and which require explicit purchases beyond that construction?",
"thesis": [
"The paper starts from finite well-founded membership presentations, a membership lens, and rank-decreasing audits. Decoration/Mostowski-style packaging yields the hereditarily finite core and supports a staged account of several familiar axiomatic behaviors. It then contrasts this 'free' auditable part with commitments that must be purchased: forms associated with Infinity, Power Set, Replacement, Choice, and extension principles.",
"The central methodological lesson is an assumption ledger. A mathematical universe should not be presented as if every expressive resource were generated by one closure. New totalities, selection principles, or extension mechanisms are declared at the boundary where the previous package saturates. Forcing, nondefinability, and strict extension are discussed through this staged lens with explicit grade separation.",
"For VII, this is a precedent for prospective commitment and access purchase: a theory can lawfully enlarge its domain only by naming the extra resource, rule, or bridge and retaining it in the audit. But the paper does not directly prove laws of inter-theory access or join. Set-theoretic 'purchase' is an analogy/structural precedent until a bridge is written.",
"Its countermodel and guard ledgers also reinforce that a successful construction should not erase the assumptions that made it possible."
],
"imports": [
"Finite membership presentations, membership lens, and rank audit.",
"Free-versus-purchased commitment ledger.",
"Explicit guard/countermodel discipline for extension claims.",
"Scope separation between theorem-grade finite construction and discussion-grade set-theoretic interpretation."
],
"nonclaims": [
"Not a derivation of all ZFC from finite closure.",
"Purchased axioms are declared commitments, not emergent consequences of the finite package.",
"Set-theoretic extension does not automatically instantiate a theory join.",
"Discussion of forcing/independence must retain its bridge and grade."
],
"vii": [
"Use an explicit purchase/commitment ledger for access growth and joins.",
"Treat seeds, bridges, observer resources, and domain expansions as declared controls.",
"Retain the assumptions enabling a join instead of laundering them into the formed object.",
"Distinguish theorem-level interaction laws from philosophical analogies to set-theoretic extension."
],
"anchors": ["Finite membership presentations", "The membership lens", "The free part", "purchased", "finite Cohen bridge", "guard discipline", "Scope and non-claims"]
},
"P046": {
"question": "How can mathematical completion claims be audited as theory packages without converting a methodological example into a theorem about the target mathematical problem?",
"thesis": [
"`A Mathematics Is a Theory` instantiates the theory-package schema for mathematical protocols: discrete procedures, limiting or completion objects, defect ledgers, feasibility gates, route mismatch, and numerical diagnostics. It treats the passage from large finite computation to stable continuous closure as an auditable claim rather than a definitional entitlement.",
"The useful contribution is methodological. Finite-difference/derivation-style anchors and route/positivity diagnostics illustrate how a proposed mathematical closure can be checked for stability, path dependence, and overclaim. The paper's slogan is that a mathematics is a theory when its objects, completion, and audits are explicit.",
"The scope boundary is critical: the paper does not prove a new theorem about zeta zeros or any open target merely because its diagnostics are suggestive. Numerical evidence, closure methodology, and target-theorem status remain separate lanes.",
"For VII, this supports the rule that a formally well-defined derived operation is not automatically an operationally admissible operation. The operation language, allowed compositions, and detector must be part of the package."
],
"imports": [
"Mathematics-theory package and explicit closure-engine viewpoint.",
"Defect ledgers, feasibility gates, route mismatch, and numerical audit separation.",
"Method/diagnostic versus target-theorem claim grading.",
"Requirement that completion claims state their instrument and stability tests."
],
"nonclaims": [
"No theorem about the Riemann hypothesis or zeta zeros follows from the diagnostics.",
"A numerical pass is not a proof of the target continuum closure.",
"A mathematically composable operation is not automatically substrate-admissible.",
"Methodological fit is not an applicability bridge to every mathematical domain."
],
"vii": [
"Define operational admissibility for derived interaction operations.",
"Attach explicit detector/null/falsifier records to mathematical join claims.",
"Keep calibration and theorem status separate.",
"Use the paper as a methods precedent, not a source of interaction laws."
],
"anchors": ["Paper contract", "Mathematics theory package", "A closure engine for mathematics", "Defect ledgers", "Interpretation and scope", "Discussion: scope, limitations"]
},
"P041": {
"question": "How does the SBT package behave in controlled multi-scale physics reductions, and which parts are exact algebraic facts versus finite simulations?",
"thesis": [
"`A Physics Is a Theory` models each effective physical theory as a lens, a completion/reconstruction, a packaging operator, and audits for closure, route mismatch, and stability. It provides exact algebraic/mechanized components and deterministic simulations across several model reductions, including dephasing, kinetic relaxation, coarse fluid structure, and backreaction-style examples.",
"The paper is valuable as an instantiation of the three-certificate loop. A coherent reduced layer needs closure/objecthood, a strict or useful distinction, and honest arrow/audit evidence. Audit monotonicity and route mismatch are examined under explicit total coarse-graining maps.",
"The paper's own scope says these are instantiations, not derivations of full continuum physics. The simulations and Lean anchors certify the stated finite/algebraic fragments; they do not establish all domain assumptions, empirical adequacy, or universal laws of emergence.",
"This matters directly for VII's totality-transfer warning. Many physics examples begin with a total analyst-declared lens over a known carrier. A partial theory with self-owned access may lack both global carrier enumeration and total reconstruction. Results must not transfer without a bridge that replaces those assumptions."
],
"imports": [
"Concrete lens/completion/package/audit instantiation pattern.",
"Three-certificate discipline in multi-scale model reduction.",
"Separation of exact mechanized algebra from deterministic numerical calibration.",
"Audit monotonicity and route-mismatch diagnostics under declared total lenses."
],
"nonclaims": [
"No derivation of continuum quantum, kinetic, fluid, or gravitational theories from SBT alone.",
"Finite simulations are not empirical confirmation of a universal emergence law.",
"Total-lens results do not automatically cover partial, endogenous access.",
"Application dictionaries do not redefine the canonical primitive roles."
],
"vii": [
"Use as a positive total-access control case in a totality-transfer countermodel.",
"State exactly which global carrier/lens assumptions fail for self-owned domains.",
"Preserve mechanized, numerical, and interpretive grades separately.",
"Do not infer interaction merely because two effective reductions share a micro substrate."
],
"anchors": ["Micro/macro state spaces and lenses", "Completion and closure", "Audits and audit monotonicity", "Route mismatch and commutation", "three-certificate loop", "Scope: instantiations, not derivations"]
},
"P040": {
"question": "Why can an object unavailable in a lower theory be indispensable to solving a lower-layer problem without being literally imported into the lower layer?",
"thesis": [
"P040 belongs to the `VF-SAU-01` version family. Despite its catalog filename/title, the internal title is *Why Mathematics Even Works*. It develops the Strict Audited Utility (SAU) pattern: a lower problem is saturated relative to a declared instrument; a promoted layer supplies a strict, non-descending object; an audited trace through that object yields a valid lower-boundary answer.",
"The main direction is necessity/normal form: a genuinely useful promoted trace that is not reducible to the lower instrument entails hidden non-descent together with audited boundary descent. The promoted object need not—and generally should not—be literalized below. What descends is a certified answer/readout through a bridge, not the higher object itself.",
"The result is instrument-relative. Strictness, saturation, admissibility, and utility are all stated against declared lower and promoted packages. Partial converses and canonical examples show the shape, while transfer between examples requires matching audits and bridge hypotheses.",
"For VII, SAU is a major bridge-discipline precedent. Peer transport or joining may make new answers available without making every parent object mutually expressible. However, SAU is vertical promoted use, not a theorem of horizontal contact or joint formation."
],
"imports": [
"Theory layers, instruments, lower problem profiles, promotion bridges, and SAU certificate.",
"Hidden non-descent plus audited boundary descent as the useful promoted-object normal form.",
"Instrument-relative saturation and strictness.",
"Bridge transfer only under matching audit hypotheses."
],
"nonclaims": [
"Not every useful mathematical object is covered without an SAU certificate.",
"The promoted object need not descend or become a lower-layer object.",
"Vertical promoted utility is not a horizontal join theorem.",
"P040 and P058 must not be double-counted as independent evidence."
],
"vii": [
"Use the boundary-descent pattern for peer transport and downward fidelity.",
"Require a native or explicitly bridged parent record before a join uses it.",
"Distinguish content becoming usable from objects becoming jointly present.",
"Resolve P040/P058 claim deltas before choosing a controlling citation."
],
"anchors": ["Scope", "Theory packages and instruments", "Lower problem profiles and saturation", "Promotion bridges", "The SAU certificate", "Necessity and Normal Form", "Complete nonclaims ledger"]
},
"P058": {
"question": "What is the alternate supplied version of the SAU theorem family, and how should it be used without provenance collapse?",
"thesis": [
"P058 is the second member of `VF-SAU-01`. Its file is catalogued as *Why Mathematics Even Works*, while its internal title is *The Usefulness of Non-Descending Objects: A Six Birds Theory of Mathematical Applicability*. It shares the same 73-section architecture and central SAU theorem family with P040 but differs in editorial framing and theorem presentation.",
"Its mathematical core is the same structural problem: a lower theory cannot represent a useful object, a promoted theory can, and an audited promoted-use trace returns a valid lower answer. Usefulness therefore does not require literal descent of the object; it requires a bridge whose boundary expression is admissible in the lower problem profile.",
"The Step-1 ruling is conservative. Both frozen files retain their IDs, filenames, internal titles, and hashes. The family is cited once at synthesis level, while member-specific statements remain member-specific. Step 2 must produce a claim-level delta ledger before declaring one version controlling.",
"The family also clarifies a likely VII distinction: shared usefulness or transferred answers do not imply shared access, common objecthood, or strict join. A joint theory would need additional source, contact, closure, and anti-product evidence."
],
"imports": [
"SAU definitions, necessity/normal-form theorem family, partial converse, and bridge discipline.",
"Instrument-relative distinction between promoted object and descended boundary answer.",
"Version-family provenance rule: no silent canonicalization or double counting.",
"Usefulness/transport as weaker than joint object formation."
],
"nonclaims": [
"No claim that all mathematics fits one literal lower/promoted pair.",
"No automatic lower-layer literalization of higher objects.",
"No evidence independence between P040 and P058.",
"No horizontal interaction theorem follows without extra definitions."
],
"vii": [
"Treat answer transport, shared access, and join as distinct status families.",
"Use explicit version-family records in the claim registry.",
"Import the bridge theorem only after a member-level hypothesis check.",
"Use non-descent as a warning against overstrong downward-causation language."
],
"anchors": ["Introduction", "Theory packages and instruments", "Lower problem profiles and saturation", "Promotion bridges", "The SAU certificate", "Necessity and Normal Form", "Complete nonclaims ledger"]
},
"P056": {
"question": "What philosophical picture of reality is proposed once closure, objecthood, cost, and audit are treated as constitutive, and which parts are purchased axioms rather than corpus theorems?",
"thesis": [
"`Reality as Closure` proposes an ontological reading: to be real is to have formed and survived closure under the relevant audit, with ongoing costs and records. Objects are presented as shadows of closure packages; probability, time, observers, and layers are read through the same grammar.",
"This is philosophy built on the mathematical corpus, not a replacement source for its definitions. The paper explicitly introduces two purchased axioms—Ontic Closure Completeness and Substrate Indifference—to move from structural SBT results to a general ontology. Those axioms do real work and must remain visible.",
"The useful Step-1 lesson is grade discipline. Structural theorems can support conditional philosophical interpretations, but the interpretation cannot be cited back as proof of stronger mathematical claims. In particular, 'reality as closure' does not establish that every formed package is physically realized or that all substrates instantiate the same closure laws.",
"For VII, the paper offers vocabulary for the reality boundary of interaction objects: a possible join, a well-typed join description, an audit-closed certificate, and an occurrent joint event may occupy different grades. The mathematical paper must define those grades before any ontological conclusion."
],
"imports": [
"Closure-centered ontology as a conditional interpretive framework.",
"Explicit distinction between corpus-grounded structural claims and purchased axioms.",
"Ongoing cost/maintenance emphasis for formed objects.",
"Observer deflation as an in-world closure package rather than an outside witness."
],
"nonclaims": [
"Not a theorem that closure exhausts physical reality without the purchased axioms.",
"Not an empirical realization result for every SBT package.",
"Philosophical language cannot override the canonical formal definitions.",
"Substrate indifference is an axiom/commitment, not silently proved layer agnosticism."
],
"vii": [
"Separate possible, expressible, audit-closed, reachable, and occurrent interaction objects.",
"Price maintenance of joins rather than treating formation as a one-time certificate.",
"Keep ontological interpretations in a conditional claim lane.",
"Model observers as packages with standing, privileges, and costs."
],
"anchors": ["The Last Rung of the Ladder", "The Price List", "How Things Become Real", "The Observer, Deflated", "Two Axioms and Their Bill", "Ghosts"]
},
"P005": {
"question": "How can a consciousness architecture separate structural closure conditions, recognition bridges, conditional realization, and open empirical claims?",
"thesis": [
"The paper defines an eight-clause candidate package: closure objecthood, strict promotion, a reflexive self-coordinate, non-exposure, action credit, temporal closure, binding, and viability. The clauses are a design and audit contract, not a declaration that any real system is conscious.",
"Its most reusable contribution is the four claim lanes: structural theorem, recognition bridge, conditional ontological/realization statement, and open empirical claim. This prevents a finite model or formal certificate from being promoted into an empirical or ontological conclusion without an additional bridge.",
"The exact finite model uses a twelve-state construction. Under a public lens the relevant viability structure is empty; a predictive quotient restores a ten-state kernel, with a uniquely minimal split of one public fiber. This is evidence that the interface can decide whether the package is even expressible and that a reflexive/predictive refinement can be structurally necessary. It is not evidence of actual consciousness.",
"For VII, the architecture is a strong pressure test for observer and realization language. A joint object can be structurally well-formed while lacking recognition, endogenous source, or occurrence. Component certificates and analyst-side summaries cannot stand in for a realization bridge."
],
"imports": [
"Eight-clause package and explicit separation of structural obligations.",
"Four claim lanes and trust-chain/bridge discipline.",
"Exact finite public-lens versus predictive-quotient model.",
"Non-exposure, action credit, temporal closure, binding, and viability as separately auditable clauses."
],
"nonclaims": [
"No empirical claim that the model or any current system is conscious.",
"No integrated real-world instance satisfying every clause.",
"Structural closure and recognition do not establish ontological realization.",
"Analyst-certified component facts do not prove endogenous self-certification."
],
"vii": [
"Adopt separate structural, recognition, realization, and occurrence lanes for joins.",
"Treat observer/instrument interface choice as potentially formation-critical.",
"Require an explicit bridge from finite interaction laboratory to any empirical interpretation.",
"Use the model as a counterexample to component-certificates-imply-realization."
],
"anchors": ["Four claim lanes", "The trust chain", "Where bridges enter", "Closure objecthood", "The exact form of the bridge", "exact finite", "Limitations, open program"]
},
"P055": {
"question": "How can finite controlled systems be typed as agents without assuming goals, and how is agenthood separated from causal agency?",
"thesis": [
"`On Agents and Agenthood` packages finite controlled Markov systems using viability kernels, feasible empowerment under budgeted action channels, and an empirical packaging endomap. Agenthood is treated as persistence of an enabled, viable theory object; agency is a stronger intervention claim that actions change external future distributions under appropriate controls.",
"The separation matters. A system can maintain a viable package or have options without demonstrating causal agency; conversely, a one-off intervention effect need not establish a stable agent object. The paper's finite ring-world experiments and Lean viability anchor support the stated finite framework.",
"The paper does not assume goals, utilities, consciousness, or biological status. It is a controlled instantiation, not a layer-agnostic theorem that all enablement has the same structure.",
"For VII, this is the best nearby model of enablement-versus-causation. A theory can enable the formation or persistence of another without determining it, containing it, or causing each within-layer event. Join and enablement certificates should state which causal counterfactual, if any, they support."
],
"imports": [
"Viability kernel, feasible empowerment, and packaging endomap as separable measurements.",
"Agenthood versus agency distinction.",
"Budgeted action/output channels and finite intervention controls.",
"Finite-model/mechanized-anchor versus broader interpretation separation."
],
"nonclaims": [
"No assumed goals, utilities, consciousness, or biological agency.",
"Viability or empowerment alone does not prove causal agency.",
"A finite ring-world result is not a universal law of enablement.",
"Agenthood is not a synonym for any formed closure object."
],
"vii": [
"Separate enablement, sufficiency, causation, and persistence.",
"Require intervention/control evidence before causal language.",
"Use viability/budget ideas to price sustained joins or enabled layers.",
"Treat the paper as an application pressure test, not the canonical definition of enablement."
],
"anchors": ["Agenthood versus agency", "viability", "feasible empowerment", "packaging engine", "Contributions", "limitations", "nonclaims"]
},
"P044": {
"question": "What does it mean to model language as a ledger of audited theory extensions rather than as next-token prediction alone?",
"thesis": [
"The Language Theory Models paper defines a non-gradient model as an audited ledger of finite theory extensions. Branchwise predictive quotients may agree while recombination-aware quotients differ under larger contexts, so compositional content requires explicit package and recombination records rather than only local predictive statistics.",
"A six-gate promotion panel, closure-deficit and idempotence diagnostics, strict-extension preconditions, and a cadenced closure-recovery loop govern candidate extensions. Fallbacks, proxies, and incomplete evidence retain their source/status and are not laundered into native real evidence.",
"The paper is a prototype and conceptual alternative, not a replacement theorem for gradient language models or a claim about how current systems train. Its finite feasibility experiments support only the declared bounded construction.",
"For VII, the runtime gate discipline is valuable. A rule may be specified, implemented, sound, and still never become reachable or fire. Guard activity must be measured, and a join detector must preserve fallback and pending statuses."
],
"imports": [
"Audited ledger of finite extensions and recombination-aware quotient distinction.",
"Six-gate promotion panel and strict-extension certificate.",
"Fallback/proxy source discipline.",
"Cadenced runtime closure-recovery and gate-activity viewpoint."
],
"nonclaims": [
"Not a substitute for gradient language-model training or a performance claim about current LMs.",
"A configured gate does not prove reachability or firing.",
"Fallback evidence does not become native by successful downstream use.",
"Finite examples do not establish a universal language theory."
],
"vii": [
"Distinguish specified, built, sound, reachable, fired, and occurrent join mechanisms.",
"Require guards to demonstrate activity and preserve PENDING/fallback statuses.",
"Use recombination-aware differences as one possible anti-product witness, not a universal join definition.",
"Carry append-only source and nonclaim records through interaction pipelines."
],
"anchors": ["Audited layers", "Branchwise versus recombination-aware quotients", "Six-gate promotion panel", "Strict-extension certificate", "Cadenced closure-recovery loop", "fallback", "nonclaim"]
},
"P013": {
"question": "In repeated games, what is the extra predictive object called an institution, and how can its strictness and cost be separated from material feedback and interpretation?",
"thesis": [
"The paper identifies an institution with a canonical predictive summary/causal-state refinement for repeated interaction. The one-shot stage game leaves a closure deficit; the repeated-history quotient carries predictive distinctions not definable as a function of the stage game's own vocabulary, yielding a strict extension when the nonfactorization witness is present.",
"The information cost of the institution is related to conditional mutual information, while material feedback, memory, selection, and promotion are analyzed as distinct mechanisms. A strict predictive institution is not simply a norm label or a causal claim about social actors.",
"The evidence includes exact finite analysis and preregistered human data. One timing hypothesis fails; the negative result is retained rather than hidden. Application-specific bridges are imported with their own scopes rather than re-proving the foundational laws.",
"For VII, institutions provide a useful example of a layer formed through repeated interaction, but they do not prove that all layer birth is an interaction theorem. They also reinforce the need to distinguish predictive strictness, material enablement, source attribution, and endogenous maintenance."
],
"imports": [
"Canonical predictive institution as a strict quotient refinement.",
"Closure deficit and conditional-mutual-information cost.",
"Separation of predictive institution, material feedback, memory, selection, and promotion.",
"Preregistered positive and failed timing results with retained status."
],
"nonclaims": [
"Strict predictive extension is not automatically a causal or normative institution.",
"Human-data findings do not establish a universal institution law.",
"A failed timing hypothesis does not erase the structural theorem.",
"The application does not settle whether birth is intrinsically inter-theory."
],
"vii": [
"Use as a pressure test for enablement attribution and repeated-contact formation.",
"Separate predictive novelty from material causation and endogenous maintenance.",
"Retain failed controls and timing hypotheses in the negative-result ledger.",
"Do not promote an application-specific formation pathway into a layer-agnostic law without a bridge."
],
"anchors": ["The stage layer and the closure deficit", "canonical institution", "non-definability", "formation/formed dichotomy", "material forcing", "promotion certificate", "timing", "limitations"]
}
}


def pick_anchors(pid: str, fragments: list[str]) -> list[str]:
    d = json.loads((META / f"{pid}.json").read_text(encoding="utf-8"))
    candidates = []
    for s in d.get("sections", []):
        candidates.append((s.get("title_plain", ""), s.get("line", ""), s.get("level", "section"), "section"))
    for e in d.get("environment_headers", []):
        candidates.append((e.get("name_plain", ""), e.get("line", ""), e.get("kind", "result"), e.get("label", "")))
    out = []
    used = set()
    for frag in fragments:
        low = frag.lower()
        hit = next((c for c in candidates if low in c[0].lower()), None)
        if hit:
            title, line, kind, label = hit
            key = (title, line)
            if key not in used:
                used.add(key)
                lab = f"; `{label}`" if label and label not in {"section", "subsection", "subsubsection"} else ""
                out.append(f"- expanded-source L{line}: {kind} **{title}**{lab}.")
    # Always give some fallback navigation even when a phrase is absent.
    if len(out) < 4:
        for title, line, kind, label in candidates:
            if not title or (title, line) in used:
                continue
            used.add((title,line))
            lab = f"; `{label}`" if label and label not in {"section", "subsection", "subsubsection"} else ""
            out.append(f"- expanded-source L{line}: {kind} **{title}**{lab}.")
            if len(out) >= 6: break
    return out


def main() -> None:
    assert len(N) == 20, len(N)
    for pid, n in N.items():
        meta = json.loads((META / f"{pid}.json").read_text(encoding="utf-8"))
        cat = CAT[pid]
        lines = [
            f"# {pid} — {cat['title']} — Step-1 deep read",
            "",
            "## Provenance and controlling status",
            "",
            f"- Source: `{cat['source_path']}`.",
            f"- Root SHA-256: `{meta['root_sha256']}`.",
            f"- Frozen reading state: `DEEP_READ`.",
            f"- Cluster: `{cat['cluster']}`.",
            f"- Approximate recovered text: {meta.get('plain_word_count',0):,} words; TeX is authoritative.",
            "",
            "## Controlling question",
            "",
            n["question"],
            "",
            "## Reconstructed argument and result architecture",
            "",
        ]
        for p in n["thesis"]: lines += [p, ""]
        lines += ["## Material imported into the Step-1 SBT model", ""]
        lines += [f"- {x}" for x in n["imports"]]
        lines += ["", "## Scope and nonclaim boundary", ""]
        lines += [f"- {x}" for x in n["nonclaims"]]
        lines += ["", "## Foundations VII consequences", ""]
        lines += [f"- {x}" for x in n["vii"]]
        lines += ["", "## Source navigation anchors", ""]
        lines += pick_anchors(pid, n["anchors"])
        lines += ["", "## Step-2 obligation", "", "Extract every definition/result/nonclaim at claim level, record exact hypotheses and proof status, and build bridge records before importing any statement into a Foundations VII candidate law.", ""]
        (OUT / f"{pid}.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"deep_notes={len(N)}")

if __name__ == "__main__":
    main()
