import FoundationsVII.Core.Enablement
import FoundationsVII.Prior.FT11

/-!
# Enablement attribution calculus

Enablement provenance is represented independently of descent, sufficiency,
causation, and endogeny. Honest bridge refinement preserves the source root;
a hidden executor invalidates attribution credit.
-/

namespace FoundationsVII

inductive EnablementSource where
  | theorist
  | carrier
  | peer
  | observer
  | environment
  | endogenousSystem
  | mixed
  deriving Repr, DecidableEq, BEq, Inhabited

def allEnablementSources : List EnablementSource :=
  [.theorist, .carrier, .peer, .observer, .environment, .endogenousSystem, .mixed]

theorem enablementSource_mem_all (source : EnablementSource) :
    source ∈ allEnablementSources := by
  cases source <;> simp [allEnablementSources]

structure AttributionEvidence where
  source : EnablementSource
  sourceRoot : SourceId
  bridgeRoot : SourceId
  sourceTyped : Bool
  executionWitnessed : Bool
  budgetAccounted : Bool
  auditAccounted : Bool
  hiddenExecutor : Bool
  deriving Repr, DecidableEq, BEq

namespace AttributionEvidence

def Valid (evidence : AttributionEvidence) : Prop :=
  evidence.sourceTyped = true ∧
  evidence.executionWitnessed = true ∧
  evidence.budgetAccounted = true ∧
  evidence.auditAccounted = true ∧
  evidence.hiddenExecutor = false

instance (evidence : AttributionEvidence) : Decidable (Valid evidence) := by
  unfold Valid
  infer_instance

def HonestBridgeRefinement (old newer : AttributionEvidence) : Prop :=
  Valid old ∧ Valid newer ∧
  old.sourceRoot = newer.sourceRoot ∧
  newer.bridgeRoot = newer.sourceRoot

theorem valid_has_no_hidden_executor {evidence : AttributionEvidence}
    (h : Valid evidence) : evidence.hiddenExecutor = false := h.2.2.2.2

theorem honest_refinement_preserves_source_root
    {old newer : AttributionEvidence}
    (h : HonestBridgeRefinement old newer) :
    old.sourceRoot = newer.sourceRoot := h.2.2.1

end AttributionEvidence

structure AttributedEnablement where
  record : EnablementRecord
  evidence : AttributionEvidence
  deriving Repr, DecidableEq, BEq

namespace AttributedEnablement

def WellFormed (enablement : AttributedEnablement) : Prop :=
  EnablementRecord.WellFormed enablement.record ∧
  AttributionEvidence.Valid enablement.evidence ∧
  enablement.record.executed = true ∧
  enablement.record.sourceId = enablement.evidence.sourceRoot

instance (enablement : AttributedEnablement) : Decidable (WellFormed enablement) := by
  unfold WellFormed
  infer_instance

theorem wellFormed_has_typed_source {enablement : AttributedEnablement}
    (h : WellFormed enablement) :
    enablement.evidence.sourceTyped = true := h.2.1.1

theorem wellFormed_has_execution_witness {enablement : AttributedEnablement}
    (h : WellFormed enablement) :
    enablement.evidence.executionWitnessed = true := h.2.1.2.1

theorem wellFormed_has_budget_accounting {enablement : AttributedEnablement}
    (h : WellFormed enablement) :
    enablement.evidence.budgetAccounted = true := h.2.1.2.2.1

theorem wellFormed_has_audit_accounting {enablement : AttributedEnablement}
    (h : WellFormed enablement) :
    enablement.evidence.auditAccounted = true := h.2.1.2.2.2.1

theorem wellFormed_has_no_hidden_executor {enablement : AttributedEnablement}
    (h : WellFormed enablement) :
    enablement.evidence.hiddenExecutor = false := h.2.1.2.2.2.2

theorem hidden_execution_defeats_attribution
    (enablement : AttributedEnablement)
    (hHidden : enablement.evidence.hiddenExecutor = true) :
    ¬ WellFormed enablement := by
  intro h
  have hNoHidden := wellFormed_has_no_hidden_executor h
  rw [hHidden] at hNoHidden
  exact Bool.noConfusion hNoHidden

end AttributedEnablement

structure AttributionRefinement where
  before : AttributionEvidence
  after : AttributionEvidence
  honest : Bool
  deriving Repr, DecidableEq, BEq

namespace AttributionRefinement

def Stable (refinement : AttributionRefinement) : Prop :=
  refinement.honest = true ∧
  AttributionEvidence.HonestBridgeRefinement refinement.before refinement.after

theorem stable_preserves_attribution_root {refinement : AttributionRefinement}
    (h : Stable refinement) :
    refinement.before.sourceRoot = refinement.after.sourceRoot :=
  AttributionEvidence.honest_refinement_preserves_source_root h.2

end AttributionRefinement

/-- C012 boundary: attribution is provenance data, not descent. -/
structure AttributionSeparationProfile where
  attributed : Bool
  descentCertified : Bool
  sufficient : Bool
  causalChannel : Bool
  endogenous : Bool
  deriving Repr, DecidableEq, BEq

private def attributionWithoutOtherCredits : AttributionSeparationProfile :=
  { attributed := true, descentCertified := false, sufficient := false,
    causalChannel := false, endogenous := false }

theorem attribution_does_not_imply_descent_sufficiency_causation_or_endogeny :
    ∃ profile : AttributionSeparationProfile,
      profile.attributed = true ∧
      profile.descentCertified = false ∧
      profile.sufficient = false ∧
      profile.causalChannel = false ∧
      profile.endogenous = false := by
  exact ⟨attributionWithoutOtherCredits, rfl, rfl, rfl, rfl, rfl⟩

end FoundationsVII
