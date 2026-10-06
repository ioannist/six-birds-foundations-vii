import SixBirdsMetaMath.FoundationsIV.Transport.DescentRepair

/-!
F7 Sufficiency Closure.

Sufficiency is closure for declared futures: a current quotient is
predictively closed exactly when the declared future signature factors through
that quotient, equivalently when no current fiber contains two different future
signatures.
-/

namespace SixBirdsMetaMath.FoundationsIV.Stability.SufficiencyClosure

open SixBirdsMetaMath.FoundationsIV.Transport.DescentRepair

/-- The current quotient already determines the declared future signature. -/
def PackageClosed {Hist Q Future : Type} (π : Hist → Q)
    (future : Hist → Future) : Prop :=
  ∀ x y : Hist, π x = π y → future x = future y

/-- The future signature factors through the current quotient. -/
def FactorsThroughQ {Hist Q Future : Type} (π : Hist → Q)
    (future : Hist → Future) : Prop :=
  ∃ futureBar : Q → Future, futureBar ∘ π = future

/-- Same current object, different future signature. -/
def SufficiencySplitPair {Hist Q Future : Type} (π : Hist → Q)
    (future : Hist → Future) : (Hist × Hist) → Prop :=
  fun pair => π pair.1 = π pair.2 ∧ future pair.1 ≠ future pair.2

/-- Same future signature, different current object: redundancy relative to the
declared futures. -/
def RedundancySplitPair {Hist Q Future : Type} (π : Hist → Q)
    (future : Hist → Future) : (Hist × Hist) → Prop :=
  fun pair => future pair.1 = future pair.2 ∧ π pair.1 ≠ π pair.2

/-- The future quotient also determines the current quotient. -/
def FutureDeterminesCurrent {Hist Q Future : Type} (π : Hist → Q)
    (future : Hist → Future) : Prop :=
  ∀ x y : Hist, future x = future y → π x = π y

/-- Memory/refinement repair preserving the current object and appending the
future signature. -/
def currentMemoryRepair {Hist Q Future : Type} (π : Hist → Q)
    (future : Hist → Future) : Hist → Q × Future :=
  fun h => (π h, future h)

/-- Four current/future quotient-comparison statuses. -/
inductive SufficiencyStatus where
  | exactClosure
  | redundantClosure
  | predictiveNonClosure
  | incomparable
deriving DecidableEq

/-- Meaning of each sufficiency-closure status. -/
def SufficiencyStatusHolds {Hist Q Future : Type} (π : Hist → Q)
    (future : Hist → Future) : SufficiencyStatus → Prop
  | SufficiencyStatus.exactClosure =>
      PackageClosed π future ∧ FutureDeterminesCurrent π future
  | SufficiencyStatus.redundantClosure =>
      PackageClosed π future ∧ ¬ FutureDeterminesCurrent π future
  | SufficiencyStatus.predictiveNonClosure =>
      ¬ PackageClosed π future ∧ FutureDeterminesCurrent π future
  | SufficiencyStatus.incomparable =>
      ¬ PackageClosed π future ∧ ¬ FutureDeterminesCurrent π future

/-- Exactly one sufficiency status applies. -/
def ExactlyOneSufficiencyStatus {Hist Q Future : Type} (π : Hist → Q)
    (future : Hist → Future) : Prop :=
  ∃ status : SufficiencyStatus,
    SufficiencyStatusHolds π future status ∧
      ∀ other : SufficiencyStatus,
        SufficiencyStatusHolds π future other → other = status

/-- Package closure is the same as absence of sufficiency split pairs. -/
theorem package_closed_iff_no_sufficiency_split {Hist Q Future : Type}
    (π : Hist → Q) (future : Hist → Future) :
    PackageClosed π future ↔ ObstructionEmpty (SufficiencySplitPair π future) := by
  constructor
  · intro hclosed pair hsplit
    rcases pair with ⟨x, y⟩
    exact hsplit.2 (hclosed x y hsplit.1)
  · intro hno x y hπ
    exact Classical.byContradiction (fun hneq =>
      False.elim (hno (x, y) ⟨hπ, hneq⟩))

/-- Redundancy split-pair emptiness is the reverse quotient determination. -/
theorem future_determines_current_iff_no_redundancy_split {Hist Q Future : Type}
    (π : Hist → Q) (future : Hist → Future) :
    FutureDeterminesCurrent π future ↔
      ObstructionEmpty (RedundancySplitPair π future) := by
  constructor
  · intro hdet pair hsplit
    rcases pair with ⟨x, y⟩
    exact hsplit.2 (hdet x y hsplit.1)
  · intro hno x y hfuture
    exact Classical.byContradiction (fun hneq =>
      False.elim (hno (x, y) ⟨hfuture, hneq⟩))

/-- The memory/refinement repair makes the future signature descend. -/
theorem current_memory_repair_closed {Hist Q Future : Type} (π : Hist → Q)
    (future : Hist → Future) :
    PackageClosed (currentMemoryRepair π future) future := by
  intro x y h
  exact congrArg Prod.snd h

/-- The memory/refinement repair supplies an explicit lower future map. -/
theorem current_memory_repair_factors {Hist Q Future : Type} (π : Hist → Q)
    (future : Hist → Future) :
    FactorsThroughQ (currentMemoryRepair π future) future := by
  refine ⟨Prod.snd, ?_⟩
  funext h
  rfl

/-- The two quotient-inclusion bits classify the current/future comparison. -/
theorem sufficiency_status_partition {Hist Q Future : Type} (π : Hist → Q)
    (future : Hist → Future) :
    ExactlyOneSufficiencyStatus π future := by
  classical
  by_cases hclosed : PackageClosed π future
  · by_cases hreverse : FutureDeterminesCurrent π future
    · refine ⟨SufficiencyStatus.exactClosure, ⟨hclosed, hreverse⟩, ?_⟩
      intro other hother
      cases other with
      | exactClosure => rfl
      | redundantClosure =>
          exact False.elim (hother.2 hreverse)
      | predictiveNonClosure =>
          exact False.elim (hother.1 hclosed)
      | incomparable =>
          exact False.elim (hother.1 hclosed)
    · refine ⟨SufficiencyStatus.redundantClosure, ⟨hclosed, hreverse⟩, ?_⟩
      intro other hother
      cases other with
      | exactClosure =>
          exact False.elim (hreverse hother.2)
      | redundantClosure => rfl
      | predictiveNonClosure =>
          exact False.elim (hother.1 hclosed)
      | incomparable =>
          exact False.elim (hother.1 hclosed)
  · by_cases hreverse : FutureDeterminesCurrent π future
    · refine ⟨SufficiencyStatus.predictiveNonClosure, ⟨hclosed, hreverse⟩, ?_⟩
      intro other hother
      cases other with
      | exactClosure =>
          exact False.elim (hclosed hother.1)
      | redundantClosure =>
          exact False.elim (hclosed hother.1)
      | predictiveNonClosure => rfl
      | incomparable =>
          exact False.elim (hother.2 hreverse)
    · refine ⟨SufficiencyStatus.incomparable, ⟨hclosed, hreverse⟩, ?_⟩
      intro other hother
      cases other with
      | exactClosure =>
          exact False.elim (hclosed hother.1)
      | redundantClosure =>
          exact False.elim (hclosed hother.1)
      | predictiveNonClosure =>
          exact False.elim (hreverse hother.2)
      | incomparable => rfl

/--
Sufficiency Closure Normal Form. For a quotient map `π`, package closure for a
declared future signature is equivalent to factorization through `π`, and also
to emptiness of the sufficiency split-pair obstruction. The four comparison
statuses record exact closure, redundant closure, predictive non-closure, and
incomparability.

The surjectivity hypothesis records that `π` is a quotient map onto its
declared current quotient carrier.
-/
theorem sufficiency_closure {Hist Q Future : Type} (π : Hist → Q)
    (future : Hist → Future) (hπ : Function.Surjective π) :
    (PackageClosed π future ↔ FactorsThroughQ π future) ∧
      (PackageClosed π future ↔ ObstructionEmpty (SufficiencySplitPair π future)) ∧
        ExactlyOneSufficiencyStatus π future := by
  constructor
  · constructor
    · intro hclosed
      classical
      let futureBar : Q → Future := fun q => future (Classical.choose (hπ q))
      refine ⟨futureBar, ?_⟩
      funext x
      unfold futureBar
      let x0 : Hist := Classical.choose (hπ (π x))
      have hx0 : π x0 = π x := Classical.choose_spec (hπ (π x))
      change future x0 = future x
      exact hclosed x0 x hx0
    · intro hfactors
      rcases hfactors with ⟨futureBar, hcomm⟩
      intro x y hxy
      have hx : futureBar (π x) = future x := congrFun hcomm x
      have hy : futureBar (π y) = future y := congrFun hcomm y
      calc
        future x = futureBar (π x) := hx.symm
        _ = futureBar (π y) := by rw [hxy]
        _ = future y := hy
  · exact ⟨(package_closed_iff_no_sufficiency_split π future),
      sufficiency_status_partition π future⟩

end SixBirdsMetaMath.FoundationsIV.Stability.SufficiencyClosure
