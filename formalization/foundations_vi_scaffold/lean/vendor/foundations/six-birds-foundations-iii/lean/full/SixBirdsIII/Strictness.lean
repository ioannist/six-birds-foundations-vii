import SixBirdsIII.FiniteMaps

namespace SixBirdsIII

def FactorsThroughImage {S O0 O1 : Type} (pi0 : S -> O0) (pi1 : S -> O1) : Prop :=
  ∃ phi : ImageOf pi0 -> O1, ∀ s : S, phi (qImage pi0 s) = pi1 s

def HasFiberMismatch {S O0 O1 : Type} (pi0 : S -> O0) (pi1 : S -> O1) : Prop :=
  ∃ s s' : S, pi0 s = pi0 s' ∧ pi1 s ≠ pi1 s'

theorem strict_extension_nonfactorization {S O0 O1 : Type}
    (pi0 : S -> O0) (pi1 : S -> O1) :
    (¬ FactorsThroughImage pi0 pi1) ↔ HasFiberMismatch pi0 pi1 := by
  constructor
  · intro hnot
    exact Classical.byContradiction (fun hno => by
      apply hnot
      refine ⟨fun y => pi1 (Classical.choose y.property), ?_⟩
      intro s
      have hrep : pi0 (Classical.choose (qImage pi0 s).property) = pi0 s :=
        Classical.choose_spec (qImage pi0 s).property
      by_cases heq : pi1 (Classical.choose (qImage pi0 s).property) = pi1 s
      · exact heq
      · exact False.elim (hno ⟨Classical.choose (qImage pi0 s).property, s, hrep, heq⟩))
  · rintro ⟨s, s', hpi0, hpi1⟩ hfac
    rcases hfac with ⟨phi, hphi⟩
    apply hpi1
    calc
      pi1 s = phi (qImage pi0 s) := (hphi s).symm
      _ = phi (qImage pi0 s') := by
        have himage : qImage pi0 s = qImage pi0 s' := by
          apply Subtype.ext
          exact hpi0
        rw [himage]
      _ = pi1 s' := hphi s'

end SixBirdsIII
