import ClosureLadder.Basic

namespace ClosureOp

universe u

variable {α : Type u}

def incl (c : ClosureOp α) : Closed c → α :=
  fun x => x.1

def reflect (c : ClosureOp α) : α → Closed c :=
  fun x => ⟨c x, c.idempotent x⟩

theorem incl_reflect_eq (c : ClosureOp α) (x : α) :
    incl c (reflect c x) = c x :=
  rfl

theorem reflect_incl_eq (c : ClosureOp α) (y : Closed c) :
    reflect c (incl c y) = y := by
  apply Subtype.ext
  exact y.property

end ClosureOp
