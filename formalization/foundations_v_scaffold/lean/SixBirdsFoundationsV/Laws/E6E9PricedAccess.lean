import SixBirdsFoundationsV.Definitional.ProbeEconomy
import SixBirdsFoundationsV.Definitional.ESystem

namespace SixBirdsFoundationsV

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Main.CriticalPair
open SixBirdsMetaMath.Xi.AdequacyResidual

/-!
E6/E9 priced access setup.

This module is the setup layer only.  The attention/curiosity theorems are
verification-shaped: marginal discharge, marginal cost, multiplier data, and
KKT equations are certified finite rational data supplied by the host.  No
calculus, convex-analysis library, or optimizer is imported or constructed
here.
-/

abbrev MarginalDischarge (Probe : Type u) (XiFamily : Type v) : Type (max u v) :=
  ActiveFamily Probe XiFamily -> Probe -> Rat

abbrev MarginalCost (Probe : Type u) (XiFamily : Type v) : Type (max u v) :=
  ActiveFamily Probe XiFamily -> Probe -> Rat

def AllocationRatio {Probe : Type u} {XiFamily : Type v}
    (marginalDischarge : MarginalDischarge Probe XiFamily)
    (marginalCost : MarginalCost Probe XiFamily)
    (w : ActiveFamily Probe XiFamily) (p : Probe) : Rat :=
  marginalDischarge w p / marginalCost w p

def PositiveMarginalCosts {Probe : Type u} {XiFamily : Type v}
    (marginalCost : MarginalCost Probe XiFamily)
    (w : ActiveFamily Probe XiFamily) : Prop :=
  ∀ p : Probe, p ∈ w.support -> marginalCost w p > 0

def SelectedProbe {Probe : Type u} {XiFamily : Type v}
    (w : ActiveFamily Probe XiFamily) (p : Probe) : Prop :=
  p ∈ w.support ∧ w.weight p > 0

def GenuineScarcity {Probe : Type u} {XiFamily : Type v}
    (w : ActiveFamily Probe XiFamily)
    (marginalDischarge : MarginalDischarge Probe XiFamily) : Prop :=
  ∃ p : Probe, SelectedProbe w p ∧ marginalDischarge w p > 0

structure ExposureBudgetWitness
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (move : ProbeMove Probe XiFamily) where
  spend : Rat
  budget : Rat
  budgetEntry : LedgerEntry
  budgetEntryInLedger : budgetEntry ∈ S.Lambda_S.ledgerEntries
  budgetEntryCertified : economy.ExposureBudgetEntry budgetEntry budget
  spendEntry : LedgerEntry
  spendEntryInLedger : spendEntry ∈ S.Lambda_S.ledgerEntries
  spendEntryCertified : economy.ExposureSpendEntry spendEntry spend
  budgetAdmissible : economy.BudgetAdmissible move

def BudgetFeasible
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    {economy : ProbeEconomy S Probe XiFamily}
    {move : ProbeMove Probe XiFamily}
    (budgetData : ExposureBudgetWitness economy move) : Prop :=
  budgetData.spend <= budgetData.budget

def BindingExposureBudget
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    {economy : ProbeEconomy S Probe XiFamily}
    {move : ProbeMove Probe XiFamily}
    (budgetData : ExposureBudgetWitness economy move) : Prop :=
  BudgetFeasible budgetData ∧ budgetData.spend = budgetData.budget

def SlackExposureBudget
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    {economy : ProbeEconomy S Probe XiFamily}
    {move : ProbeMove Probe XiFamily}
    (budgetData : ExposureBudgetWitness economy move) : Prop :=
  BudgetFeasible budgetData ∧ budgetData.spend < budgetData.budget

structure KKTWitness
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    {economy : ProbeEconomy S Probe XiFamily}
    {move : ProbeMove Probe XiFamily}
    (w : ActiveFamily Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (marginalDischarge : MarginalDischarge Probe XiFamily)
    (marginalCost : MarginalCost Probe XiFamily) where
  lambda : Rat
  mu : Probe -> Rat
  lambda_nonneg : lambda >= 0
  mu_nonneg : ∀ p : Probe, mu p >= 0
  complementarySlacknessBudget :
    lambda * (budgetData.spend - budgetData.budget) = 0
  complementarySlacknessNonneg :
    ∀ p : Probe, mu p * w.weight p = 0
  stationarity :
    ∀ p : Probe, p ∈ w.support ->
      marginalDischarge w p = lambda * marginalCost w p - mu p

abbrev AcquisitionDischarge (Probe : Type u) (XiFamily : Type v) : Type (max u v) :=
  ActiveFamily Probe XiFamily -> Probe -> Rat

abbrev AcquisitionCost (Probe : Type u) : Type u :=
  Probe -> Rat

def AcquisitionRatio {Probe : Type u} {XiFamily : Type v}
    (acquisitionDischarge : AcquisitionDischarge Probe XiFamily)
    (acquisitionCost : AcquisitionCost Probe)
    (L_t : ActiveFamily Probe XiFamily) (M : Probe) : Rat :=
  acquisitionDischarge L_t M / acquisitionCost M

def PositiveAcquisitionCosts {Probe : Type u}
    (acquisitionCost : AcquisitionCost Probe)
    (candidates : List Probe) : Prop :=
  ∀ M : Probe, M ∈ candidates -> acquisitionCost M > 0

def ViabilityRiskAdmissible (Probe : Type u) (XiFamily : Type v) : Type (max u v) :=
  ActiveFamily Probe XiFamily -> Probe -> Prop

def CandidateAcquisition
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (L_t : ActiveFamily Probe XiFamily) (M : Probe)
    (L_t' : ActiveFamily Probe XiFamily)
    (budgetData :
      ExposureBudgetWitness economy (ProbeMove.acquisition L_t M L_t'))
    (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily) : Prop :=
  M ∈ economy.catalog.probes ∧
    M ∉ L_t.support ∧
    AcquisitionStrict economy.sameFamilySaturated L_t M ∧
    BudgetFeasible budgetData ∧
    riskAdmissible L_t M

def CompleteAcquisitionCandidateList
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (L_t : ActiveFamily Probe XiFamily)
    (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily)
    (candidates : List Probe) : Prop :=
  ∀ M : Probe,
    (∃ L_t' : ActiveFamily Probe XiFamily,
      ∃ budgetData :
        ExposureBudgetWitness economy (ProbeMove.acquisition L_t M L_t'),
        CandidateAcquisition economy L_t M L_t' budgetData
          riskAdmissible) ->
    M ∈ candidates

inductive AccessMove (Probe : Type u) (XiFamily : Type v) where
  | allocate (L_t L_t' : ActiveFamily Probe XiFamily)
  | acquire (L_t : ActiveFamily Probe XiFamily) (M : Probe)
      (L_t' : ActiveFamily Probe XiFamily)

def AccessMove.toProbeMove {Probe : Type u} {XiFamily : Type v} :
    AccessMove Probe XiFamily -> ProbeMove Probe XiFamily
  | AccessMove.allocate L_t L_t' => ProbeMove.allocation L_t L_t'
  | AccessMove.acquire L_t M L_t' => ProbeMove.acquisition L_t M L_t'

structure AccessMovePricing (Probe : Type u) (XiFamily : Type v) where
  allocationDischarge :
    ActiveFamily Probe XiFamily -> ActiveFamily Probe XiFamily -> Rat
  allocationCost :
    ActiveFamily Probe XiFamily -> ActiveFamily Probe XiFamily -> Rat
  acquisitionDischarge : AcquisitionDischarge Probe XiFamily
  acquisitionCost : AcquisitionCost Probe

def AccessMoveDischarge {Probe : Type u} {XiFamily : Type v}
    (pricing : AccessMovePricing Probe XiFamily) :
    AccessMove Probe XiFamily -> Rat
  | AccessMove.allocate L_t L_t' => pricing.allocationDischarge L_t L_t'
  | AccessMove.acquire L_t M _ => pricing.acquisitionDischarge L_t M

def AccessMoveCost {Probe : Type u} {XiFamily : Type v}
    (pricing : AccessMovePricing Probe XiFamily) :
    AccessMove Probe XiFamily -> Rat
  | AccessMove.allocate L_t L_t' => pricing.allocationCost L_t L_t'
  | AccessMove.acquire _ M _ => pricing.acquisitionCost M

def PositiveAccessMoveCosts {Probe : Type u} {XiFamily : Type v}
    (pricing : AccessMovePricing Probe XiFamily)
    (candidates : List (AccessMove Probe XiFamily)) : Prop :=
  ∀ move : AccessMove Probe XiFamily, move ∈ candidates ->
    AccessMoveCost pricing move > 0

def AccessMoveRatio {Probe : Type u} {XiFamily : Type v}
    (pricing : AccessMovePricing Probe XiFamily)
    (move : AccessMove Probe XiFamily) : Rat :=
  AccessMoveDischarge pricing move / AccessMoveCost pricing move

structure AccessPolicy (Probe : Type u) (XiFamily : Type v) where
  selects : AccessMove Probe XiFamily -> Prop

def PolicyCarriedAt
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (policyRecord :
      CarriedRecordPolicy S.T (AccessPolicy Probe XiFamily))
    (policy : AccessPolicy Probe XiFamily) (n0 : Nat)
    (sourceTag : FineSourceTag) (generatedByS inScope : Bool) : Prop :=
  CarriedRecordAt policyRecord policy n0 sourceTag generatedByS inScope

/--
E6's stated law assumes a binding exposure budget, so the hypothesis is kept
for statement fidelity.  The algebra below does not use it directly:
`GenuineScarcity` together with the KKT equations already rules out the slack
case, since `E6_SlackCollapse` would force `lambda = 0` under slack while
selected-probe complementary slackness and stationarity would then force zero
marginal discharge on every selected probe.
-/
theorem E6_AttentionKKT
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    {economy : ProbeEconomy S Probe XiFamily}
    {move : ProbeMove Probe XiFamily}
    {w : ActiveFamily Probe XiFamily}
    {budgetData : ExposureBudgetWitness economy move}
    {marginalDischarge : MarginalDischarge Probe XiFamily}
    {marginalCost : MarginalCost Probe XiFamily}
    (kkt : KKTWitness w budgetData marginalDischarge marginalCost)
    (positiveCosts : PositiveMarginalCosts marginalCost w)
    (_hBinding : BindingExposureBudget budgetData)
    (hScarcity : GenuineScarcity w marginalDischarge) :
    kkt.lambda > 0 ∧
      (∀ p : Probe, SelectedProbe w p ->
        AllocationRatio marginalDischarge marginalCost w p = kkt.lambda) ∧
      (∀ p : Probe, p ∈ w.support -> w.weight p = 0 ->
        AllocationRatio marginalDischarge marginalCost w p <= kkt.lambda) := by
  have hsub_zero : ∀ a : Rat, a - 0 = a := by
    intro a
    rw [Rat.sub_eq_add_neg]
    have hneg_zero : - (0 : Rat) = 0 := by
      apply Rat.ext
      · simp [Rat.neg_num]
      · simp [Rat.neg_den]
    rw [hneg_zero]
    exact Rat.add_zero a
  have selected_ratio :
      ∀ p : Probe, SelectedProbe w p ->
        AllocationRatio marginalDischarge marginalCost w p = kkt.lambda := by
    intro p hselected
    rcases hselected with ⟨hpSupport, hpWeightPos⟩
    have hmu_zero : kkt.mu p = 0 := by
      have hprod := kkt.complementarySlacknessNonneg p
      have hcases := (Rat.mul_eq_zero).mp hprod
      cases hcases with
      | inl hmu => exact hmu
      | inr hweight_zero =>
          exact False.elim ((Rat.ne_of_gt hpWeightPos) hweight_zero)
    have hmd_eq :
        marginalDischarge w p = kkt.lambda * marginalCost w p := by
      have hstation := kkt.stationarity p hpSupport
      rw [hmu_zero] at hstation
      rw [hsub_zero] at hstation
      exact hstation
    unfold AllocationRatio
    rw [hmd_eq]
    change
      (kkt.lambda * marginalCost w p) * (marginalCost w p)⁻¹ =
        kkt.lambda
    rw [Rat.mul_assoc]
    rw [Rat.mul_inv_cancel (marginalCost w p)
      (Rat.ne_of_gt (positiveCosts p hpSupport))]
    exact Rat.mul_one kkt.lambda
  have unselected_ratio :
      ∀ p : Probe, p ∈ w.support -> w.weight p = 0 ->
        AllocationRatio marginalDischarge marginalCost w p <= kkt.lambda := by
    intro p hpSupport _hpWeightZero
    have hstation := kkt.stationarity p hpSupport
    have hmd_le :
        marginalDischarge w p <= kkt.lambda * marginalCost w p := by
      rw [hstation]
      rw [Rat.le_iff_sub_nonneg]
      have hmu_nonneg := kkt.mu_nonneg p
      grind [Rat.sub_eq_add_neg, Rat.add_assoc, Rat.add_comm,
        Rat.add_left_comm]
    unfold AllocationRatio
    change
      marginalDischarge w p * (marginalCost w p)⁻¹ <= kkt.lambda
    have hcost_pos := positiveCosts p hpSupport
    have hcost_inv_nonneg : 0 <= (marginalCost w p)⁻¹ :=
      Rat.le_of_lt ((Rat.inv_pos).mpr hcost_pos)
    have hmul :
        marginalDischarge w p * (marginalCost w p)⁻¹ <=
          (kkt.lambda * marginalCost w p) * (marginalCost w p)⁻¹ :=
      Rat.mul_le_mul_of_nonneg_right hmd_le hcost_inv_nonneg
    have hright :
        (kkt.lambda * marginalCost w p) * (marginalCost w p)⁻¹ =
          kkt.lambda := by
      rw [Rat.mul_assoc]
      rw [Rat.mul_inv_cancel (marginalCost w p)
        (Rat.ne_of_gt hcost_pos)]
      exact Rat.mul_one kkt.lambda
    rw [hright] at hmul
    exact hmul
  have hlambda_pos : kkt.lambda > 0 := by
    rcases hScarcity with ⟨p, hselected, hmd_pos⟩
    have hselected_copy : SelectedProbe w p := hselected
    rcases hselected with ⟨hpSupport, _hpWeightPos⟩
    have hratio := selected_ratio p hselected_copy
    have hcost_pos := positiveCosts p hpSupport
    have hratio_pos :
        AllocationRatio marginalDischarge marginalCost w p > 0 := by
      unfold AllocationRatio
      change
        marginalDischarge w p * (marginalCost w p)⁻¹ > 0
      exact Rat.mul_pos hmd_pos ((Rat.inv_pos).mpr hcost_pos)
    rw [hratio] at hratio_pos
    exact hratio_pos
  exact ⟨hlambda_pos, selected_ratio, unselected_ratio⟩

theorem E6_SlackCollapse
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    {economy : ProbeEconomy S Probe XiFamily}
    {move : ProbeMove Probe XiFamily}
    {w : ActiveFamily Probe XiFamily}
    {budgetData : ExposureBudgetWitness economy move}
    {marginalDischarge : MarginalDischarge Probe XiFamily}
    {marginalCost : MarginalCost Probe XiFamily}
    (kkt : KKTWitness w budgetData marginalDischarge marginalCost)
    (hSlack : SlackExposureBudget budgetData) :
    kkt.lambda = 0 := by
  have hdiff_ne : budgetData.spend - budgetData.budget ≠ 0 := by
    intro hzero
    have hbudget_le_spend : budgetData.budget <= budgetData.spend := by
      rw [Rat.le_iff_sub_nonneg]
      rw [hzero]
      exact (Rat.le_refl : (0 : Rat) <= 0)
    have heq : budgetData.spend = budgetData.budget :=
      Rat.le_antisymm hSlack.1 hbudget_le_spend
    have hlt := hSlack.2
    rw [heq] at hlt
    exact Rat.lt_irrefl hlt
  have hcases := (Rat.mul_eq_zero).mp kkt.complementarySlacknessBudget
  cases hcases with
  | inl hlambda => exact hlambda
  | inr hdiff => exact False.elim (hdiff_ne hdiff)

def XiAcqDischarge {e y z m : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (M : Mat m e)
    (KLLdagger : Mat y y) (KMMLdagger : Mat m m) : Rat :=
  traceMat
    (matMul
      (matMul (conditionalCurrencyDM_L C L D M KLLdagger) KMMLdagger)
      (conditionalCurrencyMD_L C L D M KLLdagger))

theorem E9_SameFamilyStrictness {e y z m : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (M : Mat m e)
    (KLLdagger : Mat y y) (KMMLdagger : Mat m m)
    (B : Mat m y) (extendedResidual : Mat z z)
    (hChainRule :
      extendedResidual =
        matSub
          (adequacyResidual C L D KLLdagger)
          (matMul
            (matMul (conditionalCurrencyDM_L C L D M KLLdagger) KMMLdagger)
            (conditionalCurrencyMD_L C L D M KLLdagger)))
    (hM_factors : M = matMul B L)
    (hDML_zero :
      conditionalCurrencyDM_L C L D M KLLdagger = zeroMat z m) :
    XiAcqDischarge C L D M KLLdagger KMMLdagger = 0 := by
  have _hSaturated :
      XiSameFamilySaturated C D KLLdagger KMMLdagger extendedResidual L M :=
    xi_sameFamilySaturated_of_sameFamilySaturation
      C L D M KLLdagger KMMLdagger B extendedResidual
      hChainRule hM_factors hDML_zero
  unfold XiAcqDischarge
  rw [hDML_zero]
  rw [matMul_zero_left]
  rw [matMul_zero_left]
  exact traceMat_zeroMat

theorem exists_max_ratio {Probe : Type u} (ratio : Probe -> Rat) :
    ∀ candidates : List Probe, candidates ≠ [] ->
      ∃ best : Probe,
        best ∈ candidates ∧
          ∀ p : Probe, p ∈ candidates -> ratio p <= ratio best := by
  intro candidates
  induction candidates with
  | nil =>
      intro hne
      exact False.elim (hne rfl)
  | cons head tail ih =>
      intro _hne
      by_cases htail : tail = []
      · subst tail
        exact
          ⟨head, List.mem_cons_self, by
            intro p hp
            cases hp with
            | head _ => exact Rat.le_refl
            | tail _ hmem => exact False.elim (List.not_mem_nil hmem)⟩
      · rcases ih htail with ⟨tailBest, htailBestMem, htailBestMax⟩
        cases (Rat.le_total (a := ratio head) (b := ratio tailBest)) with
        | inl hhead_le_tailBest =>
            exact
              ⟨tailBest, List.mem_cons_of_mem head htailBestMem, by
                intro p hp
                cases hp with
                | head _ => exact hhead_le_tailBest
                | tail _ hpTail => exact htailBestMax p hpTail⟩
        | inr htailBest_le_head =>
            exact
              ⟨head, List.mem_cons_self, by
                intro p hp
                cases hp with
                | head _ => exact Rat.le_refl
                | tail _ hpTail =>
                    exact Rat.le_trans (htailBestMax p hpTail)
                      htailBest_le_head⟩

theorem E9_CuriosityArgmax
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (L_t : ActiveFamily Probe XiFamily)
    (acquisitionDischarge : AcquisitionDischarge Probe XiFamily)
    (acquisitionCost : AcquisitionCost Probe)
    (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily)
    (candidates : List Probe)
    (candidateAdmissible :
      ∀ M : Probe, M ∈ candidates ->
        ∃ L_t' : ActiveFamily Probe XiFamily,
          ∃ budgetData :
            ExposureBudgetWitness economy (ProbeMove.acquisition L_t M L_t'),
            CandidateAcquisition economy L_t M L_t' budgetData
              riskAdmissible)
    (_positiveCosts : PositiveAcquisitionCosts acquisitionCost candidates)
    (complete :
      CompleteAcquisitionCandidateList economy L_t riskAdmissible candidates)
    (hne : candidates ≠ []) :
    ∃ Mstar : Probe,
      Mstar ∈ candidates ∧
        (∃ L_t' : ActiveFamily Probe XiFamily,
          ∃ budgetData :
            ExposureBudgetWitness economy (ProbeMove.acquisition L_t Mstar L_t'),
            CandidateAcquisition economy L_t Mstar L_t' budgetData
              riskAdmissible) ∧
        ∀ M : Probe,
          (∃ L_t' : ActiveFamily Probe XiFamily,
            ∃ budgetData :
              ExposureBudgetWitness economy (ProbeMove.acquisition L_t M L_t'),
              CandidateAcquisition economy L_t M L_t' budgetData
                riskAdmissible) ->
          AcquisitionRatio acquisitionDischarge acquisitionCost L_t M <=
            AcquisitionRatio acquisitionDischarge acquisitionCost L_t Mstar := by
  rcases exists_max_ratio
      (fun M : Probe =>
        AcquisitionRatio acquisitionDischarge acquisitionCost L_t M)
      candidates hne with
    ⟨Mstar, hMstarMem, hMstarMax⟩
  exact
    ⟨Mstar, hMstarMem, candidateAdmissible Mstar hMstarMem, by
      intro M hMAdmissible
      exact hMstarMax M (complete M hMAdmissible)⟩

def AccessMoveAdmissible
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily) :
    AccessMove Probe XiFamily -> Prop
  | AccessMove.allocate L_t L_t' =>
      ∃ preN0 : Nat,
        ∃ preSourceTag : FineSourceTag,
          ∃ preGeneratedByS : Bool,
            ∃ preInScope : Bool,
              ∃ postN0 : Nat,
                ∃ postSourceTag : FineSourceTag,
                  ∃ postGeneratedByS : Bool,
                    ∃ postInScope : Bool,
                      LawfulAllocation economy L_t L_t'
                        preN0 preSourceTag preGeneratedByS preInScope
                        postN0 postSourceTag postGeneratedByS postInScope
  | AccessMove.acquire L_t M L_t' =>
      ∃ preN0 : Nat,
        ∃ preSourceTag : FineSourceTag,
          ∃ preGeneratedByS : Bool,
            ∃ preInScope : Bool,
              ∃ postN0 : Nat,
                ∃ postSourceTag : FineSourceTag,
                  ∃ postGeneratedByS : Bool,
                    ∃ postInScope : Bool,
                      LawfulAcquisition economy L_t M L_t'
                        preN0 preSourceTag preGeneratedByS preInScope
                        postN0 postSourceTag postGeneratedByS postInScope ∧
                        ∃ budgetData :
                          ExposureBudgetWitness economy
                            (ProbeMove.acquisition L_t M L_t'),
                          CandidateAcquisition economy L_t M L_t'
                            budgetData riskAdmissible

def CompleteAccessMoveCandidateList
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily)
    (candidates : List (AccessMove Probe XiFamily)) : Prop :=
  ∀ move : AccessMove Probe XiFamily,
    AccessMoveAdmissible economy riskAdmissible move -> move ∈ candidates

theorem E6_E9_AccessArbitration
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (pricing : AccessMovePricing Probe XiFamily)
    (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily)
    (candidates : List (AccessMove Probe XiFamily))
    (candidateAdmissible :
      ∀ move : AccessMove Probe XiFamily, move ∈ candidates ->
        AccessMoveAdmissible economy riskAdmissible move)
    (_positiveCosts : PositiveAccessMoveCosts pricing candidates)
    (complete :
      CompleteAccessMoveCandidateList economy riskAdmissible candidates)
    (hne : candidates ≠ []) :
    ∃ mstar : AccessMove Probe XiFamily,
      mstar ∈ candidates ∧
        AccessMoveAdmissible economy riskAdmissible mstar ∧
        ∀ move : AccessMove Probe XiFamily,
          AccessMoveAdmissible economy riskAdmissible move ->
          AccessMoveRatio pricing move <= AccessMoveRatio pricing mstar := by
  rcases exists_max_ratio (AccessMoveRatio pricing) candidates hne with
    ⟨mstar, hmstarMem, hmstarMax⟩
  exact
    ⟨mstar, hmstarMem, candidateAdmissible mstar hmstarMem, by
      intro move hmoveAdmissible
      exact hmstarMax move (complete move hmoveAdmissible)⟩

theorem E6_E9_AccessArbitration_epsilon
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (pricing : AccessMovePricing Probe XiFamily)
    (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily)
    (candidates : List (AccessMove Probe XiFamily))
    (candidateAdmissible :
      ∀ move : AccessMove Probe XiFamily, move ∈ candidates ->
        AccessMoveAdmissible economy riskAdmissible move)
    (positiveCosts : PositiveAccessMoveCosts pricing candidates)
    (complete :
      CompleteAccessMoveCandidateList economy riskAdmissible candidates)
    (hne : candidates ≠ []) (eps : Rat) (heps : eps >= 0) :
    ∃ mstar : AccessMove Probe XiFamily,
      mstar ∈ candidates ∧
        AccessMoveAdmissible economy riskAdmissible mstar ∧
        ∀ move : AccessMove Probe XiFamily,
          AccessMoveAdmissible economy riskAdmissible move ->
          AccessMoveRatio pricing move <= AccessMoveRatio pricing mstar + eps := by
  rcases E6_E9_AccessArbitration economy pricing riskAdmissible candidates
      candidateAdmissible positiveCosts complete hne with
    ⟨mstar, hmstarMem, hmstarAdmissible, hmstarMax⟩
  have hself_le :
      AccessMoveRatio pricing mstar <= AccessMoveRatio pricing mstar + eps := by
    have h :=
      rat_add_le_add (AccessMoveRatio pricing mstar)
        (AccessMoveRatio pricing mstar) 0 eps Rat.le_refl heps
    rw [Rat.add_zero] at h
    exact h
  exact
    ⟨mstar, hmstarMem, hmstarAdmissible, by
      intro move hmoveAdmissible
      exact Rat.le_trans (hmstarMax move hmoveAdmissible) hself_le⟩

theorem selected_access_move_ratio_bound
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (pricing : AccessMovePricing Probe XiFamily)
    (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily)
    (candidates : List (AccessMove Probe XiFamily))
    (_candidateAdmissible :
      ∀ move : AccessMove Probe XiFamily, move ∈ candidates ->
        AccessMoveAdmissible economy riskAdmissible move)
    (_positiveCosts : PositiveAccessMoveCosts pricing candidates)
    (complete :
      CompleteAccessMoveCandidateList economy riskAdmissible candidates)
    (_hne : candidates ≠ [])
    (policy : AccessPolicy Probe XiFamily)
    (selected : AccessMove Probe XiFamily)
    (_hselects : policy.selects selected)
    (hselected_argmax :
      selected ∈ candidates ∧
        ∀ move : AccessMove Probe XiFamily, move ∈ candidates ->
          AccessMoveRatio pricing move <= AccessMoveRatio pricing selected) :
    ∀ alternative : AccessMove Probe XiFamily,
      AccessMoveAdmissible economy riskAdmissible alternative ->
        AccessMoveRatio pricing alternative <=
          AccessMoveRatio pricing selected := by
  intro alternative halternative
  exact hselected_argmax.2 alternative (complete alternative halternative)

theorem selected_access_move_ratio_bound_epsilon
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (pricing : AccessMovePricing Probe XiFamily)
    (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily)
    (candidates : List (AccessMove Probe XiFamily))
    (_candidateAdmissible :
      ∀ move : AccessMove Probe XiFamily, move ∈ candidates ->
        AccessMoveAdmissible economy riskAdmissible move)
    (_positiveCosts : PositiveAccessMoveCosts pricing candidates)
    (complete :
      CompleteAccessMoveCandidateList economy riskAdmissible candidates)
    (_hne : candidates ≠ [])
    (policy : AccessPolicy Probe XiFamily)
    (selected : AccessMove Probe XiFamily)
    (_hselects : policy.selects selected)
    (hselected_argmax :
      selected ∈ candidates ∧
        ∀ move : AccessMove Probe XiFamily, move ∈ candidates ->
          AccessMoveRatio pricing move <= AccessMoveRatio pricing selected)
    (eps : Rat) (heps : eps >= 0) :
    ∀ alternative : AccessMove Probe XiFamily,
      AccessMoveAdmissible economy riskAdmissible alternative ->
        AccessMoveRatio pricing alternative <=
          AccessMoveRatio pricing selected + eps := by
  intro alternative halternative
  have hbound :=
    selected_access_move_ratio_bound economy pricing riskAdmissible
      candidates _candidateAdmissible _positiveCosts complete _hne
      policy selected _hselects hselected_argmax alternative halternative
  have hself_le :
      AccessMoveRatio pricing selected <=
        AccessMoveRatio pricing selected + eps := by
    have h :=
      rat_add_le_add (AccessMoveRatio pricing selected)
        (AccessMoveRatio pricing selected) 0 eps Rat.le_refl heps
    rw [Rat.add_zero] at h
    exact h
  exact Rat.le_trans hbound hself_le

def Delta_access
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (pricing : AccessMovePricing Probe XiFamily)
    (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily)
    (policy : AccessPolicy Probe XiFamily) (eps : Rat)
    (statusedResidual :
      AccessMove Probe XiFamily -> AccessMove Probe XiFamily -> Prop)
    (selected alternative : AccessMove Probe XiFamily) : Prop :=
  policy.selects selected ∧
    AccessMoveAdmissible economy riskAdmissible alternative ∧
    AccessMoveRatio pricing selected + eps < AccessMoveRatio pricing alternative ∧
    ¬ statusedResidual selected alternative

end SixBirdsFoundationsV
