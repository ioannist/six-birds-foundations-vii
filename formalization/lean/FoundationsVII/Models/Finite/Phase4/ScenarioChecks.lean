import FoundationsVII.Models.Finite.Phase4.DynamicsEnvelope

/-!
# Phase-4 scenario and countermodel checks

These profiles mirror the frozen Phase-4 scenario slice and its assigned
countermodels. They are finite controls, not universal theorems.
-/

namespace FoundationsVII.Models.Finite.Phase4

inductive Phase4Status where
  | externalEnablement
  | prospectiveSeparation
  | relationOnlyContact
  | orderResidue
  | holonomyZeroArrow
  | drivenArrow
  | reachableNonoccurrent
  | occurrentEvent
  | seedDependentRefinement
  deriving Repr, DecidableEq, BEq, Inhabited

structure Phase4Profile where
  neutralSeed : Bool := false
  generatorReachable : Bool := false
  prospective : Bool := false
  contact : Bool := false
  composite : Bool := false
  orderResidue : Bool := false
  holonomy : Bool := false
  drive : Bool := false
  reachable : Bool := false
  fired : Bool := false
  parentRefined : Bool := false
  joinDestroyed : Bool := false
  newResidual : Bool := false
  deriving Repr, DecidableEq, BEq, Inhabited

def classifyPhase4 (profile : Phase4Profile) : Phase4Status :=
  if profile.holonomy && profile.drive then .drivenArrow
  else if profile.holonomy then .holonomyZeroArrow
  else if profile.orderResidue then .orderResidue
  else if profile.parentRefined && profile.joinDestroyed then .seedDependentRefinement
  else if profile.neutralSeed && profile.generatorReachable && profile.fired then
    .externalEnablement
  else if profile.prospective && profile.fired then .prospectiveSeparation
  else if profile.contact && !profile.composite then .relationOnlyContact
  else if profile.reachable && !profile.fired then .reachableNonoccurrent
  else .occurrentEvent

structure Phase4Scenario where
  scenarioId : String
  profile : Phase4Profile
  expected : Phase4Status
  deriving Repr, DecidableEq, BEq, Inhabited

def scenarioPass (scenario : Phase4Scenario) : Bool :=
  classifyPhase4 scenario.profile == scenario.expected

def phase4Scenarios : List Phase4Scenario :=
  [ { scenarioId := "TTW-S02",
      profile := { neutralSeed := true, generatorReachable := true,
                   reachable := true, fired := true }, expected := .externalEnablement },
    { scenarioId := "TTW-S03",
      profile := { prospective := true, reachable := true, fired := true },
      expected := .prospectiveSeparation },
    { scenarioId := "TTW-S06",
      profile := { contact := true, composite := false },
      expected := .relationOnlyContact },
    { scenarioId := "TTW-S16",
      profile := { orderResidue := true }, expected := .orderResidue },
    { scenarioId := "TTW-S17",
      profile := { holonomy := true, drive := false },
      expected := .holonomyZeroArrow },
    { scenarioId := "TTW-S18",
      profile := { holonomy := true, drive := true }, expected := .drivenArrow },
    { scenarioId := "TTW-S20",
      profile := { reachable := true, fired := false },
      expected := .reachableNonoccurrent },
    { scenarioId := "TTW-S21",
      profile := { reachable := true, fired := true }, expected := .occurrentEvent },
    { scenarioId := "TTW-S24",
      profile := { contact := true, parentRefined := true,
                   joinDestroyed := true, newResidual := true },
      expected := .seedDependentRefinement } ]

theorem phase4_scenario_count : phase4Scenarios.length = 9 := by decide

theorem all_phase4_scenarios_pass : phase4Scenarios.all scenarioPass = true := by decide

private def scenario02 : Phase4Scenario := phase4Scenarios[0]!
private def scenario03 : Phase4Scenario := phase4Scenarios[1]!
private def scenario16 : Phase4Scenario := phase4Scenarios[3]!
private def scenario17 : Phase4Scenario := phase4Scenarios[4]!
private def scenario24 : Phase4Scenario := phase4Scenarios[8]!

structure Phase4CountermodelCheck where
  countermodelId : String
  scenario : Phase4Scenario
  requiredFact : String
  deriving Repr, DecidableEq, BEq

def countermodelPass (check : Phase4CountermodelCheck) : Bool :=
  scenarioPass check.scenario

def phase4Countermodels : List Phase4CountermodelCheck :=
  [ { countermodelId := "CM-06", scenario := scenario03,
      requiredFact := "enablement_without_descent" },
    { countermodelId := "CM-07", scenario := scenario03,
      requiredFact := "necessary_but_insufficient" },
    { countermodelId := "CM-10", scenario := scenario17,
      requiredFact := "holonomy_zero_arrow" },
    { countermodelId := "CM-17", scenario := scenario02,
      requiredFact := "theorist_triggered_not_endogenous" },
    { countermodelId := "CM-22", scenario := scenario24,
      requiredFact := "refinement_destroys_join" },
    { countermodelId := "CM-23", scenario := scenario24,
      requiredFact := "seed_dependence" },
    { countermodelId := "CM-24", scenario := scenario16,
      requiredFact := "order_residue" },
    { countermodelId := "CM-25", scenario := scenario24,
      requiredFact := "join_created_residual" } ]

theorem phase4_countermodel_count : phase4Countermodels.length = 8 := by decide

theorem all_phase4_countermodels_pass :
    phase4Countermodels.all countermodelPass = true := by decide

end FoundationsVII.Models.Finite.Phase4
