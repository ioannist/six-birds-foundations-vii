import FoundationsVII.Models.Finite.Phase3.All

open FoundationsVII.Models.Finite.Phase3

private def line (familyId : String) (raw canonical accepted : Nat) : String :=
  "{\"family_id\":\"" ++ familyId ++ "\",\"raw_cardinality\":" ++
    toString raw ++ ",\"canonical_cardinality\":" ++ toString canonical ++
    ",\"accepted_cardinality\":" ++ toString accepted ++
    ",\"rejected_cardinality\":" ++ toString (canonical - accepted) ++ "}"

private def passLine (kind id : String) (passed : Bool) : String :=
  "{\"kind\":\"" ++ kind ++ "\",\"id\":\"" ++ id ++
    "\",\"pass\":" ++ (if passed then "true" else "false") ++ "}"

def main : IO Unit := do
  IO.println (line "P3-E01" allContactTransportCases.length
    allContactTransportCases.length
    (allContactTransportCases.filter contactTransportLaw).length)
  IO.println (line "P3-E02" (allJoinStatusCases.length * 2)
    allJoinStatusCases.length
    (allJoinStatusCases.filter joinStatusLaw).length)
  IO.println (line "P3-E03" (allStrictnessCases.length * 2)
    allStrictnessCases.length
    (allStrictnessCases.filter strictnessLaw).length)
  IO.println (line "P3-E04" allSourceLineageCases.length
    allSourceLineageCases.length
    (allSourceLineageCases.filter sourceLineageLaw).length)
  IO.println (line "P3-E05" allPaymentCases.length allPaymentCases.length
    (allPaymentCases.filter paymentLaw).length)
  IO.println (line "P3-E06" allCapacityCases.length allCapacityCases.length
    (allCapacityCases.filter capacityLaw).length)
  IO.println (line "P3-E07" allRefinementCases.length allRefinementCases.length
    (allRefinementCases.filter refinementLaw).length)
  IO.println (line "P3-E08" allResidualCases.length allResidualCases.length
    (allResidualCases.filter residualLaw).length)
  IO.println (line "P3-E09" allNoninteractionCases.length
    allNoninteractionCases.length
    (allNoninteractionCases.filter noninteractionLaw).length)
  IO.println (line "P3-E10" allCategoricalCases.length allCategoricalCases.length
    (allCategoricalCases.filter categoricalLaw).length)
  IO.println (line "P3-E11" allMeasureCases.length allMeasureCases.length
    (allMeasureCases.filter measureLaw).length)
  for scenario in phase3Scenarios do
    IO.println (passLine "scenario" scenario.scenarioId (scenarioPass scenario))
  for check in phase3Countermodels do
    IO.println (passLine "countermodel" check.countermodelId
      (countermodelPass check))
