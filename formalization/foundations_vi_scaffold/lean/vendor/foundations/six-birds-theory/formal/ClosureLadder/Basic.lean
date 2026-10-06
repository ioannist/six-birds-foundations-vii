/-!
Repo-local Foundations I ClosureLadder core.

This vendored copy is adapted for the SAU repository's Lean v4.28.0,
self-contained build. The original Foundations I Lean track used mathlib's
`ClosureOperator`; here `ClosureOp` is the paper-facing idempotent closure
interface needed by SAU and by the local dependency audit.
-/

universe u

structure ClosureOp (α : Type u) where
  toFun : α → α
  idempotent : ∀ x : α, toFun (toFun x) = toFun x

instance {α : Type u} : CoeFun (ClosureOp α) (fun _ => α → α) where
  coe c := c.toFun

namespace ClosureOp

def Iterate {α : Type u} (f : α → α) : Nat → α → α
  | 0 => fun x => x
  | n + 1 => fun x => Iterate f n (f x)

def IsClosed {α : Type u} (c : ClosureOp α) (x : α) : Prop :=
  c x = x

def Closed {α : Type u} (c : ClosureOp α) : Type u :=
  {x : α // IsClosed c x}

def le {α : Type u} (c d : ClosureOp α) : Prop :=
  ∀ x, IsClosed d x → IsClosed c x

theorem isClosed_iff {α : Type u} {c : ClosureOp α} {x : α} :
    IsClosed c x ↔ c x = x :=
  Iff.rfl

theorem isClosed_of_le {α : Type u} {c d : ClosureOp α} (hcd : le c d) {x : α} :
    IsClosed d x → IsClosed c x := by
  exact hcd x

theorem closure_isClosed {α : Type u} (c : ClosureOp α) (x : α) :
    IsClosed c (c x) :=
  c.idempotent x

theorem closure_idempotent {α : Type u} (c : ClosureOp α) (x : α) :
    c (c x) = c x :=
  c.idempotent x

theorem closure_iterate_succ {α : Type u} (c : ClosureOp α) (n : Nat) (x : α) :
    Iterate c (n + 1) x = c x := by
  induction n generalizing x with
  | zero =>
      rfl
  | succ n ih =>
      calc
        Iterate c (n + 2) x = Iterate c (n + 1) (c x) := by
          rfl
        _ = c (c x) := by
          exact ih (c x)
        _ = c x := c.idempotent x

theorem closure_iterate_ge_one {α : Type u} (c : ClosureOp α) {n : Nat}
    (h : 1 ≤ n) (x : α) :
    Iterate c n x = c x := by
  cases n with
  | zero =>
      cases h
  | succ n =>
      exact closure_iterate_succ c n x

end ClosureOp

theorem closure_isClosed {α : Type u} (c : ClosureOp α) (x : α) :
    ClosureOp.IsClosed c (c x) :=
  ClosureOp.closure_isClosed c x

theorem closure_idempotent {α : Type u} (c : ClosureOp α) (x : α) :
    c (c x) = c x :=
  ClosureOp.closure_idempotent c x

theorem closure_iterate_succ {α : Type u} (c : ClosureOp α) (n : Nat) (x : α) :
    ClosureOp.Iterate c (n + 1) x = c x :=
  ClosureOp.closure_iterate_succ c n x

theorem closure_iterate_ge_one {α : Type u} (c : ClosureOp α) {n : Nat}
    (h : 1 ≤ n) (x : α) :
    ClosureOp.Iterate c n x = c x :=
  ClosureOp.closure_iterate_ge_one c h x

def StrictlyStronger {α : Type u} (c d : ClosureOp α) : Prop :=
  ClosureOp.le c d ∧ ¬ ClosureOp.le d c

structure ClosureLadder (α : Type u) where
  c : Nat → ClosureOp α
  step_strict : ∀ n, StrictlyStronger (c n) (c (n + 1))

theorem ladder_mono {α : Type u} (L : ClosureLadder α) (n : Nat) :
    ClosureOp.le (L.c n) (L.c (n + 1)) :=
  (L.step_strict n).1

theorem closed_sets_antitone_in_ladder {α : Type u}
    (L : ClosureLadder α) (n : Nat) {x : α} :
    ClosureOp.IsClosed (L.c (n + 1)) x → ClosureOp.IsClosed (L.c n) x := by
  intro hx
  exact ClosureOp.isClosed_of_le (ladder_mono L n) hx
