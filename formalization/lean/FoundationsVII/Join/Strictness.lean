import FoundationsVII.Join.Status

/-!
# Strict join certificates and anti-product novelty

Strictness is a conjunction of independently inspectable evidence.  In
particular, anti-product novelty does not supply objecthood, parent retention,
source independence, budget settlement, or directionality.
-/

namespace FoundationsVII

structure AntiProductWitness where
  jointDistinctionPresent : Bool
  factorsThroughLeft : Bool
  factorsThroughRight : Bool
  factorsThroughDeclaredProduct : Bool
  factorsThroughCommonRefinement : Bool
  relabelOnly : Bool
  schedulingOnly : Bool
  coarseningOnly : Bool
  witnessDescription : String
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace AntiProductWitness

def Valid (witness : AntiProductWitness) : Prop :=
  witness.jointDistinctionPresent = true ∧
  witness.factorsThroughLeft = false ∧
  witness.factorsThroughRight = false ∧
  witness.factorsThroughDeclaredProduct = false ∧
  witness.factorsThroughCommonRefinement = false ∧
  witness.relabelOnly = false ∧
  witness.schedulingOnly = false ∧
  witness.coarseningOnly = false ∧
  witness.witnessDescription ≠ "" ∧
  witness.audit.entries ≠ []

instance (witness : AntiProductWitness) : Decidable (Valid witness) := by
  unfold Valid
  infer_instance

theorem valid_is_nonfactorizing {witness : AntiProductWitness}
    (h : Valid witness) :
    witness.factorsThroughLeft = false ∧
    witness.factorsThroughRight = false ∧
    witness.factorsThroughDeclaredProduct = false ∧
    witness.factorsThroughCommonRefinement = false := by
  exact ⟨h.2.1, h.2.2.1, h.2.2.2.1, h.2.2.2.2.1⟩

theorem relabel_only_fails {witness : AntiProductWitness}
    (hRelabel : witness.relabelOnly = true) : ¬ Valid witness := by
  intro h
  have hFalse : true = false := by
    calc
      true = witness.relabelOnly := hRelabel.symm
      _ = false := h.2.2.2.2.2.1
  exact Bool.noConfusion hFalse

theorem scheduling_only_fails {witness : AntiProductWitness}
    (hScheduling : witness.schedulingOnly = true) : ¬ Valid witness := by
  intro h
  have hFalse : true = false := by
    calc
      true = witness.schedulingOnly := hScheduling.symm
      _ = false := h.2.2.2.2.2.2.1
  exact Bool.noConfusion hFalse

theorem coarsening_only_fails {witness : AntiProductWitness}
    (hCoarsening : witness.coarseningOnly = true) : ¬ Valid witness := by
  intro h
  have hFalse : true = false := by
    calc
      true = witness.coarseningOnly := hCoarsening.symm
      _ = false := h.2.2.2.2.2.2.2.1
  exact Bool.noConfusion hFalse

end AntiProductWitness

structure StrictJoinEvidence where
  certificateId : CertificateId
  candidate : JoinCandidate
  objecthoodCertified : Bool
  leftParentRecoverable : Bool
  rightParentRecoverable : Bool
  antiProduct : AntiProductWitness
  sourceIndependent : Bool
  budgetSettled : Bool
  directionalityCertified : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace StrictJoinEvidence

def Certified (evidence : StrictJoinEvidence) : Prop :=
  JoinCandidate.WellFormed evidence.candidate ∧
  evidence.objecthoodCertified = true ∧
  evidence.leftParentRecoverable = true ∧
  evidence.rightParentRecoverable = true ∧
  AntiProductWitness.Valid evidence.antiProduct ∧
  evidence.sourceIndependent = true ∧
  evidence.budgetSettled = true ∧
  evidence.audit.entries ≠ []

instance (evidence : StrictJoinEvidence) : Decidable (Certified evidence) := by
  unfold Certified
  infer_instance

theorem certified_has_objecthood {evidence : StrictJoinEvidence}
    (h : Certified evidence) : evidence.objecthoodCertified = true := h.2.1

theorem certified_retains_both_parents {evidence : StrictJoinEvidence}
    (h : Certified evidence) :
    evidence.leftParentRecoverable = true ∧
    evidence.rightParentRecoverable = true := ⟨h.2.2.1, h.2.2.2.1⟩

theorem certified_has_anti_product_novelty {evidence : StrictJoinEvidence}
    (h : Certified evidence) : AntiProductWitness.Valid evidence.antiProduct :=
  h.2.2.2.2.1

theorem certified_has_source_and_budget_gates {evidence : StrictJoinEvidence}
    (h : Certified evidence) :
    evidence.sourceIndependent = true ∧ evidence.budgetSettled = true :=
  ⟨h.2.2.2.2.2.1, h.2.2.2.2.2.2.1⟩

/-- Directionality is deliberately absent from `Certified`; it needs a
separate P6-style drive certificate. -/
theorem certified_does_not_supply_directionality
    {evidence : StrictJoinEvidence} (h : Certified evidence) :
    evidence.directionalityCertified = true ∨
      evidence.directionalityCertified = false := by
  cases hDirection : evidence.directionalityCertified <;> simp [hDirection]

end StrictJoinEvidence

structure StrictJoinProfile where
  objecthood : Bool
  leftRetention : Bool
  rightRetention : Bool
  antiProduct : Bool
  sourceIndependent : Bool
  budgetSettled : Bool
  directionality : Bool
  deriving Repr, DecidableEq, BEq

namespace StrictJoinProfile

def Certified (profile : StrictJoinProfile) : Prop :=
  profile.objecthood = true ∧
  profile.leftRetention = true ∧
  profile.rightRetention = true ∧
  profile.antiProduct = true ∧
  profile.sourceIndependent = true ∧
  profile.budgetSettled = true

instance (profile : StrictJoinProfile) : Decidable (Certified profile) := by
  unfold Certified
  infer_instance

private def directionlessStrict : StrictJoinProfile :=
  { objecthood := true
    leftRetention := true
    rightRetention := true
    antiProduct := true
    sourceIndependent := true
    budgetSettled := true
    directionality := false }

private def noveltyWithoutObjecthood : StrictJoinProfile :=
  { directionlessStrict with objecthood := false }

private def strictnessWithoutRetention : StrictJoinProfile :=
  { directionlessStrict with leftRetention := false }

theorem directionless_strict_profile_exists :
    Certified directionlessStrict ∧ directionlessStrict.directionality = false := by
  decide

theorem anti_product_does_not_imply_objecthood :
    noveltyWithoutObjecthood.antiProduct = true ∧
    noveltyWithoutObjecthood.objecthood = false ∧
    ¬ Certified noveltyWithoutObjecthood := by
  decide

theorem strictness_does_not_imply_parent_retention :
    strictnessWithoutRetention.antiProduct = true ∧
    strictnessWithoutRetention.leftRetention = false ∧
    ¬ Certified strictnessWithoutRetention := by
  decide

end StrictJoinProfile

end FoundationsVII
