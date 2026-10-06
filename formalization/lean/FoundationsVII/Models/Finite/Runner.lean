import FoundationsVII.Models.Finite.Serialization

open FoundationsVII.Models.Finite

private def boolJson (value : Bool) : String :=
  if value then "true" else "false"

private def scenarioLine (fixture : ScenarioFixture) : String :=
  let observed := (evaluate fixture.flags).1
  "{\"fixture_id\":\"" ++ fixture.fixtureId ++
  "\",\"observed_status\":\"" ++ statusName observed ++
  "\",\"all_pass\":" ++ boolJson (scenarioPass fixture) ++ "}"

private def countermodelLine (fixture : CountermodelFixture) : String :=
  let observed := (evaluate fixture.scenario.flags).1
  "{\"fixture_id\":\"" ++ fixture.fixtureId ++
  "\",\"observed_status\":\"" ++ statusName observed ++
  "\",\"all_pass\":" ++ boolJson (countermodelPass fixture) ++ "}"

def main : IO Unit := do
  for fixture in allScenarios do
    IO.println (scenarioLine fixture)
  for fixture in allCountermodels do
    IO.println (countermodelLine fixture)
