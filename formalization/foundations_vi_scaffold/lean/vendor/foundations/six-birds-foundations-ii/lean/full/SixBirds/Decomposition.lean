import SixBirds.UpperBound

namespace SixBirds

inductive ChannelStatus where
  | activeProjection
  | belowThreshold
  | collapsedBoundaryCase
  | absentWithRecord
  | inapplicableOutsideScope
  deriving DecidableEq, Repr

structure DecompositionRecord (D : FATCD) where
  status : Role -> ChannelStatus
  classify : RawRecord -> ResidualClass
  classifyCovered : ∀ r : RawRecord, CoveredResidualClass (classify r)
  activeSound : ∀ role : Role, status role = ChannelStatus.activeProjection -> RoleKindPresent D.desc role
  exactChannels : primitiveRoles.length = 6
  auditCarried : AuditedDescription D.desc
  nonclaimsCarried : Bool

def WellFormedDecomposition {D : FATCD} (dec : DecompositionRecord D) : Prop :=
  dec.exactChannels = primitiveRoles_length ∧
  dec.auditCarried = D.audited ∧
  dec.nonclaimsCarried = true ∧
  (∀ r : RawRecord, CoveredResidualClass (dec.classify r)) ∧
  (∀ role : Role, dec.status role = ChannelStatus.activeProjection -> RoleKindPresent D.desc role)

def defaultDecomposition (D : FATCD) : DecompositionRecord D :=
  { status := fun _ => ChannelStatus.absentWithRecord
    classify := classifyResidual
    classifyCovered := classifyResidual_covered
    activeSound := by
      intro role h
      cases h
    exactChannels := primitiveRoles_length
    auditCarried := D.audited
    nonclaimsCarried := true }

theorem defaultDecomposition_wellFormed (D : FATCD) :
    WellFormedDecomposition (defaultDecomposition D) := by
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · rfl
  constructor
  · exact classifyResidual_covered
  · intro role h
    cases h

theorem witness_role_kind_present :
    ∀ role : Role, RoleKindPresent (witnessDescription role).desc role := by
  intro role kind hkind
  rcases roleRaw_aligned role kind hkind with ⟨r, hr, hk⟩
  exact ⟨r, by simpa [witnessDescription, witnessDescriptionData] using hr, hk⟩

def activeDecomposition (role : Role) : DecompositionRecord (witnessDescription role) :=
  { status := fun r => if r = role then ChannelStatus.activeProjection else ChannelStatus.absentWithRecord
    classify := classifyResidual
    classifyCovered := classifyResidual_covered
    activeSound := by
      intro r h
      by_cases hr : r = role
      · subst r
        exact witness_role_kind_present role
      · simp [hr] at h
    exactChannels := primitiveRoles_length
    auditCarried := (witnessDescription role).audited
    nonclaimsCarried := true }

def SixChannels {D : FATCD} (dec : DecompositionRecord D) : Prop :=
  dec.exactChannels = primitiveRoles_length

def SixActiveProjections {D : FATCD} (dec : DecompositionRecord D) : Prop :=
  ∀ role : Role, dec.status role = ChannelStatus.activeProjection

theorem decomposition_existence :
    ∀ D : FATCD, ∃ dec : DecompositionRecord D, WellFormedDecomposition dec := by
  intro D
  exact ⟨defaultDecomposition D, defaultDecomposition_wellFormed D⟩

theorem six_channel_exactness :
    ∀ (D : FATCD) (dec : DecompositionRecord D),
      WellFormedDecomposition dec ->
        SixChannels dec ∧
        (∀ r : RawRecord, CoveredResidualClass (dec.classify r)) := by
  intro D dec h
  exact ⟨h.left, h.right.right.right.left⟩

theorem channel_vs_activation :
    ∀ (D : FATCD) (dec : DecompositionRecord D),
      SixChannels dec ->
      (SixActiveProjections dec -> SixChannels dec) := by
  intro D dec h channelsActive
  exact h

theorem inactive_statuses_are_not_active :
    ChannelStatus.belowThreshold ≠ ChannelStatus.activeProjection ∧
    ChannelStatus.collapsedBoundaryCase ≠ ChannelStatus.activeProjection ∧
    ChannelStatus.absentWithRecord ≠ ChannelStatus.activeProjection ∧
    ChannelStatus.inapplicableOutsideScope ≠ ChannelStatus.activeProjection := by
  constructor
  · intro h
    cases h
  constructor
  · intro h
    cases h
  constructor
  · intro h
    cases h
  · intro h
    cases h

theorem non_uniqueness :
    ∃ (D : FATCD) (dec₁ dec₂ : DecompositionRecord D),
      dec₁.status Role.P1 ≠ dec₂.status Role.P1 := by
  refine ⟨witnessDescription Role.P1, activeDecomposition Role.P1,
    defaultDecomposition (witnessDescription Role.P1), ?_⟩
  intro h
  simp [activeDecomposition, defaultDecomposition] at h

end SixBirds
