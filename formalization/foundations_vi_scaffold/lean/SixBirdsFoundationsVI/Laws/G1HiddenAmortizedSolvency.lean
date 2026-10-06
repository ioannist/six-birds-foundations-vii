/-!
G1 Hidden Amortized Solvency: abstract membrane reduction and discharge schema.

This file formalizes the layer-agnostic logical core from `THEOREMS.md` for
G1. It does not construct the Collatz accelerated map, affine ledgers,
`2`-adic completions, ghost-shadowing families, or cycle-integrality
conditions; those are calibration and instance content.
-/

namespace SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency

/--
`Iterate T n x` is the `n`-fold forward iteration of `T` at `x`.

G1 keeps this helper local, following the project convention that each G-law
Lean file stands alone.
-/
def Iterate {X : Type} (T : X → X) : Nat → X → X
  | 0, x => x
  | n + 1, x => T (Iterate T n x)

/--
The abstract descent predicate at horizon `k`.

The concrete G1 prose phrases this through a ledger inequality
`V_k(x) > 0 iff T^k(x) < x`. The abstract law only uses the right-hand
native-order side, so `lt` is left as an arbitrary relation.
-/
def Descends {X : Type} (T : X → X) (lt : X → X → Prop)
    (k : Nat) (x : X) : Prop :=
  lt (Iterate T k x) x

/--
The bad-tail membrane at finite depth `k`.

Membership says no positive descent certificate has appeared at any checked
horizon `1 <= j <= k`.
-/
def BadTailMembrane {X : Type} (T : X → X) (lt : X → X → Prop)
    (k : Nat) (x : X) : Prop :=
  ∀ j : Nat, 1 ≤ j → j ≤ k → ¬ Descends T lt j x

/--
Pointwise liveness: every nonterminal native point eventually has a finite
positive descent certificate.
-/
def PointwiseLiveness {X : Type} (T : X → X) (lt : X → X → Prop)
    (A : X → Prop) : Prop :=
  ∀ x : X, ¬ A x → ∃ k : Nat, 1 ≤ k ∧ Descends T lt k x

/--
Emptiness of the infinite bad-tail intersection.

For every nonterminal native point, some finite bad-tail membrane depth fails.
-/
def EmptyBadTailIntersection {X : Type} (T : X → X)
    (lt : X → X → Prop) (A : X → Prop) : Prop :=
  ∀ x : X, ¬ A x → ∃ k : Nat, ¬ BadTailMembrane T lt k x

/--
G1 Part (a): pointwise liveness is equivalent to emptiness of the infinite
bad-tail membrane intersection.

The forward direction applies the live horizon `k` against membership in
`N_k`. The reverse direction is the classical contraposition of the finite
membrane definition: if no liveness witness exists, then every proposed
membrane failure would itself give such a witness.
-/
theorem part_a_reduction {X : Type} (T : X → X) (lt : X → X → Prop)
    (A : X → Prop) :
    PointwiseLiveness T lt A ↔ EmptyBadTailIntersection T lt A := by
  constructor
  · intro hlive x hx
    rcases hlive x hx with ⟨k, hkpos, hdesc⟩
    exact ⟨k, by
      intro hbad
      exact hbad k hkpos (Nat.le_refl k) hdesc⟩
  · intro hempty x hx
    exact Classical.byContradiction (by
      intro hnotlive
      rcases hempty x hx with ⟨k, hnotbad⟩
      apply hnotbad
      intro j hjpos _hjk hdesc
      exact hnotlive ⟨j, hjpos, hdesc⟩)

/--
An infinite bad thread based at `x`: `x` is nonterminal and remains in every
finite bad-tail membrane depth.
-/
def InfiniteBadThread {X : Type} (T : X → X) (lt : X → X → Prop)
    (A : X → Prop) (x : X) : Prop :=
  ¬ A x ∧ ∀ k : Nat, BadTailMembrane T lt k x

/--
`[H-G1-ghost-convergence]`, reduced to the consequence used by the abstract
contradiction proof.

Every infinite bad thread is eventually inside every declared ghost-neighborhood
depth `U h` after embedding native iterates into the completion carrier.
-/
def GhostConvergence {X Xhat : Type} (T : X → X)
    (lt : X → X → Prop) (A : X → Prop) (emb : X → Xhat)
    (U : Nat → Xhat → Prop) : Prop :=
  ∀ x : X, InfiniteBadThread T lt A x →
    ∀ h : Nat, ∃ K : Nat,
      ∀ t : Nat, K ≤ t → U h (emb (Iterate T t x))

/--
`[H-G1-separation]`: every nonterminal native orbit has a certified tail that
stays outside one computable ghost-neighborhood depth.
-/
def NativeSeparation {X Xhat : Type} (T : X → X)
    (_lt : X → X → Prop) (A : X → Prop) (emb : X → Xhat)
    (U : Nat → Xhat → Prop) : Prop :=
  ∀ x : X, ¬ A x → ∃ (h K : Nat),
    ∀ t : Nat, K ≤ t → ¬ U h (emb (Iterate T t x))

/--
G1 Part (b): ghost convergence plus native separation discharge pointwise
liveness.

Assuming an infinite bad thread at a nonterminal `x`, separation supplies a
depth `h` and tail outside `U h`, while ghost convergence supplies a tail
inside that same `U h`. At `max Kout Kin`, both claims hold, contradiction.
Part (a) then converts bad-tail-intersection emptiness into pointwise liveness.
-/
theorem part_b_discharge {X Xhat : Type} (T : X → X)
    (lt : X → X → Prop) (A : X → Prop) (emb : X → Xhat)
    (U : Nat → Xhat → Prop)
    (hconv : GhostConvergence T lt A emb U)
    (hsep : NativeSeparation T lt A emb U) :
    PointwiseLiveness T lt A := by
  have hempty : EmptyBadTailIntersection T lt A := by
    intro x hx
    exact Classical.byContradiction (by
      intro hnoFailure
      have hbad : ∀ k : Nat, BadTailMembrane T lt k x := by
        intro k
        exact Classical.byContradiction (by
          intro hnotbad
          exact hnoFailure ⟨k, hnotbad⟩)
      have hthread : InfiniteBadThread T lt A x := ⟨hx, hbad⟩
      rcases hsep x hx with ⟨h, Kout, hout⟩
      rcases hconv x hthread h with ⟨Kin, hin⟩
      let t := Nat.max Kout Kin
      have hin_t : U h (emb (Iterate T t x)) :=
        hin t (Nat.le_max_right Kout Kin)
      have hout_t : ¬ U h (emb (Iterate T t x)) :=
        hout t (Nat.le_max_left Kout Kin)
      exact hout_t hin_t)
  exact (part_a_reduction T lt A).2 hempty

end SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency
