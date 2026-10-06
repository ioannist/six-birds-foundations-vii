import SixBirds.IntegratedStress

namespace SixBirds

def ScopedExactSixQuestion : Prop :=
  ∀ D : FATCD, ∃ dec : DecompositionRecord D,
    WellFormedDecomposition dec ∧
    SixChannels dec ∧
    (∀ r : RawRecord, CoveredResidualClass (dec.classify r))

theorem scoped_exact_six : ScopedExactSixQuestion := by
  intro D
  obtain ⟨dec, hdec⟩ := decomposition_existence D
  have hexact := six_channel_exactness D dec hdec
  exact ⟨dec, hdec, hexact.left, hexact.right⟩

end SixBirds
