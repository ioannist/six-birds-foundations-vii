import FoundationsVII.Semantics.Rewriting

namespace FoundationsVII.Semantics

universe u

/-- A lower state is its predicate of present facts. -/
def LowerState (Fact : Type u) := Fact → Prop

def select {Fact : Type u} (before : LowerState Fact) (keep : Fact → Prop) :
    LowerState Fact := fun f => before f ∧ keep f

def SelectionStep {Fact : Type u} (before after : LowerState Fact) : Prop :=
  ∃ keep, after = select before keep

theorem selection_step_preserves {Fact : Type u} {before after : LowerState Fact}
    (h : SelectionStep before after) (f : Fact) : after f → before f := by
  obtain ⟨keep, rfl⟩ := h
  exact And.left

theorem selection_run_preserves {Fact : Type u} {before after : LowerState Fact}
    (h : Star SelectionStep before after) (f : Fact) : after f → before f := by
  induction h with
  | refl _ => exact id
  | @cons x y z step rest ih =>
      exact fun hf => selection_step_preserves step f (ih hf)

def insertFact {Fact : Type u} (before : LowerState Fact) (newFact : Fact) :
    LowerState Fact := fun f => before f ∨ f = newFact

theorem insertion_creates_fact {Fact : Type u} (f : Fact) :
    insertFact (fun _ => False) f f ∧ ¬ (fun _ : Fact => False) f := by
  exact ⟨Or.inr rfl, False.elim⟩

theorem insertion_not_selection {Fact : Type u} (f : Fact) :
    ¬ SelectionStep (fun _ => False) (insertFact (fun _ => False) f) := by
  intro h
  exact selection_step_preserves h f (Or.inr rfl)

end FoundationsVII.Semantics
