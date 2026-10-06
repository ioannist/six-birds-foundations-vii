
/-!
G3 Amortized Potential Currency: setup and telescoping theorem.

This file formalizes the finite-prefix amortized-analysis identity from
`THEOREMS.md` for G3. The prose says costs and potentials are nonnegative
rationals. In this Mathlib-free Lean scaffold, the mechanized theorem uses
exact integer-valued costs and potentials with explicit nonnegativity
hypotheses. This is the ordered-additive fragment needed by the telescoping
argument; the later lab packet supplies the concrete binary-counter and
dynamic-array calibrations.
-/

namespace SixBirdsFoundationsVI.Laws.G3AmortizedCurrency

/--
A finite run prefix is represented by a list of declared-cost/next-state pairs.

Together with an initial state `s0`, the list
`[(a_1, s_1), ..., (a_n, s_n)]` represents
`s_0 -> s_1 -> ... -> s_n` with actual costs `a_i`.
-/
abbrev RunPrefix (S : Type) := List (Int × S)

/--
The final state of a finite run prefix, starting from `s0`.
-/
def FinalState {S : Type} (s0 : S) : RunPrefix S → S
  | [] => s0
  | (_, s) :: rest => FinalState s rest

/--
The actual-cost sum `sum_i a_i` over a finite run prefix.
-/
def ActualCostSum {S : Type} : RunPrefix S → Int
  | [] => 0
  | (a, _) :: rest => a + ActualCostSum rest

/--
One amortized step cost:
`a_hat_i = a_i + Phi(s_i) - Phi(s_{i-1})`.
-/
def AmortizedCostAt {S : Type} (Phi : S → Int) (prev : S)
    (step : Int × S) : Int :=
  step.fst + Phi step.snd - Phi prev

/--
The amortized-cost sum over a finite run prefix.

The recursion carries the previous state so that each step can use
`Phi(s_{i-1})` and `Phi(s_i)` in the amortized-cost formula.
-/
def AmortizedCostSum {S : Type} (Phi : S → Int) (s0 : S) :
    RunPrefix S → Int
  | [] => 0
  | step :: rest => AmortizedCostAt Phi s0 step +
      AmortizedCostSum Phi step.snd rest

/--
The potential is nonnegative on every state.
-/
def NonnegativePotential {S : Type} (Phi : S → Int) : Prop :=
  ∀ s : S, 0 ≤ Phi s

/--
The declared actual costs in a run prefix are nonnegative.

The telescoping identity itself does not need this hypothesis, but it records
the setup clause that actual costs are drawn from the nonnegative part of the
chosen exact cost domain.
-/
def NonnegativeActualCosts {S : Type} : RunPrefix S → Prop
  | [] => True
  | (a, _) :: rest => 0 ≤ a ∧ NonnegativeActualCosts rest

/--
The list of per-step amortized costs for a finite run prefix.

This exposes the "every step is bounded by `B`" hypothesis used by the
uniform-bound corollary.
-/
def AmortizedCostList {S : Type} (Phi : S → Int) (s0 : S) :
    RunPrefix S → List Int
  | [] => []
  | step :: rest => AmortizedCostAt Phi s0 step ::
      AmortizedCostList Phi step.snd rest

/--
Every entry of a cost list is bounded above by `B`.
-/
def AllLe : List Int → Int → Prop
  | [], _ => True
  | x :: xs, B => x ≤ B ∧ AllLe xs B

/--
`ScaleCost n B` is the Mathlib-free repeated-addition form of `n * B`.

Using this recursive definition keeps the uniform-bound theorem independent of
external algebra libraries while matching the prose statement `n*B`.
-/
def ScaleCost : Nat → Int → Int
  | 0, _ => 0
  | n + 1, B => ScaleCost n B + B

/--
G3's telescoping identity:

`sum a_i = sum a_hat_i + Phi(s_0) - Phi(s_n)`.

The proof is a direct induction on the finite run prefix. The inductive step is
exactly the cancellation of the adjacent potential terms in the prose proof
spine.
-/
theorem telescoping_identity {S : Type} (Phi : S → Int) (s0 : S)
    (run : RunPrefix S) :
    ActualCostSum run =
      AmortizedCostSum Phi s0 run + Phi s0 - Phi (FinalState s0 run) := by
  induction run generalizing s0 with
  | nil =>
      simp [ActualCostSum, AmortizedCostSum, FinalState]
  | cons step rest ih =>
      cases step with
      | mk a s1 =>
          simp [ActualCostSum, AmortizedCostSum, AmortizedCostAt, FinalState]
          have htail := ih s1
          omega

/--
G3's finite-prefix upper bound:

`sum a_i <= sum a_hat_i + Phi(s_0)`, using `Phi(s_n) >= 0`.
-/
theorem telescoping_bound {S : Type} (Phi : S → Int)
    (hPhi : NonnegativePotential Phi) (s0 : S) (run : RunPrefix S)
    (_hActual : NonnegativeActualCosts run) :
    ActualCostSum run ≤ AmortizedCostSum Phi s0 run + Phi s0 := by
  have hid := telescoping_identity Phi s0 run
  have hnon : 0 ≤ Phi (FinalState s0 run) := hPhi (FinalState s0 run)
  rw [hid]
  omega

/--
If every amortized step cost is at most `B`, then the amortized sum is at most
`n` copies of `B`, where `n` is the run-prefix length.
-/
theorem amortized_sum_le_scale {S : Type} (Phi : S → Int) (s0 : S)
    (run : RunPrefix S) (B : Int) :
    AllLe (AmortizedCostList Phi s0 run) B →
      AmortizedCostSum Phi s0 run ≤ ScaleCost run.length B := by
  induction run generalizing s0 with
  | nil =>
      intro _hAll
      simp [AmortizedCostSum, ScaleCost]
  | cons step rest ih =>
      cases step with
      | mk a s1 =>
          intro hAll
          simp [AmortizedCostList, AllLe] at hAll
          have hHead : AmortizedCostAt Phi s0 (a, s1) ≤ B := hAll.left
          have hTail :
              AmortizedCostSum Phi s1 rest ≤ ScaleCost rest.length B :=
            ih s1 hAll.right
          simp [AmortizedCostSum, ScaleCost]
          omega

/--
G3's uniform bounded-cost corollary:

if each amortized step is bounded by `B`, every length-`n` prefix has actual
cost at most `n` copies of `B` plus the initial potential.
-/
theorem uniform_actual_cost_bound {S : Type} (Phi : S → Int)
    (hPhi : NonnegativePotential Phi) (s0 : S) (run : RunPrefix S)
    (B : Int) (_hActual : NonnegativeActualCosts run) :
    AllLe (AmortizedCostList Phi s0 run) B →
      ActualCostSum run ≤ ScaleCost run.length B + Phi s0 := by
  intro hAll
  have htel := telescoping_bound Phi hPhi s0 run _hActual
  have hsum := amortized_sum_le_scale Phi s0 run B hAll
  omega

end SixBirdsFoundationsVI.Laws.G3AmortizedCurrency
