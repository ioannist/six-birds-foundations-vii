import HolonomyMemory.Witnesses
import HolonomyMemory.Asymmetry

namespace HolonomyMemory

namespace Wheel

abbrev WheelHistory := Bool × Bool

structure WheelMap where
  atFalseFalse : WheelHistory
  atFalseTrue : WheelHistory
  atTrueFalse : WheelHistory
  atTrueTrue : WheelHistory
deriving DecidableEq

def WheelMap.apply (f : WheelMap) : WheelHistory → WheelHistory
  | (false, false) => f.atFalseFalse
  | (false, true) => f.atFalseTrue
  | (true, false) => f.atTrueFalse
  | (true, true) => f.atTrueTrue

def WheelMap.identity : WheelMap :=
  ⟨(false, false), (false, true), (true, false), (true, true)⟩

def WheelMap.comp (f g : WheelMap) : WheelMap :=
  ⟨g.apply f.atFalseFalse, g.apply f.atFalseTrue,
    g.apply f.atTrueFalse, g.apply f.atTrueTrue⟩

/-- A finite memory wheel. The first history bit is currently visible; the
second is latent memory. A continuation is an explicit four-entry transition
table, so all carrier types have decidable equality. -/
def wheel : RouteTransportCore where
  Interface := Unit
  History := fun _ => WheelHistory
  Continuation := fun _ _ => WheelMap
  Event := fun _ => Unit
  Observation := Bool
  idCont := WheelMap.identity
  compose := WheelMap.comp
  push := fun h γ => γ.apply h
  observe := fun h _ => h.1
  push_id := by
    intro i h
    rcases h with ⟨v, m⟩
    cases v <;> cases m <;> rfl
  push_compose := by
    intro i j k h γ δ
    rcases h with ⟨v, m⟩
    cases v <;> cases m <;> rfl

def i₀ : wheel.Interface := ()

/-- Flip latent memory while leaving the currently visible bit fixed. -/
def ℓ₀ : Loop wheel i₀ :=
  ⟨(false, true), (false, false), (true, true), (true, false)⟩

/-- Reveal latent memory in the visible coordinate. -/
def reveal : wheel.Continuation i₀ i₀ :=
  ⟨(false, false), (true, true), (false, false), (true, true)⟩

def wheelWitness : PredictiveWitness wheel i₀ where
  h := (false, false)
  h' := (false, true)
  sameCurrent := by intro e; rfl
  notSameFuture := by
    intro hFuture
    have := hFuture reveal ()
    contradiction

theorem wheel_strictRefinement : StrictRefinement wheel i₀ :=
  wheelWitness.induces_strictRefinement wheel

theorem wheel_distinctPredictive_sameCurrent :
    let q : PredictiveQuotient wheel i₀ :=
      Quotient.mk (PredictiveSetoid wheel i₀) wheelWitness.h
    let q' : PredictiveQuotient wheel i₀ :=
      Quotient.mk (PredictiveSetoid wheel i₀) wheelWitness.h'
    q ≠ q' ∧ predictiveToCurrent wheel q = predictiveToCurrent wheel q' :=
  wheelWitness.distinct_predictive_classes_same_current_class wheel

theorem wheel_witnessFromStrict : Nonempty (PredictiveWitness wheel i₀) :=
  strictRefinement_implies_predictiveWitness wheel wheel_strictRefinement

theorem wheel_strictRefinement_iff_witness :
    StrictRefinement wheel i₀ ↔ Nonempty (PredictiveWitness wheel i₀) :=
  strictRefinement_iff_nonempty_predictiveWitness wheel i₀

theorem wheel_currentLoopTrivial : CurrentLoopTrivial wheel i₀ ℓ₀ := by
  intro h e
  rcases h with ⟨v, m⟩
  cases v <;> cases m <;> rfl

theorem wheel_predictiveLoopNontrivial :
    PredictiveLoopNontrivial wheel i₀ ℓ₀ := by
  refine ⟨Quotient.mk (PredictiveSetoid wheel i₀) (false, false), ?_⟩
  intro hEq
  have hEq' :
      Quotient.mk (PredictiveSetoid wheel i₀) (wheel.push (false, false) ℓ₀) =
        Quotient.mk (PredictiveSetoid wheel i₀) (false, false) := by
    simpa using hEq
  have hFuture :
      FuturePredictiveEquiv wheel (wheel.push (false, false) ℓ₀) (false, false) :=
    Quotient.exact hEq'
  have hObserved := hFuture reveal ()
  contradiction

theorem wheel_loopAsymmetry : LoopAsymmetry wheel i₀ ℓ₀ :=
  ⟨wheel_currentLoopTrivial, wheel_predictiveLoopNontrivial⟩

/-- The generic witness-extraction theorem is exercised by the finite wheel. -/
theorem wheel_movedPredictive_fixedCurrent :
    ∃ q : PredictiveQuotient wheel i₀,
      predictiveLoopAction wheel ℓ₀ q ≠ q ∧
      predictiveToCurrent wheel (predictiveLoopAction wheel ℓ₀ q) =
        predictiveToCurrent wheel q :=
  loopAsymmetry_exhibits_movedPredictive_fixedCurrent wheel ℓ₀ wheel_loopAsymmetry

theorem wheel_movedPredictive_currentFixed :
    ∃ q : PredictiveQuotient wheel i₀,
      predictiveLoopAction wheel ℓ₀ q ≠ q ∧
      predictiveToCurrent wheel (predictiveLoopAction wheel ℓ₀ q) =
        predictiveToCurrent wheel q :=
  loopAsymmetry_exhibits_movedPredictive_currentFixed wheel ℓ₀ wheel_loopAsymmetry

#print axioms wheelWitness
#print axioms wheel_strictRefinement
#print axioms wheel_loopAsymmetry
#print axioms wheel_movedPredictive_fixedCurrent

end Wheel

end HolonomyMemory
