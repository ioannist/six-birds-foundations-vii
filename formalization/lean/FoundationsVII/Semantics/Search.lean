import FoundationsVII.Semantics.Rewriting

namespace FoundationsVII.Semantics

universe u

/-- A path of at most `h` steps, with unused fuel permitted. -/
inductive ReachWithin {State : Type u} (step : State → State → Prop)
    (start : State) : Nat → State → Prop where
  | zero {h : Nat} : ReachWithin step start h start
  | next {h : Nat} {x y : State} :
      ReachWithin step start h x → step x y → ReachWithin step start (h + 1) y
  | weaken {h : Nat} {x : State} :
      ReachWithin step start h x → ReachWithin step start (h + 1) x

/-- A detector scans actual enumerated states for the target predicate. -/
def detect {State : Type u} (cases : List State) (target : State → Prop)
    [DecidablePred target] : Bool :=
  cases.any fun s => decide (target s)

theorem detector_sound {State : Type u} {step : State → State → Prop}
    {start : State} {h : Nat} {cases : List State} {target : State → Prop}
    [DecidablePred target]
    (sound : ∀ s, s ∈ cases → ReachWithin step start h s)
    (positive : detect cases target = true) :
    ∃ s, ReachWithin step start h s ∧ target s := by
  simp only [detect, List.any_eq_true, decide_eq_true_eq] at positive
  obtain ⟨s, hs, ht⟩ := positive
  exact ⟨s, sound s hs, ht⟩

theorem detector_coverage {State : Type u} {step : State → State → Prop}
    {start : State} {h : Nat} {cases : List State} {target : State → Prop}
    [DecidablePred target]
    (covers : ∀ s, ReachWithin step start h s → s ∈ cases)
    (negative : detect cases target = false) :
    ∀ s, ReachWithin step start h s → ¬ target s := by
  intro s hr ht
  have positive : detect cases target = true := by
    simp only [detect, List.any_eq_true, decide_eq_true_eq]
    exact ⟨s, covers s hr, ht⟩
  simp [negative] at positive

theorem beyond_horizon_null {State : Type u} {step : State → State → Prop}
    {start : State} {h : Nat} {cases : List State} {target : State → Prop}
    [DecidablePred target]
    (covers : ∀ s, ReachWithin step start h s → s ∈ cases)
    (closed : ∀ k s, ReachWithin step start k s → ReachWithin step start h s)
    (negative : detect cases target = false) :
    ∀ k s, ReachWithin step start k s → ¬ target s := by
  intro k s hr
  exact detector_coverage covers negative s (closed k s hr)

theorem no_contact_in_covered_family {State : Type u} {step : State → State → Prop}
    {start : State} {h : Nat} {cases : List State} {contact : State → Prop}
    [DecidablePred contact]
    (covers : ∀ s, ReachWithin step start h s → s ∈ cases)
    (negative : detect cases contact = false) :
    ¬ ∃ s, ReachWithin step start h s ∧ contact s := by
  rintro ⟨s, hr, hc⟩
  exact detector_coverage covers negative s hr hc

def oneStep (x y : Bool) : Prop := x = false ∧ y = true

instance : DecidableRel oneStep := by
  intro x y
  unfold oneStep
  infer_instance

theorem zero_horizon_coverage (s : Bool) :
    ReachWithin oneStep false 0 s → s ∈ [false] := by
  intro h
  cases h with
  | zero => simp

theorem zero_horizon_null :
    detect [false] (fun s : Bool => s = true) = false := by decide

theorem later_witness : ReachWithin oneStep false 1 true := by
  exact ReachWithin.next ReachWithin.zero ⟨rfl, rfl⟩

theorem one_horizon_sound (s : Bool) (hs : s ∈ [false, true]) :
    ReachWithin oneStep false 1 s := by
  cases s with
  | false => exact ReachWithin.zero
  | true => exact later_witness

theorem one_horizon_detects_contact :
    detect [false, true] (fun s : Bool => s = true) = true := by decide

theorem detected_contact_witness :
    ∃ s, ReachWithin oneStep false 1 s ∧ s = true := by
  exact detector_sound one_horizon_sound one_horizon_detects_contact

theorem all_bool_covered (s : Bool) (h : Nat) :
    ReachWithin oneStep false h s → s ∈ [false, true] := by
  intro _
  cases s <;> simp

/-- A contact state exists in the carrier, but this system has no transition
from its initial state. Exhausting its reachable states finds no contact. -/
def stuckStep (_ _ : Bool) : Prop := False

instance : DecidableRel stuckStep := by
  intro x y
  unfold stuckStep
  infer_instance

theorem stuck_reach_only_false {h : Nat} {s : Bool}
    (hr : ReachWithin stuckStep false h s) : s = false := by
  induction hr with
  | zero => rfl
  | next _ hs => exact False.elim hs
  | weaken _ ih => exact ih

theorem stuck_closed_at_zero (k : Nat) (s : Bool)
    (hr : ReachWithin stuckStep false k s) :
    ReachWithin stuckStep false 0 s := by
  rw [stuck_reach_only_false hr]
  exact ReachWithin.zero

theorem concrete_no_contact :
    ∀ k s, ReachWithin stuckStep false k s → s ≠ true := by
  apply beyond_horizon_null (cases := [false])
    (target := fun s : Bool => s = true)
  · intro s hs
    rw [stuck_reach_only_false hs]
    simp
  · exact stuck_closed_at_zero
  · decide

end FoundationsVII.Semantics
