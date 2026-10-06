/-!
G13 Thin-Orbit Saturation: abstract relative-density packaging.

This file formalizes only the elementary arithmetic consequence used by the
G13 theorem statement: a sublinear missed-target count, together with a
positive-density target count, makes the missed targets relatively negligible.
It does not construct thin groups, expansion, spectral gaps, Apollonian
packings, sieve arguments, or reciprocity obstructions; those are imported
instance content.
-/

namespace SixBirdsFoundationsVI.Laws.G13ThinOrbitSaturation

/--
Nat-arithmetic rendering of a sublinear count.

`EventuallySublinear f` says that for every positive integer scale `k`, the
tail of `f` satisfies `f N * k <= N`. This is the Mathlib-free consequence of
an imported exceptional-set estimate such as `O(N^(1-eta))`; the fractional
exponent itself is deliberately not represented here.
-/
def EventuallySublinear (f : Nat -> Nat) : Prop :=
  forall k : Nat, k > 0 -> exists N0 : Nat,
    forall N : Nat, N >= N0 -> f N * k <= N

/--
Nat-arithmetic rendering of positive lower density.

The constants `c,k` encode a positive rational lower bound `c/k`: every target
count satisfies `c * N <= g N * k`. This is intentionally stated without real
numbers or filters.
-/
def EventuallyPositiveDensity (g : Nat -> Nat) : Prop :=
  exists c k : Nat, c > 0 /\ k > 0 /\
    forall N : Nat, g N * k >= c * N

/--
Relative negligibility of `missed` inside `total`, again encoded without real
limits: for every positive scale `j`, eventually `missed N * j <= total N`.
-/
def EventuallyRelativelyNegligible
    (missed total : Nat -> Nat) : Prop :=
  forall j : Nat, j > 0 -> exists N0 : Nat,
    forall N : Nat, N >= N0 -> missed N * j <= total N

/--
G13 relative-density packaging theorem.

The imported saturation theorem supplies the sublinear missed-count surface;
the declared thick target supplies positive lower density. The conclusion is
that missed admissible targets have relative density zero in the same
Nat-arithmetic sense.
-/
theorem relative_density_theorem {missed total : Nat -> Nat}
    (hsub : EventuallySublinear missed)
    (hdense : EventuallyPositiveDensity total) :
    EventuallyRelativelyNegligible missed total := by
  intro j hj
  rcases hdense with ⟨c, k, hc, hk, hdense_all⟩
  have hkj : k * j > 0 := Nat.mul_pos hk hj
  rcases hsub (k * j) hkj with ⟨N0, hN0⟩
  refine ⟨N0, ?_⟩
  intro N hN
  have hsubN : missed N * (k * j) <= N := hN0 N hN
  have hsub_rearr : (missed N * j) * k <= N := by
    simpa [Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm] using hsubN
  have hN_le_cN : N <= c * N := by
    have hc1 : 1 <= c := hc
    calc
      N = 1 * N := by simp
      _ <= c * N := Nat.mul_le_mul_right N hc1
  have hN_le_total : N <= total N * k :=
    Nat.le_trans hN_le_cN (hdense_all N)
  have hscaled : (missed N * j) * k <= total N * k :=
    Nat.le_trans hsub_rearr hN_le_total
  exact Nat.le_of_mul_le_mul_right hscaled hk

/--
An infinite recorded reciprocity-obstructed family: arbitrarily far out, there
is another target satisfying `recip`.
-/
def InfiniteFamily (recip : Nat -> Prop) : Prop :=
  forall N : Nat, exists M : Nat, M > N /\ recip M

/--
Bookkeeping predicate for the compatibility observation in G13: an infinite
reciprocity record and a sublinear count record may be stored together. The
counting relation between `recip` and `recip_count` is instance data, not part
of this abstract packaging layer.
-/
def ReciprocityCompatible
    (recip : Nat -> Prop) (recip_count : Nat -> Nat) : Prop :=
  InfiniteFamily recip /\ EventuallySublinear recip_count

/--
G13 reciprocity-compatibility observation.

The law's density-one conclusion is not contradicted merely by also recording
an infinite reciprocity family. What must be checked by the instance is that
the family's count is negligible; at this abstract level, the two supplied
records are packaged together without deriving a contradiction.
-/
theorem reciprocity_compatibility_observation
    {recip : Nat -> Prop} {recip_count : Nat -> Nat}
    (hinf : InfiniteFamily recip)
    (hsub : EventuallySublinear recip_count) :
    ReciprocityCompatible recip recip_count := by
  exact ⟨hinf, hsub⟩

end SixBirdsFoundationsVI.Laws.G13ThinOrbitSaturation
