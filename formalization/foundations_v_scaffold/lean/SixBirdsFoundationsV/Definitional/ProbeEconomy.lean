import SixBirdsFoundationsV.Definitional.ESystem
import SixBirdsFoundationsV.Definitional.PredictiveSurplus

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Main.CriticalPair
open SixBirdsMetaMath.Xi.AdequacyResidual

namespace SixBirdsFoundationsV

/-!
D6 probe economy.

The core definition is abstract and Mathlib-free.  Probe supports and catalogs
are represented by finite lists; active means support membership, not positive
weight.  The Xi matrix block at the bottom is an optional instantiation of the
same-family saturation strictness test, not a requirement on all probe
economies.
-/

structure ProbeCatalog (Probe : Type u) where
  probes : List Probe
  CompleteProbeCatalog : Prop
  catalogComplete : CompleteProbeCatalog

structure ActiveFamily (Probe : Type u) (XiFamily : Type v) where
  support : List Probe
  weight : Probe -> Rat
  asXiFamily : Option XiFamily

def SameFamilySaturated {Family : Type u} {Probe : Type v}
    (saturated : Family -> Probe -> Prop) (L : Family) (M : Probe) : Prop :=
  saturated L M

def AcquisitionStrict {Family : Type u} {Probe : Type v}
    (saturated : Family -> Probe -> Prop) (L : Family) (M : Probe) : Prop :=
  ¬ SameFamilySaturated saturated L M

inductive ProbeMove (Probe : Type u) (XiFamily : Type v) where
  | allocation (L_t L_t' : ActiveFamily Probe XiFamily)
  | acquisition (L_t : ActiveFamily Probe XiFamily) (M : Probe)
      (L_t' : ActiveFamily Probe XiFamily)
  | retirement (L_t : ActiveFamily Probe XiFamily) (M : Probe)
      (L_t' : ActiveFamily Probe XiFamily)

structure ProbeEconomy
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (Probe : Type z) (XiFamily : Type z') where
  catalog : ProbeCatalog Probe
  activeFamilyPolicy : CarriedRecordPolicy S.T (ActiveFamily Probe XiFamily)
  sameFamilySaturated : ActiveFamily Probe XiFamily -> Probe -> Prop
  ExposureCostEntry : LedgerEntry -> Probe -> Rat -> Prop
  ExposureBudgetEntry : LedgerEntry -> Rat -> Prop
  ExposureSpendEntry : LedgerEntry -> Rat -> Prop
  RetirementRecordEntry : LedgerEntry -> Probe -> Prop
  BudgetAdmissible : ProbeMove Probe XiFamily -> Prop

def ActiveFamilyCarriedAt
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (L_t : ActiveFamily Probe XiFamily) (n0 : Nat)
    (sourceTag : FineSourceTag) (generatedByS inScope : Bool) : Prop :=
  CarriedRecordAt economy.activeFamilyPolicy L_t n0 sourceTag generatedByS inScope

def ActiveSupportInCatalog
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (L_t : ActiveFamily Probe XiFamily) : Prop :=
  ∀ p : Probe, p ∈ L_t.support -> p ∈ economy.catalog.probes

def LawfulActiveFamilyAt
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (L_t : ActiveFamily Probe XiFamily) (n0 : Nat)
    (sourceTag : FineSourceTag) (generatedByS inScope : Bool) : Prop :=
  ActiveSupportInCatalog economy L_t ∧
    ActiveFamilyCarriedAt economy L_t n0 sourceTag generatedByS inScope

def SupportAddsProbe {Probe : Type u} {XiFamily : Type v}
    (L_t : ActiveFamily Probe XiFamily) (M : Probe)
    (L_t' : ActiveFamily Probe XiFamily) : Prop :=
  M ∉ L_t.support ∧
    ∀ p : Probe, p ∈ L_t'.support ↔ p = M ∨ p ∈ L_t.support

def SupportRemovesProbe {Probe : Type u} {XiFamily : Type v}
    (L_t : ActiveFamily Probe XiFamily) (M : Probe)
    (L_t' : ActiveFamily Probe XiFamily) : Prop :=
  M ∈ L_t.support ∧
    ∀ p : Probe, p ∈ L_t'.support ↔ p ∈ L_t.support ∧ p ≠ M

structure LawfulAllocation
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    (economy : ProbeEconomy S Probe XiFamily)
    (L_t L_t' : ActiveFamily Probe XiFamily)
    (preN0 : Nat) (preSourceTag : FineSourceTag)
    (preGeneratedByS preInScope : Bool)
    (postN0 : Nat) (postSourceTag : FineSourceTag)
    (postGeneratedByS postInScope : Bool) : Prop where
  preLawfulActiveFamily :
    LawfulActiveFamilyAt economy L_t preN0 preSourceTag preGeneratedByS
      preInScope
  supportUnchanged : L_t'.support = L_t.support
  weightsOnlyOnSharedSupport :
    ∀ p : Probe, p ∉ L_t.support -> L_t'.weight p = L_t.weight p
  costEntriesExist :
    ∀ p : Probe, p ∈ L_t.support ->
      ∃ entry : LedgerEntry,
        entry ∈ S.Lambda_S.ledgerEntries ∧
          ∃ cost : Rat, economy.ExposureCostEntry entry p cost
  budgetEntryExists :
    ∃ entry : LedgerEntry,
      entry ∈ S.Lambda_S.ledgerEntries ∧
        ∃ budget : Rat, economy.ExposureBudgetEntry entry budget
  spendEntryExists :
    ∃ entry : LedgerEntry,
      entry ∈ S.Lambda_S.ledgerEntries ∧
        ∃ spend : Rat, economy.ExposureSpendEntry entry spend
  budgetAdmissible :
    economy.BudgetAdmissible (ProbeMove.allocation L_t L_t')
  postLawfulActiveFamily :
    LawfulActiveFamilyAt economy L_t' postN0 postSourceTag postGeneratedByS
      postInScope

structure LawfulAcquisition
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
    (preN0 : Nat) (preSourceTag : FineSourceTag)
    (preGeneratedByS preInScope : Bool)
    (postN0 : Nat) (postSourceTag : FineSourceTag)
    (postGeneratedByS postInScope : Bool) : Prop where
  preLawfulActiveFamily :
    LawfulActiveFamilyAt economy L_t preN0 preSourceTag preGeneratedByS
      preInScope
  catalogMember : M ∈ economy.catalog.probes
  notActiveBefore : M ∉ L_t.support
  supportAdds : SupportAddsProbe L_t M L_t'
  strict : AcquisitionStrict economy.sameFamilySaturated L_t M
  costEntryExists :
    ∃ entry : LedgerEntry,
      entry ∈ S.Lambda_S.ledgerEntries ∧
        ∃ cost : Rat, economy.ExposureCostEntry entry M cost
  budgetEntryExists :
    ∃ entry : LedgerEntry,
      entry ∈ S.Lambda_S.ledgerEntries ∧
        ∃ budget : Rat, economy.ExposureBudgetEntry entry budget
  spendEntryExists :
    ∃ entry : LedgerEntry,
      entry ∈ S.Lambda_S.ledgerEntries ∧
        ∃ spend : Rat, economy.ExposureSpendEntry entry spend
  budgetAdmissible :
    economy.BudgetAdmissible (ProbeMove.acquisition L_t M L_t')
  postLawfulActiveFamily :
    LawfulActiveFamilyAt economy L_t' postN0 postSourceTag postGeneratedByS
      postInScope

structure LawfulRetirement
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
    (preN0 : Nat) (preSourceTag : FineSourceTag)
    (preGeneratedByS preInScope : Bool)
    (postN0 : Nat) (postSourceTag : FineSourceTag)
    (postGeneratedByS postInScope : Bool) : Prop where
  preLawfulActiveFamily :
    LawfulActiveFamilyAt economy L_t preN0 preSourceTag preGeneratedByS
      preInScope
  activeBefore : M ∈ L_t.support
  supportRemoves : SupportRemovesProbe L_t M L_t'
  retirementLedgerUpdateRecorded :
    ∃ entry : LedgerEntry,
      entry ∈ S.Lambda_S.ledgerEntries ∧ economy.RetirementRecordEntry entry M
  budgetAdmissible :
    economy.BudgetAdmissible (ProbeMove.retirement L_t M L_t')
  postLawfulActiveFamily :
    LawfulActiveFamilyAt economy L_t' postN0 postSourceTag postGeneratedByS
      postInScope

theorem lawfulAcquisition_requires_acquisitionStrict
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    {economy : ProbeEconomy S Probe XiFamily}
    {L_t L_t' : ActiveFamily Probe XiFamily} {M : Probe}
    {preN0 postN0 : Nat}
    {preSourceTag postSourceTag : FineSourceTag}
    {preGeneratedByS preInScope postGeneratedByS postInScope : Bool}
    (h :
      LawfulAcquisition economy L_t M L_t'
        preN0 preSourceTag preGeneratedByS preInScope
        postN0 postSourceTag postGeneratedByS postInScope) :
    AcquisitionStrict economy.sameFamilySaturated L_t M :=
  h.strict

theorem not_lawfulAcquisition_of_sameFamilySaturated
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    {economy : ProbeEconomy S Probe XiFamily}
    {L_t L_t' : ActiveFamily Probe XiFamily} {M : Probe}
    {preN0 postN0 : Nat}
    {preSourceTag postSourceTag : FineSourceTag}
    {preGeneratedByS preInScope postGeneratedByS postInScope : Bool}
    (hsaturated : SameFamilySaturated economy.sameFamilySaturated L_t M) :
    ¬ LawfulAcquisition economy L_t M L_t'
      preN0 preSourceTag preGeneratedByS preInScope
      postN0 postSourceTag postGeneratedByS postInScope := by
  intro h
  exact h.strict hsaturated

theorem lawfulAllocation_support_eq
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    {economy : ProbeEconomy S Probe XiFamily}
    {L_t L_t' : ActiveFamily Probe XiFamily}
    {preN0 postN0 : Nat}
    {preSourceTag postSourceTag : FineSourceTag}
    {preGeneratedByS preInScope postGeneratedByS postInScope : Bool}
    (h : LawfulAllocation economy L_t L_t'
      preN0 preSourceTag preGeneratedByS preInScope
      postN0 postSourceTag postGeneratedByS postInScope) :
    L_t'.support = L_t.support :=
  h.supportUnchanged

theorem lawfulAllocation_no_new_active_probe
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    {economy : ProbeEconomy S Probe XiFamily}
    {L_t L_t' : ActiveFamily Probe XiFamily} {M : Probe}
    {preN0 postN0 : Nat}
    {preSourceTag postSourceTag : FineSourceTag}
    {preGeneratedByS preInScope postGeneratedByS postInScope : Bool}
    (h : LawfulAllocation economy L_t L_t'
      preN0 preSourceTag preGeneratedByS preInScope
      postN0 postSourceTag postGeneratedByS postInScope)
    (hnotActive : M ∉ L_t.support) :
    M ∉ L_t'.support := by
  intro hactiveAfter
  rw [h.supportUnchanged] at hactiveAfter
  exact hnotActive hactiveAfter

theorem lawfulRetirement_requires_active
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    {economy : ProbeEconomy S Probe XiFamily}
    {L_t L_t' : ActiveFamily Probe XiFamily} {M : Probe}
    {preN0 postN0 : Nat}
    {preSourceTag postSourceTag : FineSourceTag}
    {preGeneratedByS preInScope postGeneratedByS postInScope : Bool}
    (h : LawfulRetirement economy L_t M L_t'
      preN0 preSourceTag preGeneratedByS preInScope
      postN0 postSourceTag postGeneratedByS postInScope) :
    M ∈ L_t.support :=
  h.activeBefore

theorem lawfulRetirement_probe_absent_after
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Probe : Type z} {XiFamily : Type z'}
    {economy : ProbeEconomy S Probe XiFamily}
    {L_t L_t' : ActiveFamily Probe XiFamily} {M : Probe}
    {preN0 postN0 : Nat}
    {preSourceTag postSourceTag : FineSourceTag}
    {preGeneratedByS preInScope postGeneratedByS postInScope : Bool}
    (h : LawfulRetirement economy L_t M L_t'
      preN0 preSourceTag preGeneratedByS preInScope
      postN0 postSourceTag postGeneratedByS postInScope) :
    M ∉ L_t'.support := by
  intro hactiveAfter
  have hmem := (h.supportRemoves.2 M).mp hactiveAfter
  exact hmem.2 rfl

section XiInstantiation

def XiSameFamilySaturated {e y z m : Nat}
    (C : Mat e e) (D : Mat z e)
    (KLLdagger : Mat y y) (KMMLdagger : Mat m m)
    (extendedResidual : Mat z z)
    (L : Mat y e) (M : Mat m e) : Prop :=
  ∃ B : Mat m y,
    ∃ _ :
      extendedResidual =
        matSub
          (adequacyResidual C L D KLLdagger)
          (matMul
            (matMul (conditionalCurrencyDM_L C L D M KLLdagger) KMMLdagger)
            (conditionalCurrencyMD_L C L D M KLLdagger)),
      M = matMul B L ∧
        conditionalCurrencyDM_L C L D M KLLdagger = zeroMat z m ∧
        extendedResidual = adequacyResidual C L D KLLdagger

theorem xi_sameFamilySaturated_of_sameFamilySaturation {e y z m : Nat}
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
    XiSameFamilySaturated C D KLLdagger KMMLdagger extendedResidual L M := by
  exact
    ⟨B, hChainRule, hM_factors, hDML_zero,
      SixBirdsMetaMath.Xi.StrictExtension.sameFamilySaturation
        C L D M KLLdagger KMMLdagger B extendedResidual
        hChainRule hM_factors hDML_zero⟩

theorem xi_sameFamilySaturated_not_acquisitionStrict {e y z m : Nat}
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
    ¬ AcquisitionStrict
      (XiSameFamilySaturated C D KLLdagger KMMLdagger extendedResidual)
      L M := by
  intro hstrict
  exact hstrict
    (xi_sameFamilySaturated_of_sameFamilySaturation
      C L D M KLLdagger KMMLdagger B extendedResidual
      hChainRule hM_factors hDML_zero)

end XiInstantiation

end SixBirdsFoundationsV
