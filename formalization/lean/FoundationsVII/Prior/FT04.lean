import FoundationsVII.Prior.Metadata
import SixBirdsFoundationsV.Laws.E15OfflineReclosure

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsFoundationsV.SharedBudgetAllocationRecord
def adapter_ft04_sharedbudgetallocationrecord_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-04-01"
    formalizationTarget := "FT04"
    sourceModule := "SixBirdsFoundationsV.Laws.E15OfflineReclosure"
    sourceDeclaration := "SixBirdsFoundationsV.SharedBudgetAllocationRecord"
    sourceType := "structure SixBirdsFoundationsV.SharedBudgetAllocationRecord"
    targetType := "FoundationsVII.ProspectiveCommitment / FoundationsVII.BudgetLedger"
    preservedHypotheses := ["declared timestamps and budget allocation", "source-located allocation record"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Prospective commitment timestamp/budget record", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
