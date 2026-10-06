import FoundationsVII.Prior.Metadata
import SixBirdsFoundationsV.Laws.E6E9PricedAccess
import SixBirdsFoundationsV.Laws.E4RepairCompilation

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsFoundationsV.BudgetFeasible
def adapter_ft09_budgetfeasible_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-09-01"
    formalizationTarget := "FT09"
    sourceModule := "SixBirdsFoundationsV.Laws.E6E9PricedAccess"
    sourceDeclaration := "SixBirdsFoundationsV.BudgetFeasible"
    sourceType := "def SixBirdsFoundationsV.BudgetFeasible"
    targetType := "FoundationsVII.JoinObstruction / FoundationsVII.BudgetLedger"
    preservedHypotheses := ["budget feasibility premises", "typed obstruction status"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Join obstruction and budget record", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

#check SixBirdsFoundationsV.ObstructionStatusRecord
def adapter_ft09_obstructionstatusrecord_02 : AdapterMetadata :=
  { adapterId := "FVII-ADP-09-02"
    formalizationTarget := "FT09"
    sourceModule := "SixBirdsFoundationsV.Laws.E4RepairCompilation"
    sourceDeclaration := "SixBirdsFoundationsV.ObstructionStatusRecord"
    sourceType := "structure SixBirdsFoundationsV.ObstructionStatusRecord"
    targetType := "FoundationsVII.JoinObstruction / FoundationsVII.BudgetLedger"
    preservedHypotheses := ["budget feasibility premises", "typed obstruction status"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Join obstruction and budget record", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
