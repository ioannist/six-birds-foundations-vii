import FoundationsVII.Corollaries.All
import FoundationsVII.Models.Finite.Phase5.All

/-!
# Final Foundations VII science-release registries

These executable registries close the candidate, formalization-target, no-go,
decision, and cross-family corollary surfaces.  Scientific disposition is kept
separate from kernel replay state: the replay has been executed locally, so the
recorded verification state is `kernelVerified`.  The `#print axioms` receipt for
every public theorem is `formalization/foundations_vii_lab/phase5/results/lean_axioms.txt`.

Disposition is still *not* upgraded by the replay: a `formalSchema` remains a
schema and a `closedDeferral` remains deferred.  `kernelVerified` records only
that the recorded Lean assets elaborate and carry executed axiom receipts.
-/

-- The closure registries are checked by kernel evaluation over string fields.
-- Elaboration resources only: no assumption is added and no theorem statement
-- changes.
set_option maxHeartbeats 0
set_option maxRecDepth 100000

namespace FoundationsVII.Release

inductive TerminalDisposition where
  | formalSchema
  | leanKernelProved
  | leanDecidableFinite
  | conditionalTheorem
  | constructiveCountermodel
  | refutedCandidate
  | closedDeferral
  deriving Repr, DecidableEq, BEq, Inhabited

inductive VerificationState where
  | sourceCompleteExternalKernelReplayPending
  | kernelVerified
  deriving Repr, DecidableEq, BEq, Inhabited

structure CandidateClosure where
  candidateId : String
  name : String
  disposition : TerminalDisposition
  verification : VerificationState
  note : String
  deriving Repr, DecidableEq, BEq

structure FormalizationTargetClosure where
  targetId : String
  name : String
  status : String
  deriving Repr, DecidableEq, BEq

structure NoGoClosure where
  noGoId : String
  name : String
  status : String
  deriving Repr, DecidableEq, BEq

structure DecisionClosure where
  decisionId : String
  ruling : String
  closureKind : String
  deriving Repr, DecidableEq, BEq

structure CorollaryClosure where
  corollaryId : String
  declaration : String
  verification : VerificationState
  deriving Repr, DecidableEq, BEq

def finalCandidateClosures : List CandidateClosure :=
[
  { candidateId := "VII-C001", name := "Accessible-domain state normal form", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C002", name := "Lawful admission transition system", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C003", name := "Bootstrap obstruction theorem", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C004", name := "Neutral seed and provisioning certificate", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C005", name := "Common-origin non-transfer law", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C006", name := "Prospective commitment certificate", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C007", name := "Join-entry record normal form", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C008", name := "Join existence and obstruction status calculus", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C009", name := "Strict join certificate and anti-product witness", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C010", name := "Source-independence gate", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C011", name := "Join budget and payment ledger", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C012", name := "Enablement record and attribution calculus", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C013", name := "Endogenous enablement criterion", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C014", name := "Birth/contact-surface classification", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C015", name := "Typed transmission and descent-fidelity law", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C016", name := "Peer contact and transport without join", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C017", name := "Interaction-order residue and holonomy", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C018", name := "Admission confluence and seed-dependence law", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C019", name := "Access/join residual and obstruction-dissolution ledger", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C020", name := "Bridge and semantic-withdrawal discipline", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C021", name := "Reachability, guard activity, and horizon law", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C022", name := "Exposure, recoverability, admissibility, and rigidity calculus", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C023", name := "Negative-result quantifier discipline", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C024", name := "Claim-grade and normative-specification discipline", disposition := .formalSchema, verification := .kernelVerified, note := "Terminal formalSchema asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C025", name := "Two-Theory World detector contract", disposition := .leanDecidableFinite, verification := .kernelVerified, note := "The frozen 24-scenario/27-countermodel detector is decidable over its declared finite carrier." },
  { candidateId := "VII-C026", name := "Categorical reduction decision", disposition := .closedDeferral, verification := .kernelVerified, note := "Unconditional categorical reduction is closed as a deferral; special-case representations remain permitted under explicit hypotheses." },
  { candidateId := "VII-C027", name := "Enablement-chain composition law", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C028", name := "Primitive-operation algebra readiness criterion", disposition := .closedDeferral, verification := .kernelVerified, note := "The full generators-and-relations algebra is closed as a deferral; only the smaller resource-delta fragment is landed." },
  { candidateId := "VII-C029", name := "Observer and instrument occupancy law", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C030", name := "Parent refinement, retention, and join descent", disposition := .refutedCandidate, verification := .kernelVerified, note := "Unconditional refinement monotonicity is refuted; preserve/strengthen/weaken/destroy cases are typed and conditional." },
  { candidateId := "VII-C031", name := "Contact-degree conservation decision", disposition := .refutedCandidate, verification := .kernelVerified, note := "A universal conserved scalar contact degree is refuted over the declared assay; typed ledgers remain controlling." },
  { candidateId := "VII-C032", name := "Interaction arrow, irreversibility, and cross-time contact", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C033", name := "Coverage-qualified certified non-interaction", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C034", name := "Enablement without descent separation theorem", disposition := .constructiveCountermodel, verification := .kernelVerified, note := "Constructive witnesses separate enablement from descent and from sufficiency without denying co-occurring positive cases." },
  { candidateId := "VII-C035", name := "No-free-join and self-bootstrap no-go family", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." },
  { candidateId := "VII-C036", name := "Join-created obstruction and needle law", disposition := .conditionalTheorem, verification := .kernelVerified, note := "Terminal conditionalTheorem asset with explicit scope and nonclaim registry." }
]

def finalFormalizationTargetClosures : List FormalizationTargetClosure :=
[
  { targetId := "FT01", name := "Finite access-status data model", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT02", name := "Admission reachability graph and occurrence separation", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT03", name := "Bootstrap obstruction", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT04", name := "Prospective commitment timestamp/budget record", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT05", name := "Source and bridge ledger", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT06", name := "Typed contact witness", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT07", name := "Join certificate normal form", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT08", name := "Anti-product/nonfactorization witness", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT09", name := "Join obstruction and budget record", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT10", name := "Coverage-qualified non-interaction certificate", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT11", name := "Enablement record", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT12", name := "Endogenous generator criterion", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT13", name := "Transmission/descent fidelity", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT14", name := "Confluence and critical-pair finite models", status := "CLOSED_MIXED_THEOREMS_AND_TERMINAL_FULL_ALGEBRA_DEFERRAL" },
  { targetId := "FT15", name := "Interaction holonomy/arrow separation", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT16", name := "Budget and observer occupancy", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT17", name := "Negative quantifier and claim-grade rules", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT18", name := "No-free-access/no-free-join lemmas", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT19", name := "Parent retention and refinement transport", status := "CLOSED_KERNEL_VERIFIED" },
  { targetId := "FT20", name := "Residual/needle and finite-world semantics", status := "CLOSED_KERNEL_VERIFIED" }
]

def finalNoGoClosures : List NoGoClosure :=
[
  { noGoId := "NGVII-01", name := "No first extension without seed or reachable generator", status := "CONDITIONAL_THEOREM_WITH_NAMED_ESCAPES_SOURCE_COMPLETE" },
  { noGoId := "NGVII-02", name := "No resemblance-only independence-sensitive join credit", status := "CONDITIONAL_THEOREM_WITH_NAMED_ESCAPES_SOURCE_COMPLETE" },
  { noGoId := "NGVII-03", name := "No retrospective self-certification of prospective commitment", status := "CONDITIONAL_THEOREM_WITH_NAMED_ESCAPES_SOURCE_COMPLETE" },
  { noGoId := "NGVII-04", name := "No automatic total-lens transfer to a partial target", status := "CONDITIONAL_THEOREM_WITH_NAMED_ESCAPES_SOURCE_COMPLETE" },
  { noGoId := "NGVII-05", name := "No native credit from unpriced positive observer occupancy", status := "CONDITIONAL_THEOREM_WITH_NAMED_ESCAPES_SOURCE_COMPLETE" },
  { noGoId := "NGVII-06", name := "No strict join from contact alone", status := "CONDITIONAL_THEOREM_WITH_NAMED_ESCAPES_SOURCE_COMPLETE" },
  { noGoId := "NGVII-07", name := "No strictness from product/common-refinement structure alone", status := "CONDITIONAL_THEOREM_WITH_NAMED_ESCAPES_SOURCE_COMPLETE" },
  { noGoId := "NGVII-08", name := "No source-independence credit from one uncertified lineage", status := "CONDITIONAL_THEOREM_WITH_NAMED_ESCAPES_SOURCE_COMPLETE" },
  { noGoId := "NGVII-09", name := "No positive-cost join credit without payment or zero-cost certificate", status := "CONDITIONAL_THEOREM_WITH_NAMED_ESCAPES_SOURCE_COMPLETE" },
  { noGoId := "NGVII-10", name := "No directional arrow from holonomy alone", status := "CONDITIONAL_THEOREM_WITH_NAMED_ESCAPES_SOURCE_COMPLETE" },
  { noGoId := "NGVII-11", name := "No occurrence from reachability alone", status := "CONDITIONAL_THEOREM_WITH_NAMED_ESCAPES_SOURCE_COMPLETE" }
]

def finalDecisionClosures : List DecisionClosure :=
[
  { decisionId := "DP01", ruling := "Keep it as a candidate record; require a reduction proof before calling it derived.", closureKind := "TERMINAL_SCIENCE_RULING" },
  { decisionId := "DP02", ruling := "Treat the list as scoped to the declared finite interface family.", closureKind := "TERMINAL_SCIENCE_RULING" },
  { decisionId := "DP03", ruling := "Require it only for independence-sensitive claims; preserve non-independent joins as separately typed.", closureKind := "TERMINAL_SCIENCE_RULING" },
  { decisionId := "DP04", ruling := "Defer unconditional reduction; permit special-case theorems.", closureKind := "TERMINAL_SCIENCE_RULING" },
  { decisionId := "DP05", ruling := "No; retain typed ledgers unless a representation theorem is proved.", closureKind := "TERMINAL_SCIENCE_RULING" },
  { decisionId := "DP06", ruling := "Do not posit one; retain an explicit test program.", closureKind := "TERMINAL_SCIENCE_RULING" },
  { decisionId := "DP07", ruling := "Use explicit synchronization/order witnesses; no unique simultaneity assumption.", closureKind := "TERMINAL_SCIENCE_RULING" },
  { decisionId := "DP08", ruling := "Use carried, reachable, executed, audited, and budgeted generator criteria.", closureKind := "TERMINAL_SCIENCE_RULING" },
  { decisionId := "DP09", ruling := "Keep both cases typed and require an objecthood witness for created participants.", closureKind := "TERMINAL_SCIENCE_RULING" },
  { decisionId := "DP10", ruling := "No monotonicity assumption; classify preserve/strengthen/weaken/destroy cases.", closureKind := "TERMINAL_SCIENCE_RULING" },
  { decisionId := "DP11", ruling := "No; require a separate drive/path-asymmetry certificate.", closureKind := "TERMINAL_SCIENCE_RULING" },
  { decisionId := "DP12", ruling := "Defer until categorical and operational composition are fixed.", closureKind := "TERMINAL_SCIENCE_RULING" },
  { decisionId := "DP13", ruling := "Keep both non-independent and unresolved.", closureKind := "SOURCE_GOVERNANCE_BOUNDARY_NONBLOCKING" },
  { decisionId := "DP14", ruling := "No; abstract-only until missing source files are supplied.", closureKind := "SOURCE_GOVERNANCE_BOUNDARY_NONBLOCKING" },
  { decisionId := "DP15", ruling := "Only as strong as the covered family, detector power, budget, and horizon.", closureKind := "TERMINAL_SCIENCE_RULING" }
]

def finalCorollaryClosures : List CorollaryClosure :=
[
  { corollaryId := "FVII-COR-001", declaration := "FoundationsVII.ProspectiveJoinAdmission.certified_has_temporal_source_join_and_payment", verification := .kernelVerified },
  { corollaryId := "FVII-COR-002", declaration := "FoundationsVII.ProspectiveJoinAdmission.retrospective_registration_blocks_prospective_join_credit", verification := .kernelVerified },
  { corollaryId := "FVII-COR-003", declaration := "FoundationsVII.ProspectiveJoinAdmission.certified_preserves_declared_source_alignment", verification := .kernelVerified },
  { corollaryId := "FVII-COR-004", declaration := "FoundationsVII.IndependentBudgetedJoin.certified_has_independence_payment_and_capacity_bound", verification := .kernelVerified },
  { corollaryId := "FVII-COR-005", declaration := "FoundationsVII.IndependentBudgetedJoin.source_and_payment_gates_remain_distinct", verification := .kernelVerified },
  { corollaryId := "FVII-COR-006", declaration := "FoundationsVII.JoinClaimUnderCoverage.certified_noninteraction_excludes_strict_join", verification := .kernelVerified },
  { corollaryId := "FVII-COR-007", declaration := "FoundationsVII.JoinClaimUnderCoverage.certified_noninteraction_retains_escape_routes", verification := .kernelVerified },
  { corollaryId := "FVII-COR-008", declaration := "FoundationsVII.ResidualAwareEnablementChain.certified_accumulates_resources_and_preserves_residuals", verification := .kernelVerified },
  { corollaryId := "FVII-COR-009", declaration := "FoundationsVII.ResidualAwareEnablementChain.join_created_needle_blocks_zero_residual_reading", verification := .kernelVerified },
  { corollaryId := "FVII-COR-010", declaration := "FoundationsVII.RefinedDescentPackage.preserving_refinement_with_valid_descent_preserves_three_gates", verification := .kernelVerified },
  { corollaryId := "FVII-COR-011", declaration := "FoundationsVII.RefinedDescentPackage.destroying_refinement_exhibits_a_failed_join_gate", verification := .kernelVerified },
  { corollaryId := "FVII-COR-012", declaration := "FoundationsVII.RefinedDescentPackage.valid_descent_does_not_erase_refinement_obstruction", verification := .kernelVerified },
  { corollaryId := "FVII-COR-013", declaration := "FoundationsVII.no_free_first_join_two_gate_obstruction", verification := .kernelVerified },
  { corollaryId := "FVII-COR-014", declaration := "FoundationsVII.seeded_and_paid_first_join_escape", verification := .kernelVerified },
  { corollaryId := "FVII-COR-015", declaration := "FoundationsVII.strict_join_and_holonomy_do_not_replace_drive", verification := .kernelVerified },
  { corollaryId := "FVII-COR-016", declaration := "FoundationsVII.holonomy_with_independent_drive_supports_arrow", verification := .kernelVerified },
  { corollaryId := "FVII-COR-017", declaration := "FoundationsVII.ScopedNegativePackage.certified_excludes_contact_and_occurrence_at_declared_scope", verification := .kernelVerified },
  { corollaryId := "FVII-COR-018", declaration := "FoundationsVII.ScopedNegativePackage.point_null_plus_bounded_horizon_is_not_automatically_global", verification := .kernelVerified },
  { corollaryId := "FVII-COR-019", declaration := "FoundationsVII.ObserverEndogenyPackage.certified_requires_pricing_and_internal_execution", verification := .kernelVerified },
  { corollaryId := "FVII-COR-020", declaration := "FoundationsVII.ObserverEndogenyPackage.unpriced_observer_blocks_joint_native_endogenous_credit", verification := .kernelVerified },
  { corollaryId := "FVII-COR-021", declaration := "FoundationsVII.ObserverEndogenyPackage.zero_occupancy_escape_preserves_endogenous_credit", verification := .kernelVerified }
]

def finalCandidateIds : List String := finalCandidateClosures.map CandidateClosure.candidateId
def finalTargetIds : List String := finalFormalizationTargetClosures.map FormalizationTargetClosure.targetId
def finalNoGoIds : List String := finalNoGoClosures.map NoGoClosure.noGoId
def finalDecisionIds : List String := finalDecisionClosures.map DecisionClosure.decisionId
def finalCorollaryIds : List String := finalCorollaryClosures.map CorollaryClosure.corollaryId

theorem final_candidate_census : finalCandidateClosures.length = 36 := by decide
theorem final_candidate_ids_unique : finalCandidateIds.Nodup := by decide
theorem final_target_census : finalFormalizationTargetClosures.length = 20 := by decide
theorem final_target_ids_unique : finalTargetIds.Nodup := by decide
theorem final_no_go_census : finalNoGoClosures.length = 11 := by decide
theorem final_no_go_ids_unique : finalNoGoIds.Nodup := by decide
theorem final_decision_census : finalDecisionClosures.length = 15 := by decide
theorem final_decision_ids_unique : finalDecisionIds.Nodup := by decide
theorem final_corollary_census : finalCorollaryClosures.length = 21 := by decide
theorem final_corollary_ids_unique : finalCorollaryIds.Nodup := by decide

theorem no_candidate_remains_specification_ready_unclosed :
    finalCandidateClosures.all (fun row => row.note != "") = true := by decide

theorem kernel_replay_state_is_explicit_for_every_corollary :
    finalCorollaryClosures.all (fun row =>
      row.verification == .kernelVerified) = true := by decide

end FoundationsVII.Release
