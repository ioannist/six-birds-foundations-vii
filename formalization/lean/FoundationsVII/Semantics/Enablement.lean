import FoundationsVII.Semantics.Join
import FoundationsVII.Semantics.Search

namespace FoundationsVII.Semantics

/-- Lower dynamics is a strict three-state order. -/
def lowerStep (a b : Fin 3) : Prop := a.val < b.val

/-- The vector records every state reachable from a lower seed. -/
def reachableVector (a : Fin 3) (x : Fin 3) : Bool := decide (a.val ≤ x.val)

theorem lower_reachable_iff (a x : Fin 3) :
    ReachWithin lowerStep a 1 x ↔ reachableVector a x = true := by
  constructor
  · intro h
    have mono : ∀ {n y}, ReachWithin lowerStep a n y → a.val ≤ y.val := by
      intro n y hr
      induction hr with
      | zero => exact Nat.le_refl _
      | next _ step ih => exact Nat.le_trans ih (Nat.le_of_lt step)
      | weaken _ ih => exact ih
    exact decide_eq_true (mono h)
  · intro h
    have hle : a.val ≤ x.val := of_decide_eq_true h
    by_cases heq : a = x
    · subst x
      exact ReachWithin.zero
    · have hlt : a.val < x.val := by
        have hv : a.val ≠ x.val := by
          intro hv
          apply heq
          exact Fin.ext hv
        omega
      exact ReachWithin.next ReachWithin.zero hlt

/-- Upper states are precisely the three reachable-state vectors formed by A. -/
def FormedState := {members : Fin 3 → Bool // ∃ a : Fin 3, members = reachableVector a}

def form (a : Fin 3) : FormedState := ⟨reachableVector a, a, rfl⟩

/-- The upper transition exists only when a lower transition supplies it. -/
def upperStep (b c : FormedState) : Prop :=
  ∃ a a', lowerStep a a' ∧ b = form a ∧ c = form a'

theorem lower_supplies_upper {a a' : Fin 3} (h : lowerStep a a') :
    upperStep (form a) (form a') := ⟨a, a', h, rfl, rfl⟩

theorem upper_requires_lower {b c : FormedState} (h : upperStep b c) :
    ∃ a a', lowerStep a a' ∧ b = form a ∧ c = form a' := h

theorem form_injective : Function.Injective form := by
  intro a b hab
  have ha : (form a).val a = (form b).val a := congrArg (fun s : FormedState => s.val a) hab
  have hb : (form a).val b = (form b).val b := congrArg (fun s : FormedState => s.val b) hab
  simp [form, reachableVector] at ha hb
  apply Fin.ext
  omega

theorem form_surjective : Function.Surjective form := by
  rintro ⟨members, ⟨a, ha⟩⟩
  refine ⟨a, ?_⟩
  apply Subtype.ext
  exact ha.symm

theorem upper_step_iff_lower (a a' : Fin 3) :
    upperStep (form a) (form a') ↔ lowerStep a a' := by
  constructor
  · rintro ⟨x, y, hxy, hx, hy⟩
    have hax : a = x := form_injective hx
    have hay : a' = y := form_injective hy
    simpa [hax, hay] using hxy
  · exact lower_supplies_upper

theorem three_distinct_upper_states :
    form (0 : Fin 3) ≠ form (1 : Fin 3) ∧
    form (1 : Fin 3) ≠ form (2 : Fin 3) ∧
    form (0 : Fin 3) ≠ form (2 : Fin 3) := by
  constructor
  · intro h
    have := form_injective h
    exact (by decide : (0 : Fin 3) ≠ 1) this
  constructor
  · intro h
    have := form_injective h
    exact (by decide : (1 : Fin 3) ≠ 2) this
  · intro h
    have := form_injective h
    exact (by decide : (0 : Fin 3) ≠ 2) this

theorem nontrivial_upper_formation :
    upperStep (form (0 : Fin 3)) (form (1 : Fin 3)) ∧
    form (0 : Fin 3) ≠ form (1 : Fin 3) := by
  exact ⟨lower_supplies_upper (by simp [lowerStep]), three_distinct_upper_states.1⟩

/-- This quotient of A's reachable-set representation remembers whether 1 is
reachable but forgets whether 0 is reachable. -/
def lowerQuotient (a : Fin 3) : Bool := reachableVector a 1

def upperQuotient (b : FormedState) : Bool := b.val 1

theorem quotient_commutes_with_formation (a : Fin 3) :
    upperQuotient (form a) = lowerQuotient a := rfl

def upperObservable (b : FormedState) : Bool := b.val 0

theorem enabled_not_descended :
    upperStep (form (0 : Fin 3)) (form (1 : Fin 3)) ∧
    ¬ FactorsOnImage upperQuotient upperObservable := by
  constructor
  · exact lower_supplies_upper (by simp [lowerStep])
  · intro h
    have noSplit := (factorsOnImage_iff_no_split _ _).1 h
    exact noSplit ⟨form 0, form 1, by decide, by decide⟩

/-- A fibre-constant observable descends through the reached quotient image. -/
theorem observable_descends_of_fibre_constant
    {B Q X : Type} (q : B → Q) (f : B → X)
    (constant : ∀ b c, q b = q c → f b = f c) :
    FactorsOnImage q f := by
  apply (factorsOnImage_iff_no_split q f).2
  rintro ⟨b, c, hq, hf⟩
  exact hf (constant b c hq)

theorem quotient_observable_descends :
    FactorsOnImage upperQuotient upperQuotient := by
  exact observable_descends_of_fibre_constant upperQuotient _
    (fun _ _ h => h)

end FoundationsVII.Semantics
