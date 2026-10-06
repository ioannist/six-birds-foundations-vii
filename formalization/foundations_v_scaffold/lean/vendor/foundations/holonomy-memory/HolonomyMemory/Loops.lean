import HolonomyMemory.Transport

namespace HolonomyMemory

abbrev Loop
    (T : RouteTransportCore) (i : T.Interface) :=
  T.Continuation i i

def predictiveLoopAction
    (T : RouteTransportCore) {i : T.Interface}
    (ℓ : Loop T i) :
    PredictiveQuotient T i → PredictiveQuotient T i :=
  predictiveTransport T ℓ

@[simp] theorem predictiveLoopAction_mk
    (T : RouteTransportCore) {i : T.Interface}
    (ℓ : Loop T i) (h : T.History i) :
    predictiveLoopAction T ℓ (Quotient.mk (PredictiveSetoid T i) h) =
      Quotient.mk (PredictiveSetoid T i) (T.push h ℓ) := by
  rfl

end HolonomyMemory
