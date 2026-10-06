namespace SixBirdsIII

structure Subset3 where
  hasA : Bool
  hasB : Bool
  hasC : Bool
deriving DecidableEq, Repr

def subsetAOnly : Subset3 :=
  { hasA := true, hasB := false, hasC := false }

def addBIfA (s : Subset3) : Subset3 :=
  if s.hasA then { s with hasB := true } else s

def addCIfB (s : Subset3) : Subset3 :=
  if s.hasB then { s with hasC := true } else s

def IdempotentEndomap {C : Type} (E : C -> C) : Prop :=
  forall x : C, E (E x) = E x

def NoncommutingEndomaps {C : Type} (E1 E2 : C -> C) : Prop :=
  exists x : C, E1 (E2 x) ≠ E2 (E1 x)

theorem addBIfA_idempotent : IdempotentEndomap addBIfA := by
  intro s
  cases s with
  | mk hasA hasB hasC =>
      cases hasA <;> cases hasB <;> cases hasC <;> rfl

theorem addCIfB_idempotent : IdempotentEndomap addCIfB := by
  intro s
  cases s with
  | mk hasA hasB hasC =>
      cases hasA <;> cases hasB <;> cases hasC <;> rfl

theorem addBIfA_addCIfB_noncommute : NoncommutingEndomaps addBIfA addCIfB := by
  refine ⟨subsetAOnly, ?_⟩
  decide

theorem noncommuting_completions :
    exists C : Type,
      exists E1 E2 : C -> C,
        IdempotentEndomap E1 /\
          IdempotentEndomap E2 /\
          NoncommutingEndomaps E1 E2 := by
  refine ⟨Subset3, addBIfA, addCIfB, ?_, ?_, ?_⟩
  · exact addBIfA_idempotent
  · exact addCIfB_idempotent
  · exact addBIfA_addCIfB_noncommute

def CompletionPastingDefect {C : Type} (E1 E2 : C -> C) : Prop :=
  exists c : C, E1 (E2 c) ≠ E2 (E1 c)

def CompletionsCommute {C : Type} (E1 E2 : C -> C) : Prop :=
  forall c : C, E1 (E2 c) = E2 (E1 c)

theorem completion_pasting_defect {C : Type} (E1 E2 : C -> C) :
    CompletionPastingDefect E1 E2 <-> ¬ CompletionsCommute E1 E2 := by
  constructor
  · rintro ⟨c, hc⟩ hcomm
    exact hc (hcomm c)
  · intro hnot
    exact Classical.byContradiction (fun hno => by
      apply hnot
      intro c
      exact Classical.byContradiction (fun hc => hno ⟨c, hc⟩))

theorem completion_example_has_pasting_defect :
    CompletionPastingDefect addBIfA addCIfB :=
  addBIfA_addCIfB_noncommute

end SixBirdsIII
