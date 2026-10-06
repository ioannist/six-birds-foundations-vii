import FoundationsVII.Prior.Metadata
import SixBirdsFoundationsVI.Laws.G8OdometerAbelianization

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.caseB_confluent_runs_share_final
def adapter_ft14_caseb_confluent_runs_share_final_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-14-01"
    formalizationTarget := "FT14"
    sourceModule := "SixBirdsFoundationsVI.Laws.G8OdometerAbelianization"
    sourceDeclaration := "SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.caseB_confluent_runs_share_final"
    sourceType := "theorem SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.caseB_confluent_runs_share_final"
    targetType := "finite confluence records over FoundationsVII.InteractionRecord"
    preservedHypotheses := ["declared finite run system and confluence/nonconfluence hypotheses"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Confluence and critical-pair finite models", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

#check SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.caseD_nonconfluent_witness
def adapter_ft14_cased_nonconfluent_witness_02 : AdapterMetadata :=
  { adapterId := "FVII-ADP-14-02"
    formalizationTarget := "FT14"
    sourceModule := "SixBirdsFoundationsVI.Laws.G8OdometerAbelianization"
    sourceDeclaration := "SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.caseD_nonconfluent_witness"
    sourceType := "theorem SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.caseD_nonconfluent_witness"
    targetType := "finite confluence records over FoundationsVII.InteractionRecord"
    preservedHypotheses := ["declared finite run system and confluence/nonconfluence hypotheses"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Confluence and critical-pair finite models", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
