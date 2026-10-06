namespace SixBirdsIII

def ImageOf {X Y : Type} (q : X -> Y) : Type :=
  { y : Y // ∃ x : X, q x = y }

def qImage {X Y : Type} (q : X -> Y) (x : X) : ImageOf q :=
  ⟨q x, ⟨x, rfl⟩⟩

def DescendsToImage {X Y : Type} (q : X -> Y) (F : X -> X) : Prop :=
  ∃ Fs : ImageOf q -> ImageOf q, ∀ x : X, Fs (qImage q x) = qImage q (F x)

def FiberConst {X Y : Type} (q : X -> Y) (F : X -> X) : Prop :=
  ∀ x x' : X, q x = q x' -> q (F x) = q (F x')

theorem descent_through_quotient {X Y : Type} (q : X -> Y) (F : X -> X) :
    DescendsToImage q F ↔ FiberConst q F := by
  constructor
  · rintro ⟨Fs, hFs⟩ x x' hx
    have harg : qImage q x = qImage q x' := by
      apply Subtype.ext
      exact hx
    have himage : qImage q (F x) = qImage q (F x') := by
      calc
        qImage q (F x) = Fs (qImage q x) := (hFs x).symm
        _ = Fs (qImage q x') := by rw [harg]
        _ = qImage q (F x') := hFs x'
    exact congrArg Subtype.val himage
  · intro hconst
    refine ⟨fun y => qImage q (F (Classical.choose y.property)), ?_⟩
    intro x
    apply Subtype.ext
    dsimp [qImage]
    have hrep : q (Classical.choose (qImage q x).property) = q x :=
      Classical.choose_spec (qImage q x).property
    exact hconst (Classical.choose (qImage q x).property) x hrep

end SixBirdsIII
