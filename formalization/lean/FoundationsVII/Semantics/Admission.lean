import FoundationsVII.Semantics.Rewriting

namespace FoundationsVII.Semantics

universe u v

structure AdmissionRules (I : Type u) (Label : Type v) where
  prereq : I → I → Prop
  audit : List I → Label

namespace AdmissionRules

variable {I : Type u} {Label : Type v} [BEq I] [LawfulBEq I]

def Enabled (R : AdmissionRules I Label) (s : List I) (i : I) : Prop :=
  i ∈ s ∧ ∀ p, R.prereq p i → p ∉ s

def Step (R : AdmissionRules I Label) (s t : List I) : Prop :=
  ∃ i, Enabled R s i ∧ t = s.erase i

theorem step_preserves_nodup (R : AdmissionRules I Label)
    {s t : List I} (h : R.Step s t) (hs : s.Nodup) : t.Nodup := by
  obtain ⟨i, _, rfl⟩ := h
  exact hs.erase i

theorem star_preserves_nodup (R : AdmissionRules I Label)
    {s t : List I} (h : Star R.Step s t) (hs : s.Nodup) : t.Nodup := by
  induction h with
  | refl _ => exact hs
  | cons e _ ih => exact ih (R.step_preserves_nodup e hs)

theorem terminates (R : AdmissionRules I Label) : Terminates R.Step := by
  letI : WellFoundedRelation (List I) := measure List.length
  apply Subrelation.wf (h₂ := WellFoundedRelation.wf)
  intro t s h
  obtain ⟨i, ⟨hi, _⟩, rfl⟩ := h
  change (s.erase i).length < s.length
  rw [List.length_erase_of_mem hi]
  exact Nat.sub_lt (List.length_pos_of_mem hi) (by decide)

private theorem enabled_after_other (R : AdmissionRules I Label)
    {s : List I} {i j : I} (h : Enabled R s i) (hne : i ≠ j) :
    Enabled R (s.erase j) i := by
  constructor
  · exact (List.mem_erase_of_ne hne).2 h.1
  · intro p hp hmem
    exact h.2 p hp (List.mem_of_mem_erase hmem)

theorem commuting_admissions (R : AdmissionRules I Label)
    {s y z : List I} (hy : R.Step s y) (hz : R.Step s z) :
    y = z ∨ ∃ w, R.Step y w ∧ R.Step z w := by
  obtain ⟨i, hi, rfl⟩ := hy
  obtain ⟨j, hj, rfl⟩ := hz
  by_cases h : i = j
  · exact Or.inl (by rw [h])
  · right
    refine ⟨(s.erase i).erase j, ?_, ?_⟩
    · exact ⟨j, enabled_after_other R hj (Ne.symm h), rfl⟩
    · refine ⟨i, enabled_after_other R hi h, ?_⟩
      exact List.erase_comm i j

theorem locallyConfluent (R : AdmissionRules I Label) : LocallyConfluent R.Step := by
  intro s y z hy hz
  rcases commuting_admissions R hy hz with h | ⟨w, hyw, hzw⟩
  · subst y
    exact ⟨z, Star.refl z, Star.refl z⟩
  · exact ⟨w, Star.single hyw, Star.single hzw⟩

theorem confluent (R : AdmissionRules I Label) : Confluent R.Step :=
  newman R.terminates R.locallyConfluent

theorem unique_fixed_point (R : AdmissionRules I Label) (s : List I) :
    ∃ t, Star R.Step s t ∧ Normal R.Step t ∧
      ∀ t', Star R.Step s t' → Normal R.Step t' →
        t' = t ∧ R.audit t' = R.audit t := by
  obtain ⟨t, ht, hn, hu⟩ := unique_reachable_normal R.terminates R.confluent s
  refine ⟨t, ht, hn, ?_⟩
  intro t' ht' hn'
  have heq := hu t' ht' hn'
  exact ⟨heq, congrArg R.audit heq⟩

end AdmissionRules

inductive TwoItem where | a | b
  deriving BEq, ReflBEq, LawfulBEq, DecidableEq, Repr

def freeRules : AdmissionRules TwoItem Nat :=
  { prereq := fun _ _ => False, audit := List.length }

theorem free_example :
    Star freeRules.Step [TwoItem.a, TwoItem.b] [] ∧
    Normal freeRules.Step [] := by
  constructor
  · apply Star.cons (show freeRules.Step [TwoItem.a, TwoItem.b] [TwoItem.b] from
      ⟨TwoItem.a, ⟨by decide, by intro _ h; cases h⟩, by decide⟩)
    apply Star.cons (show freeRules.Step [TwoItem.b] [] from
      ⟨TwoItem.b, ⟨by decide, by intro _ h; cases h⟩, by decide⟩)
    exact Star.refl []
  · intro y h
    obtain ⟨i, hi, _⟩ := h
    exact False.elim (by simpa [AdmissionRules.Enabled] using hi.1)

-- A guard can disable an admission after another item has been admitted.
def disablingStep (s t : List TwoItem) : Prop :=
  ∃ i, i ∈ s ∧ (i = TwoItem.b → TwoItem.a ∈ s) ∧ t = s.erase i

theorem disabling_terminates : Terminates disablingStep := by
  letI : WellFoundedRelation (List TwoItem) := measure List.length
  apply Subrelation.wf (h₂ := WellFoundedRelation.wf)
  intro t s h
  obtain ⟨i, hi, _, rfl⟩ := h
  change (s.erase i).length < s.length
  rw [List.length_erase_of_mem hi]
  exact Nat.sub_lt (List.length_pos_of_mem hi) (by decide)

theorem disabling_not_local : ¬ LocallyConfluent disablingStep := by
  intro hl
  have ha : disablingStep [TwoItem.a, TwoItem.b] [TwoItem.b] :=
    ⟨TwoItem.a, by decide, (by intro h; cases h), by decide⟩
  have hb : disablingStep [TwoItem.a, TwoItem.b] [TwoItem.a] :=
    ⟨TwoItem.b, by decide, (by intro _; decide), by decide⟩
  obtain ⟨w, hw₁, hw₂⟩ := hl ha hb
  have hnormal : Normal disablingStep [TwoItem.b] := by
    intro t h
    obtain ⟨i, hi, hg, _⟩ := h
    cases i with
    | a => exact (by decide : TwoItem.a ∉ [TwoItem.b]) hi
    | b => exact (by decide : TwoItem.a ∉ [TwoItem.b]) (hg rfl)
  have hbeq : [TwoItem.b] = w := normal_star_eq hnormal hw₁
  -- The other route admits a, reaching the empty list.
  have hstep : disablingStep [TwoItem.a] [] :=
    ⟨TwoItem.a, by decide, (by intro h; cases h), by decide⟩
  have hjoin := hl hstep hstep
  have : Star disablingStep [TwoItem.a] [] := Star.single hstep
  -- Any descendant of [a] is [a] or []. Neither can be [b].
  cases hw₂ with
  | refl _ => cases hbeq
  | @cons _ mid _ he rest =>
    obtain ⟨i, hi, _, hm⟩ := he
    cases i with
    | a =>
      have hempty : mid = ([] : List TwoItem) := by simpa using hm
      subst mid
      have hn : Normal disablingStep [] := by
        intro t h
        obtain ⟨i, hi, _, _⟩ := h
        simp at hi
      have hw : ([] : List TwoItem) = w := normal_star_eq hn rest
      cases hbeq.trans hw.symm
    | b => exact (by decide : TwoItem.b ∉ [TwoItem.a]) hi

theorem disabling_two_fixed_points :
    Star disablingStep [TwoItem.a, TwoItem.b] [TwoItem.b] ∧
    Star disablingStep [TwoItem.a, TwoItem.b] [] ∧
    Normal disablingStep [TwoItem.b] ∧ Normal disablingStep [] ∧
    [TwoItem.b] ≠ ([] : List TwoItem) ∧
    [TwoItem.b].length ≠ ([] : List TwoItem).length := by
  have ha : disablingStep [TwoItem.a, TwoItem.b] [TwoItem.b] :=
    ⟨TwoItem.a, by decide, (by intro h; cases h), by decide⟩
  have hb : disablingStep [TwoItem.a, TwoItem.b] [TwoItem.a] :=
    ⟨TwoItem.b, by decide, (by intro _; decide), by decide⟩
  have hc : disablingStep [TwoItem.a] [] :=
    ⟨TwoItem.a, by decide, (by intro h; cases h), by decide⟩
  refine ⟨Star.single ha, Star.cons hb (Star.single hc), ?_, ?_, by decide, by decide⟩
  · intro t h
    obtain ⟨i, hi, hg, _⟩ := h
    cases i with
    | a => exact (by decide : TwoItem.a ∉ [TwoItem.b]) hi
    | b => exact (by decide : TwoItem.a ∉ [TwoItem.b]) (hg rfl)
  · intro t h
    obtain ⟨i, hi, _, _⟩ := h
    simp at hi

end FoundationsVII.Semantics
