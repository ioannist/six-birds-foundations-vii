import FoundationsVII.Models.Finite.Phase5.All

open FoundationsVII.Models.Finite
open FoundationsVII.Models.Finite.Phase5

private def line (familyId : String) (raw canonical accepted : Nat) : String :=
  "{\"family_id\":\"" ++ familyId ++ "\",\"raw_cardinality\":" ++
    toString raw ++ ",\"canonical_cardinality\":" ++ toString canonical ++
    ",\"accepted_cardinality\":" ++ toString accepted ++
    ",\"rejected_cardinality\":" ++ toString (canonical - accepted) ++ "}"

private def passLine (kind id : String) (passed : Bool) : String :=
  "{\"kind\":\"" ++ kind ++ "\",\"id\":\"" ++ id ++
    "\",\"pass\":" ++ (if passed then "true" else "false") ++ "}"

def main : IO Unit := do
  IO.println (line "P5-E01" allProspectiveJoinCases.length allProspectiveJoinCases.length
    (allProspectiveJoinCases.filter prospectiveJoinLaw).length)
  IO.println (line "P5-E02" allSourceBudgetCapacityCases.length allSourceBudgetCapacityCases.length
    (allSourceBudgetCapacityCases.filter sourceBudgetCapacityLaw).length)
  IO.println (line "P5-E03" allCertifiedNoninteractionCases.length allCertifiedNoninteractionCases.length
    (allCertifiedNoninteractionCases.filter certifiedNoninteractionLaw).length)
  IO.println (line "P5-E04" allResidualEnablementCases.length allResidualEnablementCases.length
    (allResidualEnablementCases.filter residualEnablementLaw).length)
  IO.println (line "P5-E05" allRefinementDescentCases.length allRefinementDescentCases.length
    (allRefinementDescentCases.filter refinementDescentLaw).length)
  IO.println (line "P5-E06" allNoFreeJoinCases.length allNoFreeJoinCases.length
    (allNoFreeJoinCases.filter noFreeJoinLaw).length)
  IO.println (line "P5-E07" allHolonomyArrowCases.length allHolonomyArrowCases.length
    (allHolonomyArrowCases.filter holonomyArrowLaw).length)
  IO.println (line "P5-E08" allNegativeForceCases.length allNegativeForceCases.length
    (allNegativeForceCases.filter negativeForceLaw).length)
  IO.println (line "P5-E09" allObserverEndogenyCases.length allObserverEndogenyCases.length
    (allObserverEndogenyCases.filter observerEndogenyLaw).length)
  IO.println (line "P5-E10" allRawThreeDomainConfluenceCases.length allThreeDomainConfluenceCases.length
    (allThreeDomainConfluenceCases.filter threeDomainConfluenceLaw).length)
  IO.println (line "P5-E11" allIntegratedDomainCases.length allIntegratedDomainCases.length
    (allIntegratedDomainCases.filter integratedDomainLaw).length)
  for fixture in allScenarios do
    IO.println (passLine "scenario" fixture.fixtureId (scenarioPass fixture))
  for fixture in allCountermodels do
    IO.println (passLine "countermodel" fixture.fixtureId (countermodelPass fixture))
