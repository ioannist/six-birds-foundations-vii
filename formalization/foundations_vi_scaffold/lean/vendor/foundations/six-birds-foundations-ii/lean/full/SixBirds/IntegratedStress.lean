import SixBirds.Decomposition

namespace SixBirds

def DependencyCoherent : Prop :=
  (∀ role : Role, ∃ w : CommonWitnessData role, Nonempty (DerivedRoleProjection w.D role)) ∧
  (∀ D : FATCD, ∃ dec : DecompositionRecord D, WellFormedDecomposition dec)

def CircularityBlocked : Prop :=
  ∀ D : FATCD, FiniteDescription D.desc ∧ ClosedDescription D.desc ∧ AuditedDescription D.desc

def ChannelActivationSeparated : Prop :=
  ChannelStatus.belowThreshold ≠ ChannelStatus.activeProjection ∧
  ChannelStatus.collapsedBoundaryCase ≠ ChannelStatus.activeProjection ∧
  ChannelStatus.absentWithRecord ≠ ChannelStatus.activeProjection ∧
  ChannelStatus.inapplicableOutsideScope ≠ ChannelStatus.activeProjection

def RoleAlignmentBlocked : Prop :=
  ¬ GenericTransitionProjectsToP3 ∧ ¬ GenericPathProjectsToP5 ∧ ¬ GenericSemanticsProjectsToP1

def ResidualThreatsClosed : Prop :=
  ∀ (_D : FATCD) (r : RawRecord),
    classifyResidual r ≠ ResidualClass.unresolvedThreat ∧
    classifyResidual r ≠ ResidualClass.genuineSeventhRole

def OverclaimsBlocked : Prop :=
  NoGlobalIndependenceClaim standardNonclaims ∧
  NoEmpiricalRealizationClaim standardNonclaims ∧
  NoUniqueLiftClaim standardNonclaims ∧
  ∃ (D : FATCD) (dec₁ dec₂ : DecompositionRecord D), dec₁.status Role.P1 ≠ dec₂.status Role.P1

theorem dependency_stress : DependencyCoherent := by
  exact ⟨six_role_lower_bounds, decomposition_existence⟩

theorem circularity_stress : CircularityBlocked := by
  exact non_circularity

theorem channel_activation_stress : ChannelActivationSeparated := by
  exact inactive_statuses_are_not_active

theorem role_alignment_stress : RoleAlignmentBlocked := by
  exact ⟨generic_transition_not_p3, generic_path_not_p5, generic_semantics_not_p1⟩

theorem residual_stress : ResidualThreatsClosed := by
  exact unresolved_and_genuine_seventh_empty

theorem overclaim_stress : OverclaimsBlocked := by
  exact ⟨nonclaim_closure.left, nonclaim_closure.right.left, nonclaim_closure.right.right,
    non_uniqueness⟩

theorem integrated_stress :
    DependencyCoherent ∧ CircularityBlocked ∧ ChannelActivationSeparated ∧
      RoleAlignmentBlocked ∧ ResidualThreatsClosed ∧ OverclaimsBlocked := by
  exact ⟨dependency_stress, circularity_stress, channel_activation_stress,
    role_alignment_stress, residual_stress, overclaim_stress⟩

end SixBirds
