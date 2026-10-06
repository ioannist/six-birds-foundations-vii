namespace SixBirdsFoundationsV

/-!
D1 repair join.

Quotients are represented in the local house style by maps out of a
common carrier. Their semantic content is the induced fiber relation.
The operation called `vee`/join in THEOREMS.md is formalized here by the
raw product map; this has the same fibers as the image-restricted version
from the statement note and avoids extra representative machinery.
-/

def Refines {X : Type u} {A : Type v} {B : Type w} (q : X -> A) (r : X -> B) : Prop :=
  ∀ x x' : X, q x = q x' -> r x = r x'

def FiberEquiv {X : Type u} {A : Type v} {B : Type w} (q : X -> A) (r : X -> B) : Prop :=
  ∀ x x' : X, q x = q x' ↔ r x = r x'

def repairJoin {X : Type u} {A : Type v} {B : Type w} (q : X -> A) (r : X -> B) :
    X -> A × B :=
  fun x => (q x, r x)

theorem join_refines_left {X : Type u} {A : Type v} {B : Type w}
    (q : X -> A) (r : X -> B) :
    Refines (repairJoin q r) q := by
  intro x x' h
  exact congrArg Prod.fst h

theorem join_refines_right {X : Type u} {A : Type v} {B : Type w}
    (q : X -> A) (r : X -> B) :
    Refines (repairJoin q r) r := by
  intro x x' h
  exact congrArg Prod.snd h

theorem vee_greatest_lower_bound {X : Type u} {A : Type v} {B : Type w} {C : Type z}
    (s : X -> C) (q : X -> A) (r : X -> B)
    (hsq : Refines s q) (hsr : Refines s r) :
    Refines s (repairJoin q r) := by
  intro x x' h
  exact Prod.ext (hsq x x' h) (hsr x x' h)

theorem join_well_defined {X : Type u} {A : Type v} {A' : Type v'} {B : Type w}
    {B' : Type w'} (q : X -> A) (q' : X -> A') (r : X -> B) (r' : X -> B')
    (hq : FiberEquiv q q') (hr : FiberEquiv r r') :
    FiberEquiv (repairJoin q r) (repairJoin q' r') := by
  intro x x'
  constructor
  · intro h
    exact Prod.ext
      ((hq x x').mp (congrArg Prod.fst h))
      ((hr x x').mp (congrArg Prod.snd h))
  · intro h
    exact Prod.ext
      ((hq x x').mpr (congrArg Prod.fst h))
      ((hr x x').mpr (congrArg Prod.snd h))

theorem join_idem {X : Type u} {A : Type v} (q : X -> A) :
    FiberEquiv (repairJoin q q) q := by
  intro x x'
  constructor
  · intro h
    exact congrArg Prod.fst h
  · intro h
    exact Prod.ext h h

theorem join_comm {X : Type u} {A : Type v} {B : Type w} (q : X -> A) (r : X -> B) :
    FiberEquiv (repairJoin q r) (repairJoin r q) := by
  intro x x'
  constructor
  · intro h
    exact Prod.ext (congrArg Prod.snd h) (congrArg Prod.fst h)
  · intro h
    exact Prod.ext (congrArg Prod.snd h) (congrArg Prod.fst h)

theorem join_assoc {X : Type u} {A : Type v} {B : Type w} {C : Type z}
    (q : X -> A) (r : X -> B) (s : X -> C) :
    FiberEquiv (repairJoin (repairJoin q r) s) (repairJoin q (repairJoin r s)) := by
  intro x x'
  constructor
  · intro h
    have hqr : (q x, r x) = (q x', r x') := congrArg Prod.fst h
    have hs : s x = s x' := congrArg Prod.snd h
    have hq : q x = q x' := congrArg (fun p : A × B => p.1) hqr
    have hr : r x = r x' := congrArg (fun p : A × B => p.2) hqr
    exact Prod.ext hq (Prod.ext hr hs)
  · intro h
    have hq : q x = q x' := congrArg Prod.fst h
    have hrs : (r x, s x) = (r x', s x') := congrArg Prod.snd h
    have hr : r x = r x' := congrArg (fun p : B × C => p.1) hrs
    have hs : s x = s x' := congrArg (fun p : B × C => p.2) hrs
    exact Prod.ext (Prod.ext hq hr) hs

end SixBirdsFoundationsV
