import FoundationsVII.Models.Finite.Regression

/-!
# Final frozen fixture replay

The final release rechecks the complete 24-scenario and 27-countermodel corpus,
not only the phase-specific subsets used during construction.
-/

namespace FoundationsVII.Models.Finite.Phase5

open FoundationsVII.Models.Finite

theorem final_frozen_scenario_census : allScenarios.length = 24 := by decide

theorem final_frozen_countermodel_census : allCountermodels.length = 27 := by decide

theorem final_all_scenarios_pass : allScenarios.all scenarioPass = true := by decide

theorem final_all_countermodels_pass : allCountermodels.all countermodelPass = true := by decide

theorem final_fixture_identifiers_are_unique :
    (allScenarios.map ScenarioFixture.fixtureId).Nodup ∧
    (allCountermodels.map CountermodelFixture.fixtureId).Nodup := by decide

end FoundationsVII.Models.Finite.Phase5
