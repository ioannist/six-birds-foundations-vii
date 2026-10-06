import FoundationsVII.Models.Finite.Phase3.ContactJoinEnvelope

/-!
# Phase-3 scenario and countermodel checks

These profiles mirror the frozen TTW-S05--S15 and TTW-S24 evidence flags.
-/

namespace FoundationsVII.Models.Finite.Phase3

inductive Phase3Status where
  | independenceGateFailed
  | contactWithoutJoin
  | commonRefinementNonstrict
  | strictJoin
  | retentionObstruction
  | budgetObstruction
  | sourceObstruction
  | noEvidencedContact
  | certifiedNoninteraction
  | fakeJoinScheduling
  | fakeJoinRelabeling
  | refinementDestroysJoin
  | unpricedObserver
  deriving Repr, DecidableEq, BEq, Inhabited

structure Phase3Profile where
  contact : Bool := false
  composite : Bool := false
  antiProduct : Bool := false
  retention : Bool := true
  budgetOk : Bool := true
  sourceIndependent : Bool := true
  commonRefinement : Bool := false
  sameSource : Bool := false
  resemblanceOnly : Bool := false
  closedFamily : Bool := false
  detectorPower : Bool := false
  schedulingOnly : Bool := false
  relabelOnly : Bool := false
  parentRefined : Bool := false
  joinDestroyed : Bool := false
  newResidual : Bool := false
  observerUsed : Bool := false
  observerPriced : Bool := true
  deriving Repr, DecidableEq, BEq, Inhabited

def classifyPhase3 (p : Phase3Profile) : Phase3Status :=
  if p.observerUsed && !p.observerPriced then .unpricedObserver
  else if p.closedFamily && p.detectorPower && !p.contact then .certifiedNoninteraction
  else if p.schedulingOnly then .fakeJoinScheduling
  else if p.relabelOnly then .fakeJoinRelabeling
  else if p.joinDestroyed && p.parentRefined then .refinementDestroysJoin
  else if !p.contact then .noEvidencedContact
  else if p.sameSource || p.resemblanceOnly then .independenceGateFailed
  else if p.composite && p.antiProduct && !p.retention then .retentionObstruction
  else if p.composite && p.antiProduct && !p.budgetOk then .budgetObstruction
  else if p.composite && p.antiProduct && !p.sourceIndependent then .sourceObstruction
  else if p.commonRefinement && p.composite && !p.antiProduct then
    .commonRefinementNonstrict
  else if p.contact && p.composite && p.antiProduct && p.retention &&
      p.budgetOk && p.sourceIndependent then .strictJoin
  else .contactWithoutJoin

structure Phase3Scenario where
  scenarioId : String
  profile : Phase3Profile
  expected : Phase3Status
  deriving Repr, DecidableEq, BEq, Inhabited

def scenarioPass (scenario : Phase3Scenario) : Bool :=
  classifyPhase3 scenario.profile == scenario.expected

def phase3Scenarios : List Phase3Scenario :=
  [ { scenarioId := "TTW-S05",
      profile := { contact := true, composite := true, sameSource := true,
                   resemblanceOnly := true }, expected := .independenceGateFailed },
    { scenarioId := "TTW-S06", profile := { contact := true },
      expected := .contactWithoutJoin },
    { scenarioId := "TTW-S07",
      profile := { contact := true, composite := true, commonRefinement := true,
                   antiProduct := false }, expected := .commonRefinementNonstrict },
    { scenarioId := "TTW-S08",
      profile := { contact := true, composite := true, antiProduct := true,
                   retention := true, budgetOk := true, sourceIndependent := true },
      expected := .strictJoin },
    { scenarioId := "TTW-S09",
      profile := { contact := true, composite := true, antiProduct := true,
                   retention := false }, expected := .retentionObstruction },
    { scenarioId := "TTW-S10",
      profile := { contact := true, composite := true, antiProduct := true,
                   budgetOk := false }, expected := .budgetObstruction },
    { scenarioId := "TTW-S11",
      profile := { contact := true, composite := true, antiProduct := true,
                   sourceIndependent := false }, expected := .sourceObstruction },
    { scenarioId := "TTW-S12", profile := {}, expected := .noEvidencedContact },
    { scenarioId := "TTW-S13",
      profile := { closedFamily := true, detectorPower := true },
      expected := .certifiedNoninteraction },
    { scenarioId := "TTW-S14",
      profile := { contact := true, composite := true, schedulingOnly := true },
      expected := .fakeJoinScheduling },
    { scenarioId := "TTW-S15",
      profile := { contact := true, composite := true, relabelOnly := true },
      expected := .fakeJoinRelabeling },
    { scenarioId := "TTW-S24",
      profile := { contact := true, parentRefined := true, joinDestroyed := true,
                   newResidual := true }, expected := .refinementDestroysJoin } ]

theorem phase3_scenario_count : phase3Scenarios.length = 12 := by decide

theorem all_phase3_scenarios_pass : phase3Scenarios.all scenarioPass = true := by decide

structure Phase3CountermodelCheck where
  countermodelId : String
  scenario : Phase3Scenario
  deriving Repr, DecidableEq, BEq

def countermodelPass (check : Phase3CountermodelCheck) : Bool :=
  scenarioPass check.scenario

private def scenario05 : Phase3Scenario := phase3Scenarios[0]!
private def scenario06 : Phase3Scenario := phase3Scenarios[1]!
private def scenario07 : Phase3Scenario := phase3Scenarios[2]!
private def scenario08 : Phase3Scenario := phase3Scenarios[3]!
private def scenario09 : Phase3Scenario := phase3Scenarios[4]!
private def scenario10 : Phase3Scenario := phase3Scenarios[5]!
private def scenario11 : Phase3Scenario := phase3Scenarios[6]!
private def scenario12 : Phase3Scenario := phase3Scenarios[7]!
private def scenario13 : Phase3Scenario := phase3Scenarios[8]!
private def scenario14 : Phase3Scenario := phase3Scenarios[9]!
private def scenario15 : Phase3Scenario := phase3Scenarios[10]!
private def scenario24 : Phase3Scenario := phase3Scenarios[11]!

/-- TTW-S22 is a source control for CM-21 and is intentionally not counted
among the twelve primary Phase-3 scenario assignments. -/
private def scenario22 : Phase3Scenario :=
  { scenarioId := "TTW-S22",
    profile := { observerUsed := true, observerPriced := false },
    expected := .unpricedObserver }

theorem phase3_source_control_22_pass : scenarioPass scenario22 = true := by decide

def phase3Countermodels : List Phase3CountermodelCheck :=
  [ { countermodelId := "CM-01", scenario := scenario05 },
    { countermodelId := "CM-02", scenario := scenario12 },
    { countermodelId := "CM-03", scenario := scenario06 },
    { countermodelId := "CM-04", scenario := scenario14 },
    { countermodelId := "CM-05", scenario := scenario09 },
    { countermodelId := "CM-13", scenario := scenario07 },
    { countermodelId := "CM-14", scenario := scenario15 },
    { countermodelId := "CM-15", scenario := scenario15 },
    { countermodelId := "CM-16", scenario := scenario08 },
    { countermodelId := "CM-21", scenario := scenario22 },
    { countermodelId := "CM-22", scenario := scenario24 },
    { countermodelId := "CM-25", scenario := scenario24 },
    { countermodelId := "CM-26", scenario := scenario05 },
    { countermodelId := "CM-27", scenario := scenario13 } ]

theorem phase3_countermodel_count : phase3Countermodels.length = 14 := by decide

theorem all_phase3_countermodels_pass :
    phase3Countermodels.all countermodelPass = true := by decide

end FoundationsVII.Models.Finite.Phase3
