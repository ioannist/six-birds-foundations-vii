import SixBirdsIII.FiniteProbability
import Xi.AdequacyResidual
import Xi.StrictExtension

open SixBirdsIII
open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Xi.AdequacyResidual

namespace SixBirdsFoundationsV

/-!
D2 predictive surplus.

The closure-deficit route is order-level: the imported FIII closure profile
has a score preorder but no subtraction. The Rat value and the Xi trace readout
are separate concrete laboratory forms; no bridge theorem between them is
asserted here.
-/

def closureDeficit {Kernel Score : Type}
    (profile : FiniteMarkovClosureProfile Kernel Score) : Score :=
  profile.conditionalMutualInformation

structure PredictiveSurplusNonnegative {Score : Type}
    (leq : Score -> Score -> Prop) (qDeficit mDeficit : Score) : Prop where
  baseline_le : leq mDeficit qDeficit

def predictiveSurplusNonnegativeForProfiles {KernelQ KernelM Score : Type}
    (leq : Score -> Score -> Prop)
    (qProfile : FiniteMarkovClosureProfile KernelQ Score)
    (mProfile : FiniteMarkovClosureProfile KernelM Score) : Prop :=
  PredictiveSurplusNonnegative leq
    (closureDeficit qProfile)
    (closureDeficit mProfile)

theorem predictiveSurplus_identical {Score : Type}
    (leq : Score -> Score -> Prop) (qDeficit : Score)
    (hle_refl : leq qDeficit qDeficit) :
    PredictiveSurplusNonnegative leq qDeficit qDeficit := by
  exact ⟨hle_refl⟩

theorem predictiveSurplus_profile_identical {Kernel Score : Type}
    (profile : FiniteMarkovClosureProfile Kernel Score)
    (hle_refl : profile.leq (closureDeficit profile) (closureDeficit profile)) :
    predictiveSurplusNonnegativeForProfiles profile.leq profile profile := by
  exact ⟨hle_refl⟩

theorem predictiveSurplus_exact_baseline {Score : Type}
    (leq : Score -> Score -> Prop) (zero qDeficit mDeficit : Score)
    (hm_exact : mDeficit = zero) (hq_nonnegative : leq zero qDeficit) :
    PredictiveSurplusNonnegative leq qDeficit mDeficit := by
  rw [hm_exact]
  exact ⟨hq_nonnegative⟩

def predictiveSurplusValue (qDeficit mDeficit : Rat) : Rat :=
  qDeficit - mDeficit

theorem predictiveSurplusValue_nonnegative_iff (qDeficit mDeficit : Rat) :
    0 <= predictiveSurplusValue qDeficit mDeficit ↔
      PredictiveSurplusNonnegative (fun a b : Rat => a <= b) qDeficit mDeficit := by
  constructor
  · intro h
    have hmleq : mDeficit <= qDeficit := by
      rw [Rat.le_iff_sub_nonneg]
      exact h
    exact ⟨hmleq⟩
  · intro h
    have hmleq : mDeficit <= qDeficit := h.baseline_le
    rw [Rat.le_iff_sub_nonneg] at hmleq
    exact hmleq

theorem predictiveSurplusValue_identical (qDeficit : Rat) :
    predictiveSurplusValue qDeficit qDeficit = 0 := by
  unfold predictiveSurplusValue
  rw [Rat.sub_eq_add_neg]
  exact Rat.add_neg_cancel qDeficit

theorem predictiveSurplusValue_exact_baseline (qDeficit mDeficit : Rat)
    (hm_exact : mDeficit = 0) :
    predictiveSurplusValue qDeficit mDeficit = qDeficit := by
  rw [hm_exact]
  unfold predictiveSurplusValue
  rw [Rat.sub_eq_add_neg]
  have hneg_zero : - (0 : Rat) = 0 := by
    apply Rat.ext
    · simp [Rat.neg_num]
    · simp [Rat.neg_den]
  rw [hneg_zero]
  exact Rat.add_zero qDeficit

def predictiveSurplusXi {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) : Rat :=
  traceMat (adequacyResidual C L D KLLdagger)

theorem predictiveSurplusXi_nonnegative_of_psd {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y)
    (hpsd : PositiveSemidefinite (adequacyResidual C L D KLLdagger)) :
    0 <= predictiveSurplusXi C L D KLLdagger := by
  exact psd_trace_nonneg (adequacyResidual C L D KLLdagger) hpsd

theorem predictiveSurplusXi_chain_rule_monotone {e y z m : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (M : Mat m e)
    (KLLdagger : Mat y y) (KMMLdagger : Mat m m)
    (extendedResidual : Mat z z)
    (hChainRule :
      extendedResidual =
        matSub
          (adequacyResidual C L D KLLdagger)
          (matMul
            (matMul
              (SixBirdsMetaMath.Main.CriticalPair.conditionalCurrencyDM_L
                C L D M KLLdagger)
              KMMLdagger)
            (SixBirdsMetaMath.Main.CriticalPair.conditionalCurrencyMD_L
              C L D M KLLdagger)))
    (hConditionalSchurPSD :
      PositiveSemidefinite
        (matMul
          (matMul
            (SixBirdsMetaMath.Main.CriticalPair.conditionalCurrencyDM_L
              C L D M KLLdagger)
            KMMLdagger)
          (SixBirdsMetaMath.Main.CriticalPair.conditionalCurrencyMD_L
            C L D M KLLdagger))) :
    traceMat extendedResidual <= predictiveSurplusXi C L D KLLdagger := by
  have hLoewner :
      loewnerLE extendedResidual (adequacyResidual C L D KLLdagger) :=
    SixBirdsMetaMath.Xi.StrictExtension.chainRule
      C L D M KLLdagger KMMLdagger extendedResidual
      hChainRule hConditionalSchurPSD
  exact loewnerLE_traceMat_mono extendedResidual
    (adequacyResidual C L D KLLdagger) hLoewner

theorem predictiveSurplusXi_same_family_saturation {e y z m : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (M : Mat m e)
    (KLLdagger : Mat y y) (KMMLdagger : Mat m m)
    (B : Mat m y) (extendedResidual : Mat z z)
    (hChainRule :
      extendedResidual =
        matSub
          (adequacyResidual C L D KLLdagger)
          (matMul
            (matMul
              (SixBirdsMetaMath.Main.CriticalPair.conditionalCurrencyDM_L
                C L D M KLLdagger)
              KMMLdagger)
            (SixBirdsMetaMath.Main.CriticalPair.conditionalCurrencyMD_L
              C L D M KLLdagger)))
    (hM_factors : M = matMul B L)
    (hDML_zero :
      SixBirdsMetaMath.Main.CriticalPair.conditionalCurrencyDM_L
        C L D M KLLdagger = zeroMat z m) :
    traceMat extendedResidual = predictiveSurplusXi C L D KLLdagger := by
  rw [
    SixBirdsMetaMath.Xi.StrictExtension.sameFamilySaturation
      C L D M KLLdagger KMMLdagger B extendedResidual
      hChainRule hM_factors hDML_zero]
  rfl

end SixBirdsFoundationsV
