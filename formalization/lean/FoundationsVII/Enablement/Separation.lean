import FoundationsVII.Enablement.Birth
import FoundationsVII.Prior.FT13

/-!
# Enablement separations

Constructive witnesses show that enablement can be load-bearing without descent
factorization and can be necessary without being sufficient.
-/

namespace FoundationsVII

structure EnablementSeparation where
  enabled : Bool
  loadBearing : Bool
  descentFactorization : Bool
  necessary : Bool
  sufficient : Bool
  alternativeDeterminants : Bool
  causalChannel : Bool
  deriving Repr, DecidableEq, BEq

namespace EnablementSeparation

def EnablementWithoutDescent (profile : EnablementSeparation) : Prop :=
  profile.enabled = true ∧
  profile.loadBearing = true ∧
  profile.descentFactorization = false

instance (profile : EnablementSeparation) : Decidable (EnablementWithoutDescent profile) := by
  unfold EnablementWithoutDescent
  infer_instance

def NecessaryButInsufficient (profile : EnablementSeparation) : Prop :=
  profile.enabled = true ∧
  profile.necessary = true ∧
  profile.sufficient = false ∧
  profile.alternativeDeterminants = true

instance (profile : EnablementSeparation) : Decidable (NecessaryButInsufficient profile) := by
  unfold NecessaryButInsufficient
  infer_instance

end EnablementSeparation

private def withoutDescentWitness : EnablementSeparation :=
  { enabled := true, loadBearing := true, descentFactorization := false,
    necessary := true, sufficient := false, alternativeDeterminants := true,
    causalChannel := false }

private def necessaryInsufficientWitness : EnablementSeparation :=
  { enabled := true, loadBearing := false, descentFactorization := false,
    necessary := true, sufficient := false, alternativeDeterminants := true,
    causalChannel := false }

/-- C034 constructive separation theorem. -/
theorem constructive_enablement_without_descent :
    ∃ profile : EnablementSeparation,
      EnablementSeparation.EnablementWithoutDescent profile :=
  ⟨withoutDescentWitness, by decide⟩

/-- C034 constructive necessary-but-insufficient theorem. -/
theorem constructive_necessary_but_insufficient_enablement :
    ∃ profile : EnablementSeparation,
      EnablementSeparation.NecessaryButInsufficient profile :=
  ⟨necessaryInsufficientWitness, by decide⟩

theorem enablement_without_descent_need_not_be_causal :
    EnablementSeparation.EnablementWithoutDescent withoutDescentWitness ∧
    withoutDescentWitness.causalChannel = false := by decide

theorem necessary_enablement_does_not_imply_sufficiency :
    EnablementSeparation.NecessaryButInsufficient necessaryInsufficientWitness ∧
    necessaryInsufficientWitness.sufficient = false := by decide

end FoundationsVII
