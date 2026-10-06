import SixBirdsIII.FiniteMaps
import SixBirdsIII.Strictness

namespace SixBirdsIII

def HasDescentDefect {X Y : Type} (q : X -> Y) (F : X -> X) : Prop :=
  exists x x' : X, q x = q x' /\ q (F x) ≠ q (F x')

theorem descent_defect_empty_iff_descends {X Y : Type} (q : X -> Y) (F : X -> X) :
    (¬ HasDescentDefect q F) <-> DescendsToImage q F := by
  rw [descent_through_quotient q F]
  constructor
  · intro hno x x' hx
    exact Classical.byContradiction (fun hneq => hno ⟨x, x', hx, hneq⟩)
  · intro hconst hdefect
    rcases hdefect with ⟨x, x', hx, hneq⟩
    exact hneq (hconst x x' hx)

theorem descent_defect_equivalence {X Y : Type} (q : X -> Y) (F : X -> X) :
    HasDescentDefect q F <-> ¬ DescendsToImage q F := by
  constructor
  · intro hdefect hdesc
    exact ((descent_defect_empty_iff_descends q F).mpr hdesc) hdefect
  · intro hnot
    exact Classical.byContradiction (fun hno =>
      hnot ((descent_defect_empty_iff_descends q F).mp hno))

def HasFactorizationDefect {S O0 O1 : Type} (pi0 : S -> O0) (pi1 : S -> O1) : Prop :=
  exists s s' : S, pi0 s = pi0 s' /\ pi1 s ≠ pi1 s'

theorem factorization_defect_equivalence {S O0 O1 : Type}
    (pi0 : S -> O0) (pi1 : S -> O1) :
    HasFactorizationDefect pi0 pi1 <-> ¬ FactorsThroughImage pi0 pi1 := by
  constructor
  · intro hdefect
    rcases hdefect with ⟨s, s', hs, hpi⟩
    exact (strict_extension_nonfactorization pi0 pi1).mpr ⟨s, s', hs, hpi⟩
  · intro hnot
    rcases (strict_extension_nonfactorization pi0 pi1).mp hnot with ⟨s, s', hs, hpi⟩
    exact ⟨s, s', hs, hpi⟩

end SixBirdsIII
