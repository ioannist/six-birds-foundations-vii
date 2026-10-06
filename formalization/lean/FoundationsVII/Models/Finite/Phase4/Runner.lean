import FoundationsVII.Models.Finite.Phase4.All

open FoundationsVII.Models.Finite.Phase4

private def line (familyId : String) (raw canonical accepted : Nat) : String :=
  "{\"family_id\":\"" ++ familyId ++ "\",\"raw_cardinality\":" ++
    toString raw ++ ",\"canonical_cardinality\":" ++ toString canonical ++
    ",\"accepted_cardinality\":" ++ toString accepted ++
    ",\"rejected_cardinality\":" ++ toString (canonical - accepted) ++ "}"

private def passLine (kind id : String) (passed : Bool) : String :=
  "{\"kind\":\"" ++ kind ++ "\",\"id\":\"" ++ id ++
    "\",\"pass\":" ++ (if passed then "true" else "false") ++ "}"

def main : IO Unit := do
  IO.println (line "P4-E01" allAttributionCases.length allAttributionCases.length
    (allAttributionCases.filter attributionLaw).length)
  IO.println (line "P4-E02" allEndogenousCases.length allEndogenousCases.length
    (allEndogenousCases.filter endogenousLaw).length)
  IO.println (line "P4-E03" allBirthCases.length allBirthCases.length
    (allBirthCases.filter birthLaw).length)
  IO.println (line "P4-E04" allTransmissionCases.length allTransmissionCases.length
    (allTransmissionCases.filter transmissionLaw).length)
  IO.println (line "P4-E05" allSeparationCases.length allSeparationCases.length
    (allSeparationCases.filter separationLaw).length)
  IO.println (line "P4-E06" allCompositionCases.length allCompositionCases.length
    (allCompositionCases.filter compositionLaw).length)
  IO.println (line "P4-E07" allConfluenceCases.length allConfluenceCases.length
    (allConfluenceCases.filter confluenceLaw).length)
  IO.println (line "P4-E08" allSeedCases.length allSeedCases.length
    (allSeedCases.filter seedLaw).length)
  IO.println (line "P4-E09" allHolonomyCases.length allHolonomyCases.length
    (allHolonomyCases.filter holonomyLaw).length)
  IO.println (line "P4-E10" allArrowCases.length allArrowCases.length
    (allArrowCases.filter arrowLaw).length)
  IO.println (line "P4-E11" allCrossTimeCases.length allCrossTimeCases.length
    (allCrossTimeCases.filter crossTimeLaw).length)
  IO.println (line "P4-E12" allAlgebraCases.length allAlgebraCases.length
    (allAlgebraCases.filter algebraLaw).length)
  for scenario in phase4Scenarios do
    IO.println (passLine "scenario" scenario.scenarioId (scenarioPass scenario))
  for check in phase4Countermodels do
    IO.println (passLine "countermodel" check.countermodelId
      (countermodelPass check))
