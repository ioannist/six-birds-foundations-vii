import FoundationsVII.Prior.Metadata
import SixBirdsFoundationsV.Laws.E6E9PricedAccess

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsFoundationsV.BindingExposureBudget
def adapter_ft16_bindingexposurebudget_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-16-01"
    formalizationTarget := "FT16"
    sourceModule := "SixBirdsFoundationsV.Laws.E6E9PricedAccess"
    sourceDeclaration := "SixBirdsFoundationsV.BindingExposureBudget"
    sourceType := "def SixBirdsFoundationsV.BindingExposureBudget"
    targetType := "FoundationsVII.BudgetLedger / FoundationsVII.ObserverOccupancyRecord"
    preservedHypotheses := ["binding budget/positive-cost premises"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Budget and observer occupancy", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

#check SixBirdsFoundationsV.PositiveAccessMoveCosts
def adapter_ft16_positiveaccessmovecosts_02 : AdapterMetadata :=
  { adapterId := "FVII-ADP-16-02"
    formalizationTarget := "FT16"
    sourceModule := "SixBirdsFoundationsV.Laws.E6E9PricedAccess"
    sourceDeclaration := "SixBirdsFoundationsV.PositiveAccessMoveCosts"
    sourceType := "def SixBirdsFoundationsV.PositiveAccessMoveCosts"
    targetType := "FoundationsVII.BudgetLedger / FoundationsVII.ObserverOccupancyRecord"
    preservedHypotheses := ["binding budget/positive-cost premises"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Budget and observer occupancy", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
