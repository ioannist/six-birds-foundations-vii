import FoundationsVII.Join.Budget

/-!
# Parent retention, refinement effects, and join descent

Retention is recorded per parent and per law/source component.  Refinement may
preserve, strengthen, weaken, or destroy a join; no unconditional monotonicity
is asserted.
-/

namespace FoundationsVII

inductive ParentRetentionStatus where
  | full
  | «partial»
  | erased
  deriving Repr, DecidableEq, BEq, Inhabited

def allParentRetentionStatuses : List ParentRetentionStatus :=
  [.full, .«partial», .erased]

theorem parentRetentionStatus_mem_all (value : ParentRetentionStatus) :
    value ∈ allParentRetentionStatuses := by
  cases value <;> simp [allParentRetentionStatuses]

structure ParentRetentionMap where
  parentTheory : TheoryId
  compositeTheory : TheoryId
  retainedObjects : List String
  retainedLaws : List String
  sourceIdentityRetained : Bool
  recoverable : Bool
  status : ParentRetentionStatus
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace ParentRetentionMap

def WellFormed (record : ParentRetentionMap) : Prop :=
  record.parentTheory ≠ record.compositeTheory ∧
  record.audit.entries ≠ [] ∧
  (record.status = .full →
    record.retainedObjects ≠ [] ∧
    record.retainedLaws ≠ [] ∧
    record.sourceIdentityRetained = true ∧
    record.recoverable = true) ∧
  (record.status = .«partial» →
    record.retainedObjects ≠ [] ∨ record.retainedLaws ≠ []) ∧
  (record.status = .erased → record.recoverable = false)

instance (record : ParentRetentionMap) : Decidable (WellFormed record) := by
  unfold WellFormed
  infer_instance

def FullRetention (record : ParentRetentionMap) : Prop :=
  WellFormed record ∧ record.status = .full

instance (record : ParentRetentionMap) : Decidable (FullRetention record) := by
  unfold FullRetention
  infer_instance

theorem full_retention_is_recoverable {record : ParentRetentionMap}
    (h : FullRetention record) : record.recoverable = true := by
  have hFields := h.1.2.2.1 h.2
  exact hFields.2.2.2

theorem erased_parent_is_not_recoverable {record : ParentRetentionMap}
    (h : WellFormed record) (hErased : record.status = .erased) :
    record.recoverable = false := h.2.2.2.2 hErased

end ParentRetentionMap

structure JoinDescentCertificate where
  joinCertificateId : CertificateId
  parentMaps : List ParentRetentionMap
  allParentsAccounted : Bool
  sourceIdentitiesAccounted : Bool
  lawsAccounted : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace JoinDescentCertificate

def Valid (certificate : JoinDescentCertificate) : Prop :=
  certificate.parentMaps ≠ [] ∧
  (∀ record, record ∈ certificate.parentMaps →
    ParentRetentionMap.WellFormed record) ∧
  certificate.allParentsAccounted = true ∧
  certificate.sourceIdentitiesAccounted = true ∧
  certificate.lawsAccounted = true ∧
  certificate.audit.entries ≠ []

instance (certificate : JoinDescentCertificate) : Decidable (Valid certificate) := by
  unfold Valid
  infer_instance

theorem valid_accounts_for_all_parents {certificate : JoinDescentCertificate}
    (h : Valid certificate) : certificate.allParentsAccounted = true := h.2.2.1

end JoinDescentCertificate

inductive RefinementEffect where
  | preserves
  | strengthens
  | weakens
  | destroys
  deriving Repr, DecidableEq, BEq, Inhabited

def allRefinementEffects : List RefinementEffect :=
  [.preserves, .strengthens, .weakens, .destroys]

theorem refinementEffect_mem_all (value : RefinementEffect) :
    value ∈ allRefinementEffects := by
  cases value <;> simp [allRefinementEffects]

structure ParentRefinementRecord where
  before : ParentRetentionMap
  after : ParentRetentionMap
  compatibilityPreserved : Bool
  strictnessPreserved : Bool
  effect : RefinementEffect
  residualChanged : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace ParentRefinementRecord

def WellFormed (record : ParentRefinementRecord) : Prop :=
  ParentRetentionMap.WellFormed record.before ∧
  ParentRetentionMap.WellFormed record.after ∧
  record.audit.entries ≠ [] ∧
  (record.effect = .preserves →
    record.compatibilityPreserved = true ∧
    record.strictnessPreserved = true) ∧
  (record.effect = .destroys →
    record.compatibilityPreserved = false ∨
    record.strictnessPreserved = false)

instance (record : ParentRefinementRecord) : Decidable (WellFormed record) := by
  unfold WellFormed
  infer_instance

end ParentRefinementRecord

private def fullParentMap : ParentRetentionMap :=
  { parentTheory := 1
    compositeTheory := 3
    retainedObjects := ["carrier", "interface"]
    retainedLaws := ["closure", "audit"]
    sourceIdentityRetained := true
    recoverable := true
    status := .full
    audit := phase3Audit }

private def partialParentMap : ParentRetentionMap :=
  { parentTheory := 2
    compositeTheory := 3
    retainedObjects := ["carrier"]
    retainedLaws := []
    sourceIdentityRetained := true
    recoverable := true
    status := .«partial»
    audit := phase3Audit }

private def erasedParentMap : ParentRetentionMap :=
  { parentTheory := 2
    compositeTheory := 4
    retainedObjects := []
    retainedLaws := []
    sourceIdentityRetained := false
    recoverable := false
    status := .erased
    audit := phase3Audit }

private def preservationRefinement : ParentRefinementRecord :=
  { before := fullParentMap
    after := fullParentMap
    compatibilityPreserved := true
    strictnessPreserved := true
    effect := .preserves
    residualChanged := false
    audit := phase3Audit }

private def strengtheningRefinement : ParentRefinementRecord :=
  { before := partialParentMap
    after := fullParentMap
    compatibilityPreserved := true
    strictnessPreserved := true
    effect := .strengthens
    residualChanged := false
    audit := phase3Audit }

private def weakeningRefinement : ParentRefinementRecord :=
  { before := fullParentMap
    after := partialParentMap
    compatibilityPreserved := true
    strictnessPreserved := false
    effect := .weakens
    residualChanged := true
    audit := phase3Audit }

private def destructionRefinement : ParentRefinementRecord :=
  { before := partialParentMap
    after := erasedParentMap
    compatibilityPreserved := false
    strictnessPreserved := false
    effect := .destroys
    residualChanged := true
    audit := phase3Audit }

private def descentWitness : JoinDescentCertificate :=
  { joinCertificateId := 77
    parentMaps := [fullParentMap, partialParentMap]
    allParentsAccounted := true
    sourceIdentitiesAccounted := true
    lawsAccounted := true
    audit := phase3Audit }

theorem full_and_partial_retention_are_explicit :
    ParentRetentionMap.FullRetention fullParentMap ∧
    ParentRetentionMap.WellFormed partialParentMap ∧
    partialParentMap.status = ParentRetentionStatus.«partial» := by
  decide

theorem composite_formation_does_not_imply_parent_retention :
    ParentRetentionMap.WellFormed erasedParentMap ∧
    erasedParentMap.status = ParentRetentionStatus.erased ∧
    erasedParentMap.recoverable = false := by
  decide

theorem join_descent_certificate_accounts_for_retained_parents :
    JoinDescentCertificate.Valid descentWitness := by
  simp [JoinDescentCertificate.Valid, descentWitness,
    ParentRetentionMap.WellFormed, fullParentMap, partialParentMap,
    phase3Audit, phase3AuditEntry]

theorem refinement_effects_have_all_four_controls :
    ParentRefinementRecord.WellFormed preservationRefinement ∧
    ParentRefinementRecord.WellFormed strengtheningRefinement ∧
    ParentRefinementRecord.WellFormed weakeningRefinement ∧
    ParentRefinementRecord.WellFormed destructionRefinement ∧
    preservationRefinement.effect = RefinementEffect.preserves ∧
    strengtheningRefinement.effect = RefinementEffect.strengthens ∧
    weakeningRefinement.effect = RefinementEffect.weakens ∧
    destructionRefinement.effect = RefinementEffect.destroys := by
  decide

theorem refinement_may_preserve_or_destroy_join_evidence :
    ParentRefinementRecord.WellFormed preservationRefinement ∧
    ParentRefinementRecord.WellFormed destructionRefinement ∧
    preservationRefinement.effect = RefinementEffect.preserves ∧
    destructionRefinement.effect = RefinementEffect.destroys := by
  decide

/-- DP10 terminal ruling: parent refinement is not unconditionally monotone. -/
theorem no_unconditional_join_monotonicity_under_refinement :
    (∃ record : ParentRefinementRecord,
      ParentRefinementRecord.WellFormed record ∧
      record.effect = RefinementEffect.preserves) ∧
    (∃ record : ParentRefinementRecord,
      ParentRefinementRecord.WellFormed record ∧
      record.effect = RefinementEffect.destroys) := by
  exact ⟨⟨preservationRefinement, by decide, rfl⟩,
    ⟨destructionRefinement, by decide, rfl⟩⟩

end FoundationsVII
