import SixBirds.ScopedExactSix

namespace SixBirds

def malformedFiniteDescription : Description :=
  { raw := [badRawRecord]
    annotations := [ann AnnotationKind.audit 99, ann AnnotationKind.claim 99, ann AnnotationKind.nonclaim 99] }

theorem malformed_finite_rejected :
    ¬ FiniteDescription malformedFiniteDescription := by
  intro h
  have hf := h.left badRawRecord (by simp [malformedFiniteDescription])
  simp [badRawRecord] at hf

def malformedClosedDescription : Description :=
  { raw := [rawRecord 1 RawKind.object]
    annotations := [ann AnnotationKind.audit 99, ann AnnotationKind.claim 99, ann AnnotationKind.nonclaim 99] }

theorem malformed_closure_rejected :
    ¬ ClosedDescription malformedClosedDescription := by
  intro h
  have hc := (h.right (ann AnnotationKind.audit 99) (by simp [malformedClosedDescription])).left
  simp [malformedClosedDescription, HasRawId, RawIds, ann, rawRecord] at hc

def malformedAuditDescription : Description :=
  { raw := [rawRecord 1 RawKind.object]
    annotations := [ann AnnotationKind.audit 1, ann AnnotationKind.claim 1] }

theorem malformed_audit_rejected :
    ¬ AuditedDescription malformedAuditDescription := by
  intro h
  rcases h.right.right with ⟨a, ha, hk⟩
  simp [malformedAuditDescription, ann] at ha
  rcases ha with ha | ha <;> subst a <;> cases hk

theorem p1_witness_semantic :
    Nonempty (DerivedRoleProjection (witnessDescription Role.P1) Role.P1) := by
  exact ⟨roleProjection Role.P1⟩

theorem p2_witness_semantic :
    Nonempty (DerivedRoleProjection (witnessDescription Role.P2) Role.P2) := by
  exact ⟨roleProjection Role.P2⟩

theorem p3_witness_semantic :
    Nonempty (DerivedRoleProjection (witnessDescription Role.P3) Role.P3) := by
  exact ⟨roleProjection Role.P3⟩

theorem p4_witness_semantic :
    Nonempty (DerivedRoleProjection (witnessDescription Role.P4) Role.P4) := by
  exact ⟨roleProjection Role.P4⟩

theorem p5_witness_semantic :
    Nonempty (DerivedRoleProjection (witnessDescription Role.P5) Role.P5) := by
  exact ⟨roleProjection Role.P5⟩

theorem p6_witness_semantic :
    Nonempty (DerivedRoleProjection (witnessDescription Role.P6) Role.P6) := by
  exact ⟨roleProjection Role.P6⟩

theorem generic_transition_not_p3_semantic : ¬ GenericTransitionProjectsToP3 :=
  generic_transition_not_p3

theorem generic_path_not_p5_semantic : ¬ GenericPathProjectsToP5 :=
  generic_path_not_p5

theorem generic_semantics_not_p1_semantic : ¬ GenericSemanticsProjectsToP1 :=
  generic_semantics_not_p1

theorem unresolved_not_covered :
    ¬ CoveredResidualClass ResidualClass.unresolvedThreat := by
  intro h
  exact h

theorem genuine_seventh_not_covered :
    ¬ CoveredResidualClass ResidualClass.genuineSeventhRole := by
  intro h
  exact h

theorem probability_not_default_outside :
    classifyResidual (rawRecord 0 RawKind.probability) ≠ ResidualClass.outsideDomainStructure := by
  intro h
  cases h

theorem inactive_statuses_semantic :
    ChannelStatus.belowThreshold ≠ ChannelStatus.activeProjection ∧
    ChannelStatus.collapsedBoundaryCase ≠ ChannelStatus.activeProjection ∧
    ChannelStatus.absentWithRecord ≠ ChannelStatus.activeProjection ∧
    ChannelStatus.inapplicableOutsideScope ≠ ChannelStatus.activeProjection :=
  inactive_statuses_are_not_active

end SixBirds
