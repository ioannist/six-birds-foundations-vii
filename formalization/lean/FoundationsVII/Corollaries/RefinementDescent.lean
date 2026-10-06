import FoundationsVII.Join.Retention
import FoundationsVII.Dynamics.Transmission

/-!
# Parent refinement and descent fidelity
-/

namespace FoundationsVII

structure RefinedDescentPackage where
  refinement : ParentRefinementRecord
  fidelity : TransmissionFidelity

namespace RefinedDescentPackage

structure Certified (profile : RefinedDescentPackage) : Prop where
  refinementWellFormed : ParentRefinementRecord.WellFormed profile.refinement
  transmissionValid : TransmissionFidelity.Valid profile.fidelity

/-- A preserving refinement and a valid transmission jointly preserve
strictness, source, and budget, but only because both certificates are present. -/
theorem preserving_refinement_with_valid_descent_preserves_three_gates
    {profile : RefinedDescentPackage}
    (h : Certified profile)
    (hPreserves : profile.refinement.effect = RefinementEffect.preserves) :
    profile.refinement.strictnessPreserved = true ∧
      profile.fidelity.sourcePreserved = true ∧
      profile.fidelity.budgetPreserved = true := by
  have hRefinement := h.refinementWellFormed.2.2.2.1 hPreserves
  exact ⟨hRefinement.2,
    TransmissionFidelity.valid_preserves_source h.transmissionValid,
    TransmissionFidelity.valid_preserves_budget h.transmissionValid⟩

/-- A destroying refinement is an explicit obstruction to any unconditional
claim that refinement preserves the join. -/
theorem destroying_refinement_exhibits_a_failed_join_gate
    {profile : RefinedDescentPackage}
    (h : Certified profile)
    (hDestroys : profile.refinement.effect = RefinementEffect.destroys) :
    profile.refinement.compatibilityPreserved = false ∨
      profile.refinement.strictnessPreserved = false :=
  h.refinementWellFormed.2.2.2.2 hDestroys

/-- Descent fidelity does not repair a destroyed join gate by itself. -/
theorem valid_descent_does_not_erase_refinement_obstruction
    {profile : RefinedDescentPackage}
    (h : Certified profile)
    (hDestroys : profile.refinement.effect = RefinementEffect.destroys) :
    (profile.refinement.compatibilityPreserved = false ∨
      profile.refinement.strictnessPreserved = false) ∧
      profile.fidelity.squareCommutes = true := by
  exact ⟨destroying_refinement_exhibits_a_failed_join_gate h hDestroys,
    h.transmissionValid.2.2.2.2.2.2⟩

end RefinedDescentPackage

end FoundationsVII
