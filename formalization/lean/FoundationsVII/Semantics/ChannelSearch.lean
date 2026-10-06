import FoundationsVII.Semantics.Search

namespace FoundationsVII.Semantics

/-- One channel use advances exactly one side by one genuine theory step. -/
def leftStep (a a' : Bool) : Prop := a = false ∧ a' = true
def rightStep (b b' : Bool) : Prop := b = false ∧ b' = true

def channelStep (p q : Bool × Bool) : Prop :=
  (leftStep p.1 q.1 ∧ p.2 = q.2) ∨
  (p.1 = q.1 ∧ rightStep p.2 q.2)

def channelRelated (p : Bool × Bool) : Prop := p.1 = true ∧ p.2 = true

def ContactWithin (budget : Nat) : Prop :=
  ∃ p, ReachWithin channelStep (false, false) budget p ∧ channelRelated p

instance : DecidablePred channelRelated := by
  intro p
  unfold channelRelated
  infer_instance

theorem zero_channel_reach_eq {start p : Bool × Bool}
    (h : ReachWithin channelStep start 0 p) : p = start := by
  cases h with
  | zero => rfl

theorem one_channel_coverage (p : Bool × Bool)
    (h : ReachWithin channelStep (false, false) 1 p) :
    p ∈ [(false, false), (true, false), (false, true)] := by
  cases h with
  | zero => simp
  | @next _ x y prev step =>
      have hx := zero_channel_reach_eq prev
      subst x
      rcases step with ⟨hl, heq⟩ | ⟨heq, hr⟩
      · cases p with
        | mk a b => cases a <;> cases b <;> simp_all [leftStep]
      · cases p with
        | mk a b => cases a <;> cases b <;> simp_all [rightStep]
  | weaken prev =>
      have hp := zero_channel_reach_eq prev
      subst p
      simp

theorem one_channel_negative_scan :
    detect [(false, false), (true, false), (false, true)] channelRelated = false := by
  decide

theorem no_contact_with_one_use : ¬ ContactWithin 1 := by
  exact no_contact_in_covered_family one_channel_coverage one_channel_negative_scan

theorem two_channel_uses_reach_contact :
    ReachWithin channelStep (false, false) 2 (true, true) := by
  exact ReachWithin.next
    (ReachWithin.next (ReachWithin.zero)
      (show channelStep (false, false) (true, false) from
        Or.inl ⟨⟨rfl, rfl⟩, rfl⟩))
    (show channelStep (true, false) (true, true) from
      Or.inr ⟨rfl, ⟨rfl, rfl⟩⟩)

theorem contact_with_two_uses : ContactWithin 2 := by
  exact ⟨(true, true), two_channel_uses_reach_contact, ⟨rfl, rfl⟩⟩

end FoundationsVII.Semantics
