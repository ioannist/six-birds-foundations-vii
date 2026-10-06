import FoundationsVII.Semantics.Rewriting

namespace FoundationsVII.Semantics

universe u v

/-- List order is precedence: requirements must be initially available or
produced by an earlier event. -/
structure EventSystem (Event : Type u) (Capability : Type v) where
  initial : Capability → Prop
  requires : Event → Capability → Prop
  produces : Event → Capability → Prop

inductive Lawful {Event : Type u} {Capability : Type v}
    (sys : EventSystem Event Capability) : List Event → Prop where
  | nil : Lawful sys []
  | snoc {prior : List Event} {event : Event} :
      Lawful sys prior →
      (∀ cap, sys.requires event cap →
        sys.initial cap ∨ ∃ source, source ∈ prior ∧ sys.produces source cap) →
      Lawful sys (prior ++ [event])

theorem sole_producer_join_absent {Event : Type u} {Capability : Type v}
    (sys : EventSystem Event Capability) (join : Event) (cap : Capability)
    (need : sys.requires join cap) (noExternal : ¬ sys.initial cap)
    (sole : ∀ event, sys.produces event cap → event = join)
    {run : List Event} (lawful : Lawful sys run) : join ∉ run := by
  induction lawful with
  | nil => simp
  | @snoc prior event hprior hready ih =>
      simp only [List.mem_append, List.mem_singleton]
      intro h
      rcases h with h | h
      · exact ih h
      · subst event
        rcases hready cap need with hinit | ⟨source, hsource, hproduces⟩
        · exact noExternal hinit
        · exact ih ((sole source hproduces) ▸ hsource)

def seededJoinSystem : EventSystem Unit Unit where
  initial := fun _ => True
  requires := fun _ _ => True
  produces := fun _ _ => True

theorem external_source_allows_join : Lawful seededJoinSystem [()] := by
  simpa using (Lawful.snoc (sys := seededJoinSystem) Lawful.nil
    (fun _ _ => Or.inl True.intro))

theorem external_source_join_occurs : () ∈ ([()] : List Unit) := by simp

end FoundationsVII.Semantics
