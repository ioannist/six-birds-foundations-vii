import FoundationsVII.Join.Strictness

namespace FoundationsVII.Semantics

universe u

inductive Star {α : Type u} (step : α → α → Prop) : α → α → Prop where
  | refl (x : α) : Star step x x
  | cons {x y z : α} : step x y → Star step y z → Star step x z

namespace Star

theorem single {α : Type u} {r : α → α → Prop} {x y : α} (h : r x y) :
    Star r x y := cons h (refl y)

theorem trans {α : Type u} {r : α → α → Prop} {x y z : α}
    (h : Star r x y) (k : Star r y z) : Star r x z := by
  induction h with
  | refl _ => exact k
  | cons e _ ih => exact cons e (ih k)

end Star

def Joinable {α : Type u} (r : α → α → Prop) (x y : α) : Prop :=
  ∃ z, Star r x z ∧ Star r y z

def LocallyConfluent {α : Type u} (r : α → α → Prop) : Prop :=
  ∀ ⦃x y z⦄, r x y → r x z → Joinable r y z

def Confluent {α : Type u} (r : α → α → Prop) : Prop :=
  ∀ ⦃x y z⦄, Star r x y → Star r x z → Joinable r y z

def Terminates {α : Type u} (r : α → α → Prop) : Prop :=
  WellFounded (fun y x => r x y)

def Normal {α : Type u} (r : α → α → Prop) (x : α) : Prop :=
  ∀ y, ¬ r x y

private theorem join_of_stars {α : Type u} {r : α → α → Prop}
    (hloc : LocallyConfluent r) (wf : Terminates r) :
    ∀ x, ∀ ⦃y z⦄, Star r x y → Star r x z → Joinable r y z := by
  intro x
  induction x using wf.induction with
  | h x ih =>
    intro y z hy hz
    cases hy with
    | refl _ => exact ⟨z, hz, Star.refl z⟩
    | @cons _ a y hxa hay =>
      cases hz with
      | refl _ => exact ⟨y, Star.refl y, Star.cons hxa hay⟩
      | @cons _ b z hxb hbz =>
        obtain ⟨w, haw, hbw⟩ := hloc hxa hxb
        obtain ⟨v, hayv, hawv⟩ := ih a hxa hay haw
        obtain ⟨t, hbzt, hbwt⟩ := ih b hxb hbz hbw
        obtain ⟨s, hvs, hts⟩ := ih a hxa
          (Star.trans haw hawv) (Star.trans haw hbwt)
        exact ⟨s, Star.trans hayv hvs, Star.trans hbzt hts⟩

theorem newman {α : Type u} {r : α → α → Prop}
    (termination : Terminates r) (hloc : LocallyConfluent r) : Confluent r :=
  by intro x y z hx hy; exact join_of_stars hloc termination x hx hy

theorem normal_star_eq {α : Type u} {r : α → α → Prop} {x y : α}
    (hn : Normal r x) (h : Star r x y) : x = y := by
  cases h with
  | refl _ => rfl
  | cons e _ => exact False.elim (hn _ e)

theorem normal_forms_unique {α : Type u} {r : α → α → Prop}
    (confluence : Confluent r)
    {x y z : α} (hy : Star r x y) (hz : Star r x z)
    (ny : Normal r y) (nz : Normal r z) : y = z := by
  obtain ⟨w, hyw, hzw⟩ := confluence hy hz
  exact (normal_star_eq ny hyw).trans (normal_star_eq nz hzw).symm

private theorem reaches_normal {α : Type u} {r : α → α → Prop}
    (wf : Terminates r) : ∀ x, ∃ y, Star r x y ∧ Normal r y := by
  intro x
  induction x using wf.induction with
  | h x ih =>
    by_cases h : ∃ y, r x y
    · obtain ⟨y, hxy⟩ := h
      obtain ⟨z, hyz, hn⟩ := ih y hxy
      exact ⟨z, Star.cons hxy hyz, hn⟩
    · exact ⟨x, Star.refl x, fun y hxy => h ⟨y, hxy⟩⟩

theorem unique_reachable_normal {α : Type u} {r : α → α → Prop}
    (termination : Terminates r) (confluence : Confluent r) (x : α) :
    ∃ y, Star r x y ∧ Normal r y ∧
      ∀ z, Star r x z → Normal r z → z = y := by
  obtain ⟨y, hy, ny⟩ := reaches_normal termination x
  exact ⟨y, hy, ny, fun z hz nz => normal_forms_unique confluence hz hy nz ny⟩

-- Enumerating all sublists gives a finite (possibly exponential) search over
-- candidate closed sets. Duplicate entries in `all` are harmless.
def allSubsets {α : Type u} : List α → List (List α)
  | [] => [[]]
  | a :: as =>
    let ss := allSubsets as
    ss ++ ss.map (a :: ·)

theorem filter_mem_allSubsets {α : Type u} (p : α → Bool) (all : List α) :
    all.filter p ∈ allSubsets all := by
  induction all with
  | nil => simp [allSubsets]
  | cons a as ih =>
    cases h : p a
    · simp [allSubsets, h, ih]
    · simp [allSubsets, h, ih]

def finiteClosedCheck {α : Type u} [DecidableEq α]
    (all : List α) (r : α → α → Prop) [DecidableRel r]
    (s : List α) : Bool :=
  s.all fun a => all.all fun b => decide (r a b → b ∈ s)

theorem finiteClosedCheck_correct {α : Type u} [DecidableEq α]
    (all : List α) (r : α → α → Prop) [DecidableRel r] (s : List α) :
    finiteClosedCheck all r s = true ↔
      ∀ a, a ∈ s → ∀ b, b ∈ all → r a b → b ∈ s := by
  simp only [finiteClosedCheck, List.all_eq_true, decide_eq_true_eq]

def finiteReachCheck {α : Type u} [DecidableEq α]
    (all : List α) (r : α → α → Prop) [DecidableRel r]
    (x y : α) : Bool :=
  (allSubsets all).all fun s =>
    if decide (x ∈ s) && finiteClosedCheck all r s then
      decide (y ∈ s)
    else true

theorem finiteReachCheck_correct {α : Type u} [DecidableEq α]
    (all : List α) (covers : ∀ a, a ∈ all)
    (r : α → α → Prop) [DecidableRel r] (x y : α) :
    finiteReachCheck all r x y = true ↔ Star r x y := by
  constructor
  · intro h
    classical
    let reachable : List α := all.filter (fun z => decide (Star r x z))
    have hsub : reachable ∈ allSubsets all := filter_mem_allSubsets _ _
    have hx : x ∈ reachable := by
      simp [reachable, covers x, Star.refl]
    have hclosed : finiteClosedCheck all r reachable = true := by
      apply (finiteClosedCheck_correct all r reachable).2
      intro a ha b _ hab
      have hxa : Star r x a := by
        have hmem := (List.mem_filter.mp ha).2
        exact of_decide_eq_true hmem
      apply List.mem_filter.mpr
      exact ⟨covers b, decide_eq_true (Star.trans hxa (Star.single hab))⟩
    have hval := (List.all_eq_true.mp h) reachable hsub
    have hy : y ∈ reachable := by
      simpa [finiteReachCheck, hx, hclosed] using hval
    exact of_decide_eq_true (List.mem_filter.mp hy).2
  · intro h
    apply List.all_eq_true.mpr
    intro s _
    by_cases hx : x ∈ s
    · by_cases hc : finiteClosedCheck all r s = true
      · have hclosure := (finiteClosedCheck_correct all r s).1 hc
        have hy : y ∈ s := by
          induction h with
          | refl _ => exact hx
          | @cons a b c hab _ ih =>
            -- The induction hypothesis needs the successor in s.
            exact ih (hclosure a hx b (covers b) hab)
        simp [hx, hc, hy]
      · simp [hx, hc]
    · simp [hx]

-- A finite peak scan. A constructive reachability decider is an explicit
-- parameter; decidability of one-step edges alone does not supply it here.
def finitePeakCheck {α : Type u} (all : List α) (r : α → α → Prop)
    [DecidableRel r] (joinDecision : ∀ y z, Decidable (Joinable r y z)) : Bool :=
  all.all fun x => all.all fun y => all.all fun z =>
    letI : Decidable (Joinable r y z) := joinDecision y z
    decide (r x y → r x z → Joinable r y z)

theorem finitePeakCheck_correct {α : Type u} (all : List α)
    (covers : ∀ x, x ∈ all) (r : α → α → Prop)
    [DecidableRel r] (joinDecision : ∀ y z, Decidable (Joinable r y z)) :
    finitePeakCheck all r joinDecision = true ↔ LocallyConfluent r := by
  simp only [finitePeakCheck, List.all_eq_true]
  constructor
  · intro h x y z hxy hxz
    have hx := h x (covers x) y (covers y) z (covers z)
    exact (of_decide_eq_true hx) hxy hxz
  · intro h x _ y _ z _
    exact decide_eq_true (h (x := x) (y := y) (z := z))

def finiteJoinCheck {α : Type u} [DecidableEq α]
    (all : List α) (r : α → α → Prop) [DecidableRel r]
    (x y : α) : Bool :=
  all.any fun z => finiteReachCheck all r x z && finiteReachCheck all r y z

theorem finiteJoinCheck_correct {α : Type u} [DecidableEq α]
    (all : List α) (covers : ∀ a, a ∈ all)
    (r : α → α → Prop) [DecidableRel r] (x y : α) :
    finiteJoinCheck all r x y = true ↔ Joinable r x y := by
  simp only [finiteJoinCheck, List.any_eq_true, Bool.and_eq_true,
    finiteReachCheck_correct all covers r]
  constructor
  · rintro ⟨z, _, hx, hy⟩
    exact ⟨z, hx, hy⟩
  · rintro ⟨z, hx, hy⟩
    exact ⟨z, covers z, hx, hy⟩

def finiteJoinDecision {α : Type u} [DecidableEq α]
    (all : List α) (covers : ∀ a, a ∈ all)
    (r : α → α → Prop) [DecidableRel r] (x y : α) :
    Decidable (Joinable r x y) :=
  if h : finiteJoinCheck all r x y = true then
    isTrue ((finiteJoinCheck_correct all covers r x y).1 h)
  else
    isFalse (fun hj => h ((finiteJoinCheck_correct all covers r x y).2 hj))

def finitePeakCheckComplete {α : Type u} [DecidableEq α]
    (all : List α) (covers : ∀ a, a ∈ all)
    (r : α → α → Prop) [DecidableRel r] : Bool :=
  finitePeakCheck all r (finiteJoinDecision all covers r)

theorem finitePeakCheckComplete_correct {α : Type u} [DecidableEq α]
    (all : List α) (covers : ∀ a, a ∈ all)
    (r : α → α → Prop) [DecidableRel r] :
    finitePeakCheckComplete all covers r = true ↔ LocallyConfluent r :=
  finitePeakCheck_correct all covers r (finiteJoinDecision all covers r)

def finitePeakCheckFin (n : Nat) (r : Fin n → Fin n → Prop)
    [DecidableRel r] : Bool :=
  finitePeakCheckComplete (List.finRange n) List.mem_finRange r

theorem finitePeakCheckFin_correct (n : Nat) (r : Fin n → Fin n → Prop)
    [DecidableRel r] :
    finitePeakCheckFin n r = true ↔ LocallyConfluent r :=
  finitePeakCheckComplete_correct (List.finRange n) List.mem_finRange r

inductive Four where | a | b | c | d
  deriving DecidableEq, Repr

def fourStep : Four → Four → Prop
  | .b, .a => True
  | .b, .c => True
  | .c, .b => True
  | .c, .d => True
  | _, _ => False

instance : DecidableRel fourStep := fun x y => by cases x <;> cases y <;> unfold fourStep <;> infer_instance

theorem four_local : LocallyConfluent fourStep := by
  intro x y z hxy hxz
  cases x <;> cases y <;> cases z <;> simp [fourStep] at hxy hxz
  all_goals try exact ⟨_, Star.refl _, Star.refl _⟩
  all_goals try exact ⟨_, Star.refl _, Star.single trivial⟩
  all_goals try exact ⟨_, Star.single trivial, Star.refl _⟩
  case b.a.c => exact ⟨Four.a, Star.refl _, Star.cons (show fourStep Four.c Four.b from trivial) (Star.single (show fourStep Four.b Four.a from trivial))⟩
  case b.c.a => exact ⟨Four.a, Star.cons (show fourStep Four.c Four.b from trivial) (Star.single (show fourStep Four.b Four.a from trivial)), Star.refl _⟩
  case c.b.d => exact ⟨Four.d, Star.cons (show fourStep Four.b Four.c from trivial) (Star.single (show fourStep Four.c Four.d from trivial)), Star.refl _⟩
  case c.d.b => exact ⟨Four.d, Star.refl _, Star.cons (show fourStep Four.b Four.c from trivial) (Star.single (show fourStep Four.c Four.d from trivial))⟩

theorem four_not_confluent : ¬ Confluent fourStep := by
  intro hc
  obtain ⟨w, haw, hdw⟩ := hc
    (Star.single (show fourStep Four.b Four.a from trivial))
    (Star.cons (show fourStep Four.b Four.c from trivial)
      (Star.single (show fourStep Four.c Four.d from trivial)))
  have ha : Four.a = w := normal_star_eq (by intro t h; cases t <;> simp [fourStep] at h) haw
  have hd : Four.d = w := normal_star_eq (by intro t h; cases t <;> simp [fourStep] at h) hdw
  cases ha.trans hd.symm

end FoundationsVII.Semantics
