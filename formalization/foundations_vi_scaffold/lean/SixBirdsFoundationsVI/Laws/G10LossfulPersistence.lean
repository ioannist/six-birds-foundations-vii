/-!
G10 Lossful Boundary Persistence: setup, induction theorem, and checksum
cascade witness.

This file formalizes the protection/regeneration induction from `THEOREMS.md`
for G10. It deliberately has no imports: the required iteration and injectivity
notions are hand-rolled in this namespace.
-/

namespace SixBirdsFoundationsVI.Laws.G10LossfulPersistence

/--
`Iterate f n x` is the `n`-fold forward iteration of `f` at `x`.

This hand-rolled definition is used both for the destructive state operator
`D : X -> X` and the boundary update `rho : B -> B`.
-/
def Iterate {X : Type} (f : X → X) : Nat → X → X
  | 0, x => x
  | n + 1, x => f (Iterate f n x)

/--
Function injectivity, stated locally to avoid importing any external API.
-/
def Injective {X Y : Type} (f : X → Y) : Prop :=
  ∀ {x y : X}, f x = f y → x = y

/--
A destructive operator is lossful when it is not injective.
-/
def Lossful {X : Type} (D : X → X) : Prop :=
  ¬ Injective D

/--
`[H-G10-protect]`: whenever the interior invariant holds, applying the
destructive operator updates the boundary exactly by `rho`.
-/
def Protect {X B : Type} (D : X → X) (b : X → B) (rho : B → B)
    (I : X → Prop) : Prop :=
  ∀ x : X, I x → b (D x) = rho (b x)

/--
`[H-G10-regen]`: whenever the interior invariant holds, applying the
destructive operator regenerates it.
-/
def Regen {X : Type} (D : X → X) (I : X → Prop) : Prop :=
  ∀ x : X, I x → I (D x)

/--
G10 theorem: protection plus regeneration preserves the interior invariant and
iterates the boundary readout by `rho`.

Lossfulness is part of G10's setup and is therefore carried in the theorem
signature, but this specific induction uses only `Protect`, `Regen`, and
`I x0`. No invertibility of `D` is assumed.
-/
theorem boundary_persistence {X B : Type} (D : X → X) (b : X → B)
    (rho : B → B) (I : X → Prop)
    (_hlossful : Lossful D)
    (hprotect : Protect D b rho I) (hregen : Regen D I)
    {x0 : X} (hI0 : I x0) :
    ∀ n : Nat,
      I (Iterate D n x0) ∧
        b (Iterate D n x0) = Iterate rho n (b x0) := by
  intro n
  induction n with
  | zero =>
      simp [Iterate, hI0]
  | succ n ih =>
      rcases ih with ⟨hIn, hb⟩
      constructor
      · exact hregen _ hIn
      · simp [Iterate]
        calc
          b (D (Iterate D n x0)) = rho (b (Iterate D n x0)) :=
            hprotect _ hIn
          _ = rho (Iterate rho n (b x0)) := by
            rw [hb]

/--
The checksum-cascade state space `({0,1}^2) x {0,1}`.
-/
abbrev ChecksumState := (Bool × Bool) × Bool

/--
The checksum-cascade boundary carrier.
-/
abbrev ChecksumBoundary := Bool

/--
The checksum-cascade destructive map:
`D(((a,b),c)) = ((c,0),c)`.
-/
def checksumD : ChecksumState → ChecksumState
  | ((_a, _b), c) => ((c, false), c)

/--
The checksum-cascade boundary readout `bdy((a,b),c)=c`.
-/
def checksumBoundary : ChecksumState → ChecksumBoundary
  | ((_a, _b), c) => c

/--
The checksum-cascade boundary update `rho(c)=c`.
-/
def checksumRho : ChecksumBoundary → ChecksumBoundary :=
  fun c => c

/--
The checksum-cascade interior invariant `c = a xor b`.
-/
def checksumInvariant : ChecksumState → Prop
  | ((a, b), c) => c = Bool.xor a b

/--
The checksum-cascade destructive map is lossful: the two distinct states
`((0,0),0)` and `((1,1),0)` collide.
-/
theorem checksum_lossful : Lossful checksumD := by
  intro hInjective
  have hcollision :
      checksumD ((false, false), false) =
        checksumD ((true, true), false) := rfl
  have heq := hInjective hcollision
  cases heq

/--
The checksum-cascade instance discharges `[H-G10-protect]`.
-/
theorem checksum_protect :
    Protect checksumD checksumBoundary checksumRho checksumInvariant := by
  intro x _hx
  cases x with
  | mk data c =>
      cases data with
      | mk a b =>
          simp [checksumD, checksumBoundary, checksumRho]

/--
The checksum-cascade instance discharges `[H-G10-regen]`.
-/
theorem checksum_regen : Regen checksumD checksumInvariant := by
  intro x _hx
  cases x with
  | mk data c =>
      cases data with
      | mk a b =>
          simp [checksumD, checksumInvariant]

/--
Concrete G10 positive witness: every checksum-cascade run starting from a state
satisfying `c = a xor b` preserves the invariant and keeps the boundary checksum
persistent under `rho = id`.
-/
theorem checksum_boundary_persistence {x0 : ChecksumState}
    (hI0 : checksumInvariant x0) :
    ∀ n : Nat,
      checksumInvariant (Iterate checksumD n x0) ∧
        checksumBoundary (Iterate checksumD n x0) =
          Iterate checksumRho n (checksumBoundary x0) :=
  boundary_persistence checksumD checksumBoundary checksumRho checksumInvariant
    checksum_lossful checksum_protect checksum_regen hI0

end SixBirdsFoundationsVI.Laws.G10LossfulPersistence
