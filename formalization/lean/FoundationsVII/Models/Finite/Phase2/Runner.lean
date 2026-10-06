import FoundationsVII.Models.Finite.Phase2.AdmissionEnvelope

open FoundationsVII.Models.Finite.Phase2

private def line (familyId : String) (raw canonical accepted : Nat) : String :=
  "{\"family_id\":\"" ++ familyId ++ "\",\"raw_cardinality\":" ++
    toString raw ++ ",\"canonical_cardinality\":" ++ toString canonical ++
    ",\"accepted_cardinality\":" ++ toString accepted ++
    ",\"rejected_cardinality\":" ++ toString (canonical - accepted) ++ "}"

def main : IO Unit := do
  IO.println (line "P2-E01" allAccessCases.length allAccessCases.length
    (allAccessCases.filter accessCoherent).length)
  IO.println (line "P2-E02" allTransitionCases.length allTransitionCases.length
    (allTransitionCases.filter transitionCoherent).length)
  IO.println (line "P2-E03" allBootstrapCases.length allBootstrapCases.length
    (allBootstrapCases.filter bootstrapLaw).length)
  IO.println (line "P2-E04" allCommitmentCases.length allCommitmentCases.length
    (allCommitmentCases.filter commitmentLaw).length)
  IO.println (line "P2-E05" (allOriginCases.length * 2) allOriginCases.length
    (allOriginCases.filter originLaw).length)
  IO.println (line "P2-E06" allTotalityCases.length allTotalityCases.length
    (allTotalityCases.filter totalityLaw).length)
  IO.println (line "P2-E07" allHorizonCases.length allHorizonCases.length
    (allHorizonCases.filter horizonLaw).length)
  IO.println (line "P2-E08" allObserverCases.length allObserverCases.length
    (allObserverCases.filter observerLaw).length)
  IO.println (line "P2-E09" allSettlementCases.length allSettlementCases.length
    (allSettlementCases.filter settlementLaw).length)
