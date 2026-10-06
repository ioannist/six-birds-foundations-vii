import SixBirds.FATCD

namespace SixBirds

structure ClaimRecord where
  claimId : Nat
  level : Level
  claimRecorded : Bool
  promotionsRecorded : Bool
  translationsRecorded : Bool
  selectedLiftsRecorded : Bool
  forgettingLossesRecorded : Bool
  visibilityRecorded : Bool
  empiricalBridgeRecorded : Bool
  instrument : Option Nat

def HonestBookkeeping (c : ClaimRecord) : Prop :=
  c.claimRecorded = true ∧
  c.promotionsRecorded = true ∧
  c.translationsRecorded = true ∧
  c.selectedLiftsRecorded = true ∧
  c.forgettingLossesRecorded = true ∧
  c.visibilityRecorded = true ∧
  c.empiricalBridgeRecorded = true

def AdmissibleClaim (c : ClaimRecord) : Prop :=
  HonestBookkeeping c

def HasLevelProfile (_D : FATCD) (c : ClaimRecord) : Prop :=
  c.level = Level.behavioral ∨ c.level = Level.verification ∨ c.level = Level.structuralCategorical

def HasTranslationRecord (_D : FATCD) (c : ClaimRecord) : Prop :=
  c.translationsRecorded = true

def HasVisibilityRecord (_D : FATCD) (c : ClaimRecord) : Prop :=
  c.visibilityRecorded = true ∧ c.instrument.isSome

def HasEmpiricalBridgeRecord (_D : FATCD) (c : ClaimRecord) : Prop :=
  c.empiricalBridgeRecorded = true ∧ c.instrument.isSome

structure NonclaimRecord where
  noGlobalIndependence : Bool
  noEmpiricalRealization : Bool
  noUniqueLift : Bool

def NoGlobalIndependenceClaim (n : NonclaimRecord) : Prop :=
  n.noGlobalIndependence = true

def NoEmpiricalRealizationClaim (n : NonclaimRecord) : Prop :=
  n.noEmpiricalRealization = true

def NoUniqueLiftClaim (n : NonclaimRecord) : Prop :=
  n.noUniqueLift = true

def standardClaimRecord : ClaimRecord :=
  { claimId := 1
    level := Level.verification
    claimRecorded := true
    promotionsRecorded := true
    translationsRecorded := true
    selectedLiftsRecorded := true
    forgettingLossesRecorded := true
    visibilityRecorded := true
    empiricalBridgeRecorded := true
    instrument := some 1 }

def standardNonclaims : NonclaimRecord :=
  { noGlobalIndependence := true
    noEmpiricalRealization := true
    noUniqueLift := true }

theorem honest_bookkeeping_admissibility :
    ∀ c : ClaimRecord, HonestBookkeeping c -> AdmissibleClaim c := by
  intro c h
  exact h

theorem typed_non_collapse :
    ∀ {r s : Role}, r ≠ s -> ForbiddenCollapse r s := by
  intro r s h
  exact h

theorem level_profile :
    ∀ (D : FATCD) (c : ClaimRecord), AdmissibleClaim c -> HasLevelProfile D c := by
  intro D c h
  cases c with
  | mk claimId level claimRecorded promotionsRecorded translationsRecorded selectedLiftsRecorded forgettingLossesRecorded visibilityRecorded empiricalBridgeRecorded instrument =>
    cases level <;> simp [HasLevelProfile]

theorem forgetting_lifts :
    ∀ r : Role, (selectedLiftAtlas.lift r).selected = true ∧
      (selectedLiftAtlas.lift r).nonUnique = true := by
  intro r
  exact ⟨selectedLiftAtlas.selected r, selectedLiftAtlas.nonUnique r⟩

theorem activation_thresholds :
    ∀ (D : FATCD) (r : Role) (p : DerivedRoleProjection D r),
      p.attachment.threshold.kind = AnnotationKind.threshold ∧
      HasAnnotationKind D.desc AnnotationKind.audit := by
  intro D r p
  exact ⟨p.attachment.thresholdIsDeclared, p.attachment.auditRecorded⟩

theorem visibility :
    ∀ (D : FATCD), AdmissibleClaim standardClaimRecord ->
      HasVisibilityRecord D standardClaimRecord := by
  intro D h
  exact ⟨rfl, rfl⟩

theorem empirical_bridge :
    ∀ (D : FATCD), AdmissibleClaim standardClaimRecord ->
      HasEmpiricalBridgeRecord D standardClaimRecord ∧
      NoEmpiricalRealizationClaim standardNonclaims := by
  intro D h
  exact ⟨⟨rfl, rfl⟩, rfl⟩

theorem nonclaim_closure :
    NoGlobalIndependenceClaim standardNonclaims ∧
    NoEmpiricalRealizationClaim standardNonclaims ∧
    NoUniqueLiftClaim standardNonclaims := by
  exact ⟨rfl, rfl, rfl⟩

end SixBirds
