import FoundationsVII.Models.Finite.Detector
import FoundationsVII.Models.Finite.Serialization

/-!
# Aggregate finite regression theorems

Theorems in this module are decidable facts about the frozen 24-scenario and
27-countermodel reference family.  They have no force beyond that declared
finite family.
-/

namespace FoundationsVII.Models.Finite

theorem frozen_scenario_census : allScenarios.length = 24 := by decide

theorem frozen_countermodel_census : allCountermodels.length = 27 := by decide

theorem frozen_scenario_assay_passes :
    allScenarios.all scenarioPass = true := by decide

theorem frozen_countermodel_assay_passes :
    allCountermodels.all countermodelPass = true := by decide

theorem frozen_status_regression_has_24_distinct_expected_statuses :
    (allScenarios.map ScenarioFixture.expectedStatus).eraseDups.length = 24 := by
  decide

theorem detector_covers_entire_frozen_family :
    phase1DetectorContract.frozenScenarioIds =
        allScenarios.map ScenarioFixture.fixtureId ∧
    phase1DetectorContract.frozenCountermodelIds =
        allCountermodels.map CountermodelFixture.fixtureId := by
  exact ⟨rfl, rfl⟩

end FoundationsVII.Models.Finite
