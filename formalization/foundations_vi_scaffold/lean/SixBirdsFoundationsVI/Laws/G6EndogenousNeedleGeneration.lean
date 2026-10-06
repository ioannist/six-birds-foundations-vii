/-!
G6 Endogenous Needle Generation: abstract covering and hole-forming schemas.

This file formalizes the layer-agnostic theorem surface from `THEOREMS.md` for
G6. It does not construct Recaman's sequence, endogenous obstruction sets,
OEIS-specific facts, or concrete `gamma`/`rho` rate ledgers; those are
calibration and lab content.
-/

namespace SixBirdsFoundationsVI.Laws.G6EndogenousNeedleGeneration

/--
`[H-G6-dominant-pressure]`, reduced to the hole-count consequence used by the
covering schema for one fixed finite audit window.

Whenever the current hole count is positive, some later audited block strictly
decreases it. The concrete block decomposition, first-visit charge, and
`rho`/`gamma` inequality are instance data; the abstract proof only needs this
strict decrease surface.
-/
def DominantPressure (holes : Nat → Nat) : Prop :=
  ∀ n : Nat, holes n > 0 → ∃ m : Nat, m > n ∧ holes m < holes n

/--
G6 covering schema for one audit window: dominant pressure forces eventual
coverage from every starting time.

The proof is strong induction on the current hole count. If the count is zero,
we are done. If it is positive, dominant pressure supplies a later time with a
strictly smaller count, and the induction hypothesis finishes from there.
-/
theorem covering_schema {holes : Nat → Nat}
    (hpressure : DominantPressure holes) (n : Nat) :
    ∃ N : Nat, n ≤ N ∧ holes N = 0 := by
  let motive : Nat → Prop :=
    fun k : Nat => ∀ n : Nat, holes n = k → ∃ N : Nat, n ≤ N ∧ holes N = 0
  have hmain : ∀ k : Nat, motive k := by
    intro k
    exact Nat.strongRecOn (motive := motive) k (by
      intro k ih n hn
      cases k with
      | zero =>
          exact ⟨n, Nat.le_refl n, by simpa using hn⟩
      | succ k' =>
          have hpositive : holes n > 0 := by
            rw [hn]
            exact Nat.succ_pos k'
          rcases hpressure n hpositive with ⟨m, hmn, hsmall⟩
          have hmaller : holes m < Nat.succ k' := by
            simpa [hn] using hsmall
          rcases ih (holes m) hmaller m rfl with ⟨N, hmN, hzero⟩
          exact ⟨N, Nat.le_trans (Nat.le_of_lt hmn) hmN, hzero⟩)
  exact hmain (holes n) n rfl

/--
`[H-G6-dominant-obstruction]`, reduced to the per-step consequence needed for
the hole-forming schema for one displayed target.

`visited n` means the target has been visited by time `n`. The hypothesis says
the target is unvisited at the displayed start time `N`, and obstruction
dominance propagates non-visitation one step forward on every later time.
-/
def DominantObstruction (visited : Nat → Prop) (N : Nat) : Prop :=
  ¬ visited N ∧
    ∀ n : Nat, N ≤ n → ¬ visited n → ¬ visited (n + 1)

/--
G6 hole-forming schema: a dominant obstruction makes the displayed target a
permanent hole after the certificate time `N`.

The proof is ordinary induction on the offset from `N` to the queried time.
-/
theorem hole_forming_schema {visited : Nat → Prop} {N : Nat}
    (hobstruct : DominantObstruction visited N) :
    ∀ n : Nat, N ≤ n → ¬ visited n := by
  rcases hobstruct with ⟨hstart, hstep⟩
  intro n
  induction n with
  | zero =>
      intro hle
      have hNzero : N = 0 := Nat.eq_zero_of_le_zero hle
      subst N
      exact hstart
  | succ n ih =>
      intro hle
      cases Nat.eq_or_lt_of_le hle with
      | inl heq =>
          subst N
          exact hstart
      | inr hlt =>
          have hprev : N ≤ n := Nat.le_of_lt_succ hlt
          exact hstep n hprev (ih hprev)

end SixBirdsFoundationsVI.Laws.G6EndogenousNeedleGeneration
