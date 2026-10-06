import FoundationsVII.Join.Strictness

namespace FoundationsVII.Semantics

universe u v w t x

structure TheoryPackage (X : Type v) where
  Carrier : Type u
  observe : Carrier → X

structure SemanticJoin (A : Type u) (B : Type v) (J : Type w) where
  pA : J → A
  pB : J → B

structure PackageJoin {XA : Type v} {XB : Type w}
    (A : TheoryPackage XA) (B : TheoryPackage XB) where
  Carrier : Type u
  pA : Carrier → A.Carrier
  pB : Carrier → B.Carrier

def Factors {J : Type u} {Y : Type v} {X : Type w}
    (q : J → Y) (f : J → X) : Prop :=
  ∃ g : Y → X, ∀ j, f j = g (q j)

-- The image subtype avoids requiring an arbitrary default value of X.
def FactorsOnImage {J : Type u} {Y : Type v} {X : Type w}
    (q : J → Y) (f : J → X) : Prop :=
  ∃ g : {y : Y // ∃ j, q j = y} → X,
    ∀ j, f j = g ⟨q j, j, rfl⟩

theorem factors_implies_onImage {J : Type u} {Y : Type v} {X : Type w}
    {q : J → Y} {f : J → X} (h : Factors q f) : FactorsOnImage q f := by
  obtain ⟨g, hg⟩ := h
  exact ⟨fun y => g y.1, hg⟩

def SplitPair {J : Type u} {Y : Type v} {X : Type w}
    (q : J → Y) (f : J → X) : Prop :=
  ∃ j k, q j = q k ∧ f j ≠ f k

theorem factorsOnImage_iff_no_split {J : Type u} {Y : Type v} {X : Type w}
    (q : J → Y) (f : J → X) :
    FactorsOnImage q f ↔ ¬ SplitPair q f := by
  classical
  constructor
  · rintro ⟨g, hg⟩ ⟨j, k, hq, hf⟩
    apply hf
    calc
      f j = g ⟨q j, j, rfl⟩ := hg j
      _ = g ⟨q k, k, rfl⟩ := by congr 1; exact Subtype.ext hq
      _ = f k := (hg k).symm
  · intro h
    have hconst : ∀ j k, q j = q k → f j = f k := by
      intro j k hq
      exact Classical.byContradiction (fun hf => h ⟨j, k, hq, hf⟩)
    let g : {y : Y // ∃ j, q j = y} → X :=
      fun y => f (Classical.choose y.property)
    refine ⟨g, ?_⟩
    intro j
    exact hconst j (Classical.choose (show ∃ k, q k = q j from ⟨j, rfl⟩))
      (Classical.choose_spec (show ∃ k, q k = q j from ⟨j, rfl⟩)).symm

-- The list covers the carrier; only finitely many q-fibres need inspection.
def FiniteSplitCheck {J : Type u} {Y : Type v} {X : Type w}
    [DecidableEq Y] [DecidableEq X] (all : List J) (q : J → Y) (f : J → X) : Bool :=
  all.any fun j => all.any fun k => decide (q j = q k ∧ f j ≠ f k)

theorem finiteSplitCheck_correct {J : Type u} {Y : Type v} {X : Type w}
    [DecidableEq Y] [DecidableEq X] (all : List J)
    (covers : ∀ j, j ∈ all) (q : J → Y) (f : J → X) :
    FiniteSplitCheck all q f = true ↔ SplitPair q f := by
  simp only [FiniteSplitCheck, List.any_eq_true, decide_eq_true_eq]
  constructor
  · rintro ⟨j, _, k, _, h⟩
    exact ⟨j, k, h⟩
  · rintro ⟨j, k, h⟩
    exact ⟨j, covers j, k, covers k, h⟩

-- A refinement retains the pair of parental observations.
def CommonRefinement {J : Type u} {A : Type v} {B : Type w} {R : Type t}
    (pA : J → A) (pB : J → B) (q : J → R) : Prop :=
  ∃ h : R → A × B, ∀ j, h (q j) = (pA j, pB j)

theorem factors_through_pair_of_refinement {J : Type u} {A : Type v}
    {B : Type w} {R : Type t} {X : Type u}
    (pA : J → A) (pB : J → B) (q : J → R) (f : J → X)
    (refines : CommonRefinement pA pB q)
    (h : Factors (fun j => (pA j, pB j)) f) :
    Factors q f := by
  obtain ⟨map, hmap⟩ := refines
  obtain ⟨g, hg⟩ := h
  exact ⟨g ∘ map, fun j => by simp [Function.comp, hg j, hmap j]⟩

def StrictObservable {J : Type u} {A : Type v} {B : Type w} {X : Type t}
    (join : SemanticJoin A B J) (f : J → X) : Prop :=
  ¬ FactorsOnImage join.pA f ∧
  ¬ FactorsOnImage join.pB f ∧
  ¬ FactorsOnImage (fun j => (join.pA j, join.pB j)) f

theorem strict_iff_split_pairs {J : Type u} {A : Type v} {B : Type w} {X : Type t}
    (join : SemanticJoin A B J) (f : J → X) :
    StrictObservable join f ↔
      SplitPair join.pA f ∧ SplitPair join.pB f ∧
      SplitPair (fun j => (join.pA j, join.pB j)) f := by
  classical
  simp [StrictObservable, factorsOnImage_iff_no_split]

def cubeJoin : SemanticJoin Bool Bool (Bool × Bool × Bool) :=
  ⟨fun j => j.1, fun j => j.2.1⟩

def cubeObservable (j : Bool × Bool × Bool) : Bool := j.2.2

def boolPackage : TheoryPackage Bool :=
  { Carrier := Bool, observe := id }

def cubePackageJoin : PackageJoin boolPackage boolPackage :=
  { Carrier := Bool × Bool × Bool,
    pA := fun j => j.1, pB := fun j => j.2.1 }

theorem cube_strict : StrictObservable cubeJoin cubeObservable := by
  apply (strict_iff_split_pairs _ _).2
  refine ⟨?_, ?_, ?_⟩
  all_goals exact ⟨(false, false, false), (false, false, true), rfl, by decide⟩

theorem cube_first_not_strict :
    ¬ StrictObservable cubeJoin (fun j => j.1) := by
  intro h
  have hs := (strict_iff_split_pairs _ _).1 h |>.1
  obtain ⟨j, k, hjk, hdiff⟩ := hs
  exact hdiff hjk

theorem identity_refinement_recovers_cube :
    CommonRefinement cubeJoin.pA cubeJoin.pB (fun j => j) ∧
    FactorsOnImage (fun j : Bool × Bool × Bool => j) cubeObservable := by
  constructor
  · exact ⟨fun j => (j.1, j.2.1), fun _ => rfl⟩
  · exact ⟨fun y => cubeObservable y.1, fun _ => rfl⟩

-- These predicates make the three presentation flags model-relative. A
-- schedule coordinate must be explicitly declared; strictness alone does not
-- forbid factoring through an arbitrary new coordinate (e.g. identity on J).
def RelabelOnly {J : Type u} {A : Type v} {B : Type w} {X : Type t}
    (join : SemanticJoin A B J) (f : J → X) : Prop :=
  ∃ h : A × B → A × B, (Function.Injective h ∧ Function.Surjective h) ∧
    FactorsOnImage (fun j => h (join.pA j, join.pB j)) f

def SchedulingOnly {J : Type u} {S : Type v} {X : Type w}
    (schedule : J → S) (f : J → X) : Prop :=
  FactorsOnImage schedule f

def CoarseningOnly {J : Type u} {A : Type v} {B : Type w} {X : Type t}
    (join : SemanticJoin A B J) (f : J → X) : Prop :=
  (∃ (C : Type v) (c : A → C),
    FactorsOnImage (fun j => c (join.pA j)) f) ∨
  (∃ (C : Type w) (c : B → C),
    FactorsOnImage (fun j => c (join.pB j)) f)

theorem split_composition {J : Type u} {Y : Type v} {Z : Type w} {X : Type t}
    {q : J → Y} {f : J → X} (h : SplitPair q f) (c : Y → Z) :
    SplitPair (fun j => c (q j)) f := by
  obtain ⟨j, k, hq, hf⟩ := h
  exact ⟨j, k, congrArg c hq, hf⟩

theorem strict_not_relabel {J : Type u} {A : Type v} {B : Type w} {X : Type t}
    {join : SemanticJoin A B J} {f : J → X}
    (hs : StrictObservable join f) : ¬ RelabelOnly join f := by
  intro hr
  obtain ⟨h, _, hh⟩ := hr
  have split := (strict_iff_split_pairs join f).1 hs |>.2.2
  exact (factorsOnImage_iff_no_split _ _).1 hh (split_composition split h)

theorem strict_not_coarsening {J : Type u} {A : Type v} {B : Type w} {X : Type t}
    {join : SemanticJoin A B J} {f : J → X}
    (hs : StrictObservable join f) : ¬ CoarseningOnly join f := by
  intro hc
  obtain ⟨C, c, hf⟩ | ⟨C, c, hf⟩ := hc
  · have split := (strict_iff_split_pairs join f).1 hs |>.1
    exact (factorsOnImage_iff_no_split _ _).1 hf (split_composition split c)
  · have split := (strict_iff_split_pairs join f).1 hs |>.2.1
    exact (factorsOnImage_iff_no_split _ _).1 hf (split_composition split c)

noncomputable def semanticFlag (p : Prop) : Bool :=
  @decide p (Classical.propDecidable p)

theorem semanticFlag_true {p : Prop} (hp : p) : semanticFlag p = true := by
  simp [semanticFlag, hp]

theorem semanticFlag_false {p : Prop} (hp : ¬ p) : semanticFlag p = false := by
  simp [semanticFlag, hp]

structure SemanticStrictEvidence {J : Type u} {A : Type v} {B : Type w}
    {X : Type t} {R : Type x} {S : Type x}
    (join : SemanticJoin A B J) (f : J → X) (q : J → R)
    (schedule : J → S) : Prop where
  refines : CommonRefinement join.pA join.pB q
  strict : StrictObservable join f
  refinementNonfactor : ¬ FactorsOnImage q f
  scheduleNonfactor : ¬ SchedulingOnly schedule f

-- Each Boolean is evaluated from its declared semantic predicate. The
-- certificate is noncomputable when those predicates lack a decider.
noncomputable def strictCertificate {J : Type u} {A : Type v} {B : Type w}
    {X : Type t} {R : Type x} {S : Type x}
    (join : SemanticJoin A B J) (f : J → X) (q : J → R)
    (schedule : J → S)
    (_evidence : SemanticStrictEvidence join f q schedule) : AntiProductWitness :=
  { jointDistinctionPresent := semanticFlag
      (SplitPair (fun j => (join.pA j, join.pB j)) f)
    factorsThroughLeft := semanticFlag (FactorsOnImage join.pA f)
    factorsThroughRight := semanticFlag (FactorsOnImage join.pB f)
    factorsThroughDeclaredProduct := semanticFlag
      (FactorsOnImage (fun j => (join.pA j, join.pB j)) f)
    factorsThroughCommonRefinement := semanticFlag (FactorsOnImage q f)
    relabelOnly := semanticFlag (RelabelOnly join f)
    schedulingOnly := semanticFlag (SchedulingOnly schedule f)
    coarseningOnly := semanticFlag (CoarseningOnly join f)
    witnessDescription := "semantic split pairs for parents, pairing, and declared refinement"
    audit := { entries := [
      { auditId := 0, disposition := .accepted,
        subject := "semantic strict join", message := "semantic predicates evaluated",
        sourceLocation := "FoundationsVII.Semantics.Join" } ] } }

theorem strictCertificate_valid {J : Type u} {A : Type v} {B : Type w}
    {X : Type t} {R : Type x} {S : Type x}
    (join : SemanticJoin A B J) (f : J → X) (q : J → R)
    (schedule : J → S)
    (evidence : SemanticStrictEvidence join f q schedule) :
    AntiProductWitness.Valid (strictCertificate join f q schedule evidence) := by
  have hsplit := (strict_iff_split_pairs join f).1 evidence.strict |>.2.2
  have hRelabel := strict_not_relabel evidence.strict
  have hCoarsening := strict_not_coarsening evidence.strict
  unfold AntiProductWitness.Valid strictCertificate
  simp [semanticFlag_true hsplit, semanticFlag_false evidence.strict.1,
    semanticFlag_false evidence.strict.2.1,
    semanticFlag_false evidence.strict.2.2,
    semanticFlag_false evidence.refinementNonfactor,
    semanticFlag_false hRelabel,
    semanticFlag_false evidence.scheduleNonfactor,
    semanticFlag_false hCoarsening]

private theorem cubeEvidence : SemanticStrictEvidence cubeJoin cubeObservable
    (fun j => (cubeJoin.pA j, cubeJoin.pB j)) cubeJoin.pA := by
  exact ⟨⟨id, fun _ => rfl⟩, cube_strict, cube_strict.2.2, cube_strict.1⟩

theorem cubeCertificate_valid :
    AntiProductWitness.Valid
      (strictCertificate cubeJoin cubeObservable
        (fun j => (cubeJoin.pA j, cubeJoin.pB j)) cubeJoin.pA cubeEvidence) :=
  strictCertificate_valid _ _ _ _ cubeEvidence

end FoundationsVII.Semantics
