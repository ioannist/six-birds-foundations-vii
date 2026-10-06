import FoundationsVII.Models.Finite.Countermodels

/-!
# Terminal finite detector contract for VII-C025

The contract freezes the complete Step-3 fixture family and the mandatory
control classes.  Passing this finite assay does not assert an unbounded
interaction law.
-/

namespace FoundationsVII.Models.Finite

private def detectorAuditEntry : FoundationsVII.AuditEntry :=
  { auditId := 2501
    disposition := .accepted
    subject := "VII-C025"
    message := "Twenty-four scenarios and twenty-seven countermodels frozen before Phase-1 evaluation."
    sourceLocation := "readiness/two_theory_world/" }

private def detectorAudit : FoundationsVII.AuditRecord :=
  { entries := [detectorAuditEntry] }

def phase1DetectorContract : FoundationsVII.DetectorContract :=
  { detectorId := 25
    signalDescription := "A frozen fixture satisfies its typed premises and declared signal assertions."
    nullDescription := "A matched fixture removes the principal witness while preserving unrelated fields."
    falsifierDescription := "Observed status or any declared assertion differs from its frozen expectation."
    signalCaseIds := ["TTW-S01", "TTW-S08", "TTW-S21"]
    nullCaseIds := ["TTW-S02", "TTW-S06", "TTW-S12", "TTW-S19", "TTW-S20"]
    falsifierCaseIds := allCountermodels.map CountermodelFixture.fixtureId
    sameSourceControls := ["TTW-S05", "CM-01", "CM-26"]
    noContactControls := ["TTW-S12", "TTW-S13", "CM-02", "CM-27"]
    schedulingControls := ["TTW-S14", "CM-04"]
    relabelingControls := ["TTW-S15", "CM-16"]
    falsePositiveCost := 10
    falseNegativeCost := 1
    frozenScenarioIds := allScenarios.map ScenarioFixture.fixtureId
    frozenCountermodelIds := allCountermodels.map CountermodelFixture.fixtureId
    evidenceAudit := detectorAudit }

theorem phase1_detector_contract_wellFormed :
    FoundationsVII.DetectorContract.WellFormed phase1DetectorContract := by
  decide

theorem phase1_detector_frozen_complete :
    FoundationsVII.DetectorContract.FrozenComplete phase1DetectorContract 24 27 := by
  decide

theorem phase1_detector_has_24_scenarios :
    phase1DetectorContract.frozenScenarioIds.length = 24 := by
  exact phase1_detector_frozen_complete.1

theorem phase1_detector_has_27_countermodels :
    phase1DetectorContract.frozenCountermodelIds.length = 27 := by
  exact phase1_detector_frozen_complete.2.1

theorem phase1_detector_false_positive_cost_exceeds_false_negative :
    phase1DetectorContract.falseNegativeCost <
      phase1DetectorContract.falsePositiveCost := by
  decide

theorem phase1_detector_false_positive_cost_is_asymmetric :
    phase1DetectorContract.falsePositiveCost ≠
      phase1DetectorContract.falseNegativeCost := by
  decide

end FoundationsVII.Models.Finite
