/-!
G5 Carry-Horizon Confinement: abstract no-go and confinement schemas.

This file formalizes the two conditional theorem schemas from `THEOREMS.md`
for G5. It deliberately does not build base-specific digit strings,
reverse-and-add arithmetic, regular languages, or automata. Those are
calibration/lab content for the base-2 and base-10 instances.
-/

namespace SixBirdsFoundationsVI.Laws.G5CarryHorizonConfinement

/--
`FutureSufficient q Probe m` says that quotient depth `m` determines every
declared future probe value.

This is the abstract version of "the fixed-depth quotient `q_m` is
future-sufficient": whenever two states agree after applying `q m`, no
step-indexed probe can distinguish them.
-/
def FutureSufficient {X Q V : Type} (q : Nat → X → Q)
    (Probe : Nat → X → V) (m : Nat) : Prop :=
  ∀ (j : Nat) (y z : X), q m y = q m z → Probe j y = Probe j z

/--
`[H-G5-unbounded-horizon]`: every fixed quotient depth has a split-pair
obstruction at some future probe.

The existential witness is the Lean-level counterpart of the prose's
nonempty `Delta(q_m, R_b^j, r_j)`: two states agree under the current-depth
quotient but disagree under a future probe.
-/
def UnboundedHorizon {X Q V : Type} (q : Nat → X → Q)
    (Probe : Nat → X → V) : Prop :=
  ∀ m : Nat, ∃ (j : Nat) (y z : X),
    q m y = q m z ∧ Probe j y ≠ Probe j z

/--
G5 no-go schema, pointwise form: no fixed depth is future-sufficient.

The proof is the split-pair obstruction applied at the same depth `m`.
-/
theorem no_fixed_depth_future_sufficient {X Q V : Type}
    (q : Nat → X → Q) (Probe : Nat → X → V)
    (hunbounded : UnboundedHorizon q Probe) :
    ∀ m : Nat, ¬ FutureSufficient q Probe m := by
  intro m hsufficient
  rcases hunbounded m with ⟨j, y, z, hq, hneq⟩
  exact hneq (hsufficient j y z hq)

/--
G5 no-go schema, existential form: there is no future-sufficient fixed depth.
-/
theorem no_future_sufficient_depth {X Q V : Type}
    (q : Nat → X → Q) (Probe : Nat → X → V)
    (hunbounded : UnboundedHorizon q Probe) :
    ¬ ∃ m : Nat, FutureSufficient q Probe m := by
  intro hexists
  rcases hexists with ⟨m, hsufficient⟩
  exact no_fixed_depth_future_sufficient q Probe hunbounded m hsufficient

/--
`Iterate R n x` is the `n`-fold forward iteration of `R` at `x`.

G5 keeps this local rather than importing G10's similar helper, because each
G-law Lean file is intended to stand alone.
-/
def Iterate {X : Type} (R : X → X) : Nat → X → X
  | 0, x => x
  | n + 1, x => R (Iterate R n x)

/--
Iteration composes across addition on the right:
`R^(N+t)(x) = R^t(R^N(x))`.

This lemma is the small arithmetic bridge needed to state the confinement
theorem exactly in the prose's `R_b^{N+t}(x)` form while proving persistence
from the entry state `R_b^N(x)`.
-/
theorem iterate_add {X : Type} (R : X → X) :
    ∀ (N t : Nat) (x : X),
      Iterate R (N + t) x = Iterate R t (Iterate R N x) := by
  intro N t
  induction t with
  | zero =>
      intro x
      simp [Iterate]
  | succ t ih =>
      intro x
      simp [Iterate, ih x]

/--
`[H-G5-closed-pattern]` closure half: the declared pattern family is closed
under the transition.
-/
def ClosedUnderR {X : Type} (R : X → X) (Pcal : X → Prop) : Prop :=
  ∀ x : X, Pcal x → Pcal (R x)

/--
`[H-G5-closed-pattern]` target-free half: no state in the declared pattern
family satisfies the target predicate.
-/
def TargetFree {X : Type} (Target Pcal : X → Prop) : Prop :=
  ∀ x : X, Pcal x → ¬ Target x

/--
Bundled form of `[H-G5-closed-pattern]`.

The prose states closure and target exclusion together. Keeping the bundled
definition available makes the named hypothesis explicit, while the theorem
below also exposes the two components in its proof.
-/
def ClosedPattern {X : Type} (R : X → X) (Target Pcal : X → Prop) : Prop :=
  ClosedUnderR R Pcal ∧ TargetFree Target Pcal

/--
Closure propagates membership in the pattern family through all later iterates.
-/
theorem closed_pattern_persists {X : Type} (R : X → X) (Pcal : X → Prop)
    (hclosed : ClosedUnderR R Pcal) :
    ∀ (t : Nat) (x : X), Pcal x → Pcal (Iterate R t x) := by
  intro t
  induction t with
  | zero =>
      intro x hx
      exact hx
  | succ t ih =>
      intro x hx
      exact hclosed (Iterate R t x) (ih x hx)

/--
G5 confinement schema: once an orbit enters a closed target-free pattern at
time `N`, every later time `N+t` remains in the pattern and misses the target.

This is the abstract version of the regular-language confinement certificate:
closure gives `R_b^{N+t}(x) in Pcal`, and target-freeness gives
`not Target(R_b^{N+t}(x))`.
-/
theorem closed_pattern_confinement {X : Type} (R : X → X)
    (Target Pcal : X → Prop) (hpattern : ClosedPattern R Target Pcal)
    (x : X) (N : Nat) (hentry : Pcal (Iterate R N x)) :
    ∀ t : Nat,
      Pcal (Iterate R (N + t) x) ∧
        ¬ Target (Iterate R (N + t) x) := by
  intro t
  rcases hpattern with ⟨hclosed, hfree⟩
  have hpersist :
      Pcal (Iterate R t (Iterate R N x)) :=
    closed_pattern_persists R Pcal hclosed t (Iterate R N x) hentry
  have hrewrite :
      Iterate R (N + t) x = Iterate R t (Iterate R N x) :=
    iterate_add R N t x
  constructor
  · rw [hrewrite]
    exact hpersist
  · rw [hrewrite]
    exact hfree (Iterate R t (Iterate R N x)) hpersist

end SixBirdsFoundationsVI.Laws.G5CarryHorizonConfinement
