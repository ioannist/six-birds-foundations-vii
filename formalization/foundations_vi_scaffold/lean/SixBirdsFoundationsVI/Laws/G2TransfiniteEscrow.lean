/-!
G2 Transfinite Escrow: setup and Theorem Part (a).

This file formalizes the stage-indexed run, presentations, escrow maps, and
stage-coherence audit from `THEOREMS.md` for G2. It proves the abstract Part
(a) theorem: a well-founded escrow carrier rules out an infinite nonterminal
run whose escrow value strictly descends at every nonterminal step.
-/

namespace SixBirdsFoundationsVI.Laws.G2TransfiniteEscrow

/--
A stage-indexed run follows the stage-indexed transition `T`.

The fixed-transition case from the prose is represented by a constant `T k`.
-/
def Run {X : Type} (x : Nat → X) (T : Nat → X → X) : Prop :=
  ∀ k : Nat, x (k + 1) = T k (x k)

/--
An infinite nonterminal run never reaches the accepted terminal set `A`.
-/
def Nonterminal {X : Type} (x : Nat → X) (A : X → Prop) : Prop :=
  ∀ k : Nat, ¬ A (x k)

/--
`[H-G2-stage-coherence]`: the composed presentation-change-plus-step escrow
strictly decreases at every nonterminal stage.

The definition is stated on the realized run values `x k` and `x (k+1)`. The
separate `Run x T` hypothesis records that `x (k+1)` is exactly the native
transition `T k (x k)`, so the audit is still the composed native-step plus
re-presentation check from the prose.
-/
def StageCoherence {X W : Type} {P : Nat → Type}
    (x : Nat → X) (A : X → Prop)
    (pi : (k : Nat) → X → P k)
    (e : (k : Nat) → P k → W)
    (wlt : W → W → Prop) : Prop :=
  ∀ k : Nat, ¬ A (x k) →
    wlt (e (k + 1) (pi (k + 1) (x (k + 1)))) (e k (pi k (x k)))

/--
Accessible elements cannot start an infinite strictly descending `Nat`-indexed
chain.

The proof is by induction on the accessibility witness for the chain head. One
descent step moves from `f 0` to `f 1`, and the induction hypothesis is applied
to the tail sequence `n ↦ f (n+1)`.
-/
theorem no_descending_chain_from_acc {W : Type} {wlt : W → W → Prop}
    {head : W} (hacc : Acc wlt head) :
    ∀ f : Nat → W,
      f 0 = head →
        (∀ k : Nat, wlt (f (k + 1)) (f k)) →
          False := by
  induction hacc with
  | intro x hprev ih =>
      intro f hhead hdesc
      have hstep : wlt (f 1) x := by
        rw [← hhead]
        exact hdesc 0
      exact ih (f 1) hstep (fun n => f (n + 1)) rfl (by
        intro k
        exact hdesc (k + 1))

/--
A well-founded strict order admits no infinite strictly descending
`Nat`-indexed chain.
-/
theorem wellFounded_no_descending_chain {W : Type} {wlt : W → W → Prop}
    (hwf : WellFounded wlt) (f : Nat → W)
    (hdesc : ∀ k : Nat, wlt (f (k + 1)) (f k)) :
    False :=
  no_descending_chain_from_acc (hwf.apply (f 0)) f rfl hdesc

/--
G2 Theorem Part (a): stage-coherent escrow descent into a well-founded carrier
rules out infinite nonterminal runs.

The `Run x T` hypothesis records the stage-indexed native dynamics. The proof
uses `StageCoherence` to build the descending escrow chain
`k ↦ e k (pi k (x k))`, then contradicts well-foundedness.
-/
theorem no_infinite_nonterminal_run {X W : Type} {P : Nat → Type}
    {x : Nat → X} {T : Nat → X → X} {A : X → Prop}
    {pi : (k : Nat) → X → P k}
    {e : (k : Nat) → P k → W}
    {wlt : W → W → Prop}
    (_hrun : Run x T)
    (hcoh : StageCoherence x A pi e wlt)
    (hwf : WellFounded wlt)
    (hnonterminal : Nonterminal x A) :
    False := by
  let escrow : Nat → W := fun k => e k (pi k (x k))
  have hdesc : ∀ k : Nat, wlt (escrow (k + 1)) (escrow k) := by
    intro k
    exact hcoh k (hnonterminal k)
  exact wellFounded_no_descending_chain hwf escrow hdesc

/--
Contrapositive wrapper for the main theorem: under the G2 audit and
well-founded escrow order, the run cannot be nonterminal forever.

This is the constructive form of the prose sentence "therefore every run
reaches `A` in finitely many steps"; extracting an explicit `∃ k, A (x k)` from
`¬ Nonterminal x A` would require an additional classical decidability step and
is deliberately not introduced here.
-/
theorem not_nonterminal_of_stage_coherence {X W : Type} {P : Nat → Type}
    {x : Nat → X} {T : Nat → X → X} {A : X → Prop}
    {pi : (k : Nat) → X → P k}
    {e : (k : Nat) → P k → W}
    {wlt : W → W → Prop}
    (hrun : Run x T)
    (hcoh : StageCoherence x A pi e wlt)
    (hwf : WellFounded wlt) :
    ¬ Nonterminal x A := by
  intro hnonterminal
  exact no_infinite_nonterminal_run hrun hcoh hwf hnonterminal

end SixBirdsFoundationsVI.Laws.G2TransfiniteEscrow
