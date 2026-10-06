/-!
G9 Defect-Evacuation-to-Transport: abstract defect-ledger schemas.

This file formalizes the layer-agnostic census and transport-certificate
surface from `THEOREMS.md` for G9. It does not construct lattices, cellular
automata, rule 184, Langton's ant, or concrete recurrence-with-displacement
patterns; those are calibration and lab content.
-/

namespace SixBirdsFoundationsVI.Laws.G9DefectEvacuationTransport

/--
`[H-G9-census]`, reduced to the unresolved-defect count required for the
negative schema.

The witness `N` is the time after which the unresolved count is
non-increasing. The richer prose ledger also records creation, annihilation,
binding, and absorption events; those typed event fields are instance data, but
the abstract incompatibility theorem only needs this unresolved-count surface.
-/
def Census (unresolved : Nat → Nat) : Prop :=
  ∃ N : Nat, ∀ n : Nat, N ≤ n → unresolved (n + 1) ≤ unresolved n

/--
Unbounded unresolved creation: no tail of the run has a finite unresolved
defect bound.

This states the prose's `sup_n |unresolved_n| = infinity` / unmatched creation
alternative in elementary `Nat` terms: for every proposed bound `B` and every
tail start `N'`, some later census exceeds `B`.
-/
def UnboundedCreation (unresolved : Nat → Nat) : Prop :=
  ∀ (B N' : Nat), ∃ n : Nat, N' ≤ n ∧ unresolved n > B

/--
Tail monotonicity from a census start propagates to every explicit offset.

If the unresolved count is non-increasing from `N` onward, then the count at
time `N + k` is bounded by the count at `N`.
-/
theorem census_bound_from_start {unresolved : Nat → Nat} {N : Nat}
    (hmono : ∀ n : Nat, N ≤ n → unresolved (n + 1) ≤ unresolved n) :
    ∀ k : Nat, unresolved (N + k) ≤ unresolved N := by
  intro k
  induction k with
  | zero =>
      simp
  | succ k ih =>
      have hstep :
          unresolved ((N + k) + 1) ≤ unresolved (N + k) :=
        hmono (N + k) (Nat.le_add_right N k)
      have hcurrent :
          unresolved (N + (k + 1)) ≤ unresolved (N + k) := by
        simpa [Nat.add_assoc] using hstep
      exact Nat.le_trans hcurrent ih

/--
Tail monotonicity from a census start bounds every later time by the start
value.

This is the indexed form used to contradict unbounded creation on the same
tail.
-/
theorem census_tail_bound {unresolved : Nat → Nat} {N : Nat}
    (hmono : ∀ n : Nat, N ≤ n → unresolved (n + 1) ≤ unresolved n) :
    ∀ n : Nat, N ≤ n → unresolved n ≤ unresolved N := by
  intro n hn
  rcases Nat.exists_eq_add_of_le hn with ⟨k, hk⟩
  rw [hk]
  exact census_bound_from_start hmono k

/--
G9 negative schema: an exact census with eventual non-increase excludes
unbounded unresolved creation.

The proof is the substantive exclusivity fact behind the case priority:
after the census start `N`, every unresolved count is at most `unresolved N`,
so the same tail cannot contain arbitrarily large unresolved counts.
-/
theorem census_excludes_unbounded_creation {unresolved : Nat → Nat}
    (hcensus : Census unresolved) : ¬ UnboundedCreation unresolved := by
  intro hunbounded
  rcases hcensus with ⟨N, hmono⟩
  rcases hunbounded (unresolved N) N with ⟨n, hn, hgt⟩
  have hbound : unresolved n ≤ unresolved N :=
    census_tail_bound hmono n hn
  exact Nat.not_lt_of_ge hbound hgt

/--
Abstract transporter data for G9's positive schema.

`assigned d = some t` says defect `d` is assigned by the ledger to transporter
record `t`; `displacement t` is the declared motion of `t`; and
`certificate t` stands for the recurrence-with-displacement equality for that
transporter. Concrete lattice equalities are lab/instance content.
-/
structure TransportData (Defect Transporter Disp : Type) where
  assigned : Defect → Option Transporter
  displacement : Transporter → Disp
  certificate : Transporter → Prop

/--
Certified transport regime, in the abstract positive-schema sense.

There is a certified transporter with nonzero displacement, and at least one
persistent defect is assigned to it by the ledger.
-/
def CertifiedTransportRegime {Defect Transporter Disp : Type}
    (data : TransportData Defect Transporter Disp) (zero : Disp) : Prop :=
  ∃ t : Transporter, data.certificate t ∧ data.displacement t ≠ zero ∧
    ∃ d : Defect, data.assigned d = some t

/--
G9 positive schema: certified transporter data plus a nonzero assigned
transporter witness packages into a certified transport regime.

This intentionally keeps the proof shallow. The prose's positive theorem
assumes `[H-G9-absorb]` already supplies the transporter records and their
recurrence certificates; the abstract theorem only repackages that supplied
data with the required nonzero-displacement witness.
-/
theorem certified_transport_regime_of_assigned_nonzero
    {Defect Transporter Disp : Type}
    (data : TransportData Defect Transporter Disp) (zero : Disp)
    (hcert : ∀ t : Transporter, data.certificate t)
    (hwitness : ∃ (t : Transporter) (d : Defect),
      data.assigned d = some t ∧ data.displacement t ≠ zero) :
    CertifiedTransportRegime data zero := by
  rcases hwitness with ⟨t, d, hassigned, hnonzero⟩
  exact ⟨t, hcert t, hnonzero, d, hassigned⟩

end SixBirdsFoundationsVI.Laws.G9DefectEvacuationTransport
