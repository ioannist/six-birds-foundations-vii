namespace SixBirdsIII

def IsLossMinimum {Kernel Score : Type}
    (leq : Score -> Score -> Prop)
    (admissible : Kernel -> Prop)
    (loss : Kernel -> Score)
    (best : Kernel) : Prop :=
  admissible best /\ forall K : Kernel, admissible K -> leq (loss best) (loss K)

structure FiniteMarkovClosureProfile (Kernel Score : Type) where
  admissible : Kernel -> Prop
  conditionalMacroKernel : Kernel
  predictiveClosureLoss : Kernel -> Score
  conditionalMutualInformation : Score
  excessLoss : Kernel -> Score
  zero : Score
  add : Score -> Score -> Score
  leq : Score -> Score -> Prop
  conditional_admissible : admissible conditionalMacroKernel
  loss_decomposition :
    forall K : Kernel,
      admissible K ->
        predictiveClosureLoss K =
          add conditionalMutualInformation (excessLoss K)
  excess_nonnegative :
    forall K : Kernel, admissible K -> leq zero (excessLoss K)
  conditional_excess_zero : excessLoss conditionalMacroKernel = zero
  add_zero_cmi : add conditionalMutualInformation zero = conditionalMutualInformation
  cmi_le_add_nonnegative :
    forall e : Score, leq zero e -> leq conditionalMutualInformation
      (add conditionalMutualInformation e)

theorem finite_markov_closure_deficit {Kernel Score : Type}
    (profile : FiniteMarkovClosureProfile Kernel Score) :
    IsLossMinimum profile.leq
      profile.admissible
      profile.predictiveClosureLoss
      profile.conditionalMacroKernel /\
    profile.predictiveClosureLoss profile.conditionalMacroKernel =
      profile.conditionalMutualInformation := by
  have hbest :
      profile.predictiveClosureLoss profile.conditionalMacroKernel =
        profile.conditionalMutualInformation := by
    calc
      profile.predictiveClosureLoss profile.conditionalMacroKernel =
          profile.add profile.conditionalMutualInformation
            (profile.excessLoss profile.conditionalMacroKernel) :=
        profile.loss_decomposition profile.conditionalMacroKernel
          profile.conditional_admissible
      _ = profile.add profile.conditionalMutualInformation profile.zero := by
        rw [profile.conditional_excess_zero]
      _ = profile.conditionalMutualInformation := profile.add_zero_cmi
  refine ⟨?_, hbest⟩
  constructor
  · exact profile.conditional_admissible
  · intro K hK
    rw [hbest, profile.loss_decomposition K hK]
    exact profile.cmi_le_add_nonnegative
      (profile.excessLoss K)
      (profile.excess_nonnegative K hK)

end SixBirdsIII
