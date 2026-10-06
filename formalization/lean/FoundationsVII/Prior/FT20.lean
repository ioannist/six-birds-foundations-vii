import FoundationsVII.Prior.Metadata
import SixBirdsFoundationsV.Laws.E5ReclosureCollapse
import Xi.Obstruction

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsFoundationsV.ResidualStatusRecord
def adapter_ft20_residualstatusrecord_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-20-01"
    formalizationTarget := "FT20"
    sourceModule := "SixBirdsFoundationsV.Laws.E5ReclosureCollapse"
    sourceDeclaration := "SixBirdsFoundationsV.ResidualStatusRecord"
    sourceType := "structure SixBirdsFoundationsV.ResidualStatusRecord"
    targetType := "FoundationsVII.JoinObstruction / finite reference-world semantics"
    preservedHypotheses := ["residual status / adequacy-defect witness and exact carrier"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Residual/needle and finite-world semantics", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

#check SixBirdsMetaMath.Xi.Obstruction.blindSpotWitness
def adapter_ft20_blindspotwitness_02 : AdapterMetadata :=
  { adapterId := "FVII-ADP-20-02"
    formalizationTarget := "FT20"
    sourceModule := "Xi.Obstruction"
    sourceDeclaration := "SixBirdsMetaMath.Xi.Obstruction.blindSpotWitness"
    sourceType := "theorem SixBirdsMetaMath.Xi.Obstruction.blindSpotWitness"
    targetType := "FoundationsVII.JoinObstruction / finite reference-world semantics"
    preservedHypotheses := ["residual status / adequacy-defect witness and exact carrier"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Residual/needle and finite-world semantics", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
