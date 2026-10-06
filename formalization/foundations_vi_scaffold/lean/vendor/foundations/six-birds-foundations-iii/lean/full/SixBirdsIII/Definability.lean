import SixBirdsIII.FiniteMaps

namespace SixBirdsIII

def DefinableBy {X Y : Type} (f : X -> Y) (p : X -> Prop) : Prop :=
  exists B : ImageOf f -> Prop, forall x : X, p x <-> B (qImage f x)

def PreimagePredicate {X Y : Type} (f : X -> Y) (B : ImageOf f -> Prop) : X -> Prop :=
  fun x => B (qImage f x)

def fixedInterfaceEncode {X Y : Type} (f : X -> Y) :
    (ImageOf f -> Prop) -> { p : X -> Prop // DefinableBy f p } :=
  fun B => ⟨PreimagePredicate f B, ⟨B, fun _ => Iff.rfl⟩⟩

theorem fixedInterfaceEncode_injective {X Y : Type} (f : X -> Y) :
    Function.Injective (fixedInterfaceEncode f) := by
  intro B B' h
  funext y
  rcases y.property with ⟨x, hx⟩
  have hval : PreimagePredicate f B = PreimagePredicate f B' :=
    congrArg Subtype.val h
  have hxval : B (qImage f x) = B' (qImage f x) :=
    congrFun hval x
  have hy : qImage f x = y := by
    apply Subtype.ext
    exact hx
  calc
    B y = B (qImage f x) := by rw [hy]
    _ = B' (qImage f x) := hxval
    _ = B' y := by rw [hy]

theorem fixedInterfaceEncode_surjective {X Y : Type} (f : X -> Y) :
    Function.Surjective (fixedInterfaceEncode f) := by
  intro p
  rcases p with ⟨p, hp⟩
  rcases hp with ⟨B, hB⟩
  refine ⟨B, ?_⟩
  apply Subtype.ext
  funext x
  exact propext (hB x).symm

theorem fixed_interface_definability_bound {X Y : Type} (f : X -> Y) :
    exists encode : (ImageOf f -> Prop) -> { p : X -> Prop // DefinableBy f p },
      Function.Injective encode /\ Function.Surjective encode := by
  exact ⟨fixedInterfaceEncode f,
    fixedInterfaceEncode_injective f,
    fixedInterfaceEncode_surjective f⟩

end SixBirdsIII
