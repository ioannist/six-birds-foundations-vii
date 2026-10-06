import SixBirdsMetaMath.FoundationsIV.Access.NoFreeDistinction

/-!
F13a Hiddenness theorem-grade quotient/currentizer normal form.

This file records the theorem-grade layer only. The CSL formed-closure law is
F13b. The actual saturated-SAT substrate from Paper 7 has no Lean code in this
repository, so the Paper 7 claim is represented by the narrow
`substrate_pending` axiom `hiddenness_pending`.
-/

namespace SixBirdsMetaMath.FoundationsIV.Access.HiddennessNormalForm

open SixBirdsMetaMath.FoundationsIV.Stability.SufficiencyClosure

/-- Paper 7's saturated SAT layer, unavailable as Lean substrate in this repo. -/
opaque Paper7SaturatedSATLayer : Type

/-- Paper 7 current-access quotient carrier. -/
opaque Paper7CurrentQuotient : Type

/-- Paper 7 predictive quotient carrier. -/
opaque Paper7PredictiveQuotient : Type

/-- Paper 7 upstream determining-state signature carrier. -/
opaque Paper7UpstreamState : Type

/-- Layer-agnostic quotient/currentizer data for the theorem-grade hiddenness
normal form. -/
structure HiddennessInterface where
  Hist : Type
  Current : Type
  Predictive : Type
  Upstream : Type
  current : Hist → Current
  predictive : Hist → Predictive
  upstream : Hist → Upstream
  forgetPredictive : Predictive → Current
  predictive_refines_current : forgetPredictive ∘ predictive = current
  determiningStateTyped : Prop
  minimalRelevantUpstream : Prop
  lawfulCurrentExposure : Prop

/-- The upstream determining signature descends to current access. -/
def QuotientExposed (I : HiddennessInterface) : Prop :=
  FactorsThroughQ I.current I.upstream

/-- The determining state is hidden from current observation. -/
def HiddenFromCurrent (I : HiddennessInterface) : Prop :=
  ¬ I.lawfulCurrentExposure

/-- The predictive quotient collapses to the current quotient: since `current`
already factors through `predictive`, this is the missing reverse descent. -/
def PredictiveCollapse (I : HiddennessInterface) : Prop :=
  FactorsThroughQ I.current I.predictive

/-- A surviving predictive surplus is a same-current / different-predictive
split pair. -/
def PredictiveSurplus (I : HiddennessInterface) : Prop :=
  ∃ x y : I.Hist, I.current x = I.current y ∧ I.predictive x ≠ I.predictive y

/-- The theorem-grade hiddenness normal-form content, separated from the later
CSL formed-closure law. -/
def HiddennessNormalForm (I : HiddennessInterface) : Prop :=
  I.determiningStateTyped ∧ I.minimalRelevantUpstream ∧
    (I.lawfulCurrentExposure ↔ QuotientExposed I) ∧
      (PredictiveCollapse I ↔ I.lawfulCurrentExposure) ∧
        (PredictiveSurplus I ↔ HiddenFromCurrent I)

/-- Opaque certificate that a hiddenness interface is the Paper 7 saturated SAT
instance. This prevents the pending substrate axiom from applying to arbitrary
interfaces without an explicit Paper 7 certificate. -/
opaque Paper7SaturatedSATInstance : HiddennessInterface → Prop

/--
# substrate_pending — F13a Hiddenness theorem-grade (Paper 7, no Lean here).

Pending Paper 7 substrate claim, restricted to interfaces certified as the
saturated SAT hiddenness instance. It asserts only the quotient/currentizer
normal form: currentizer exposure matches quotient exposure, exposure collapses
the predictive quotient, and hiddenness is equivalent to surviving predictive
surplus.
-/
axiom hiddenness_pending :
  ∀ I : HiddennessInterface,
    Paper7SaturatedSATInstance I → HiddennessNormalForm I

/-- F13a wrapper: apply the narrow Paper 7 pending substrate claim. -/
theorem hiddenness_normal_form (I : HiddennessInterface)
    (hPaper7 : Paper7SaturatedSATInstance I) :
    HiddennessNormalForm I :=
  hiddenness_pending I hPaper7

end SixBirdsMetaMath.FoundationsIV.Access.HiddennessNormalForm
