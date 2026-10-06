import SixBirdsIII.FiniteMaps
import SixBirdsIII.CompletionExamples
import SixBirdsIII.Defects

namespace SixBirdsIII

inductive SquareKind where
  | descent
  | completion
  | factorization
deriving DecidableEq, Repr

def DescentSquareExact {X Y : Type}
    (q : X -> Y) (F : X -> X) (Fs : ImageOf q -> ImageOf q) : Prop :=
  forall x : X, Fs (qImage q x) = qImage q (F x)

theorem descent_square_recovery {X Y : Type}
    (q : X -> Y) (F : X -> X) :
    (exists Fs : ImageOf q -> ImageOf q, DescentSquareExact q F Fs) <->
      DescendsToImage q F := by
  constructor
  · rintro ⟨Fs, hFs⟩
    exact ⟨Fs, hFs⟩
  · rintro ⟨Fs, hFs⟩
    exact ⟨Fs, hFs⟩

def CompletionSquareExact {C : Type} (E1 E2 : C -> C) : Prop :=
  CompletionsCommute E1 E2

def CompletionSquareObstructed {C : Type} (E1 E2 : C -> C) : Prop :=
  CompletionPastingDefect E1 E2

theorem completion_pasting_recovery {C : Type} (E1 E2 : C -> C) :
    CompletionSquareExact E1 E2 <->
      ¬ CompletionSquareObstructed E1 E2 := by
  unfold CompletionSquareExact CompletionSquareObstructed
  constructor
  · intro hcomm hdefect
    exact (completion_pasting_defect E1 E2).mp hdefect hcomm
  · intro hno c
    exact Classical.byContradiction (fun hneq => hno ⟨c, hneq⟩)

def HasExactFiller {S O0 O1 : Type} (pi0 : S -> O0) (pi1 : S -> O1) : Prop :=
  FactorsThroughImage pi0 pi1

def NoExactFiller {S O0 O1 : Type} (pi0 : S -> O0) (pi1 : S -> O1) : Prop :=
  ¬ HasExactFiller pi0 pi1

theorem strict_extension_as_no_filler {S O0 O1 : Type}
    (pi0 : S -> O0) (pi1 : S -> O1) :
    NoExactFiller pi0 pi1 <->
      HasFactorizationDefect pi0 pi1 := by
  unfold NoExactFiller HasExactFiller
  constructor
  · intro hno
    exact (factorization_defect_equivalence pi0 pi1).mpr hno
  · intro hdefect
    exact (factorization_defect_equivalence pi0 pi1).mp hdefect

end SixBirdsIII
