import ClosureLadder.Basic

namespace ClosureLadder

universe u

/-- An idempotent endomorphism on a type. -/
structure IdempotentEndo (α : Type u) where
  f : α → α
  idem : ∀ x, f (f x) = f x

namespace IdempotentEndo

variable {α : Type u} (e : IdempotentEndo α)

/-- Fixed points of an endomap. -/
def FixedPoints : Type u := {x : α // e.f x = x}

def incl : e.FixedPoints → α := Subtype.val

/-- Retract onto fixed points: x maps to f x. -/
def retract (x : α) : e.FixedPoints := ⟨e.f x, by simp [e.idem]⟩

@[simp] theorem incl_retract (x : α) : e.incl (e.retract x) = e.f x := rfl

@[simp] theorem retract_incl (y : e.FixedPoints) : e.retract (e.incl y) = y := by
  apply Subtype.ext
  simp [IdempotentEndo.retract, IdempotentEndo.incl, y.property]

end IdempotentEndo

/-- Any local closure operator forgets to an idempotent endomap. -/
def ClosureOp.toIdempotentEndo {α : Type u} (c : ClosureOp α) : IdempotentEndo α :=
  ⟨c, by intro x; exact c.idempotent x⟩

end ClosureLadder
