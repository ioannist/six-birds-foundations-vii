import FoundationsVII.Models.Finite.Scenarios

/-! Generated countermodel declarations.  Source: readiness/countermodel_atlas.jsonl -/

namespace FoundationsVII.Models.Finite

def countermodelPass (fixture : CountermodelFixture) : Bool :=
  scenarioPass fixture.scenario &&
  (evaluate fixture.scenario.flags).1 == fixture.expectedStatus

def countermodel01 : CountermodelFixture :=
  { fixtureId := "CM-01"
    name := "Same source but no shared access"
    scenario := scenario05
    expectedStatus := .independenceGateFailed
    shows := "Common origin does not imply shared access or independence."
    candidateIds := ["VII-C005", "VII-C010"] }

theorem countermodel01_passes : countermodelPass countermodel01 = true := by
  decide

def countermodel02 : CountermodelFixture :=
  { fixtureId := "CM-02"
    name := "Common interface without witnessed contact"
    scenario := scenario12
    expectedStatus := .noEvidencedContact
    shows := "Compatibility does not imply contact or non-interaction."
    candidateIds := ["VII-C007", "VII-C008", "VII-C016", "VII-C033"] }

theorem countermodel02_passes : countermodelPass countermodel02 = true := by
  decide

def countermodel03 : CountermodelFixture :=
  { fixtureId := "CM-03"
    name := "Contact without strict joint information"
    scenario := scenario06
    expectedStatus := .contactWithoutJoin
    shows := "Contact does not imply strict join."
    candidateIds := ["VII-C007", "VII-C009", "VII-C036"] }

theorem countermodel03_passes : countermodelPass countermodel03 = true := by
  decide

def countermodel04 : CountermodelFixture :=
  { fixtureId := "CM-04"
    name := "Scheduling-only apparent joint novelty"
    scenario := scenario14
    expectedStatus := .fakeJoinScheduling
    shows := "Post-hoc scheduling can manufacture an apparent joint signal."
    candidateIds := ["VII-C009", "VII-C025"] }

theorem countermodel04_passes : countermodelPass countermodel04 = true := by
  decide

def countermodel05 : CountermodelFixture :=
  { fixtureId := "CM-05"
    name := "Join that loses one child"
    scenario := scenario09
    expectedStatus := .retentionObstruction
    shows := "Composite formation does not imply parent retention."
    candidateIds := ["VII-C009", "VII-C030"] }

theorem countermodel05_passes : countermodelPass countermodel05 = true := by
  decide

def countermodel06 : CountermodelFixture :=
  { fixtureId := "CM-06"
    name := "Enablement without descent"
    scenario := scenario03
    expectedStatus := .prospectiveAdmission
    shows := "An enabling condition can be load-bearing without factorization of the enabled object."
    candidateIds := ["VII-C012", "VII-C015", "VII-C034"] }

theorem countermodel06_passes : countermodelPass countermodel06 = true := by
  decide

def countermodel07 : CountermodelFixture :=
  { fixtureId := "CM-07"
    name := "Enablement necessary but insufficient"
    scenario := scenario03
    expectedStatus := .prospectiveAdmission
    shows := "An enabler may be necessary while alternatives still determine the result."
    candidateIds := ["VII-C012", "VII-C027", "VII-C034"] }

theorem countermodel07_passes : countermodelPass countermodel07 = true := by
  decide

def countermodel08 : CountermodelFixture :=
  { fixtureId := "CM-08"
    name := "Sound but unreachable admission rule"
    scenario := scenario19
    expectedStatus := .soundUnreachable
    shows := "Soundness does not imply operational reachability."
    candidateIds := ["VII-C001", "VII-C002", "VII-C021"] }

theorem countermodel08_passes : countermodelPass countermodel08 = true := by
  decide

def countermodel09 : CountermodelFixture :=
  { fixtureId := "CM-09"
    name := "Reachable admission that never occurs"
    scenario := scenario20
    expectedStatus := .reachableNonoccurrent
    shows := "Reachability does not imply occurrence."
    candidateIds := ["VII-C001", "VII-C002", "VII-C006", "VII-C021"] }

theorem countermodel09_passes : countermodelPass countermodel09 = true := by
  decide

def countermodel10 : CountermodelFixture :=
  { fixtureId := "CM-10"
    name := "Holonomy with zero arrow"
    scenario := scenario17
    expectedStatus := .holonomyZeroArrow
    shows := "Route residue does not imply directionality."
    candidateIds := ["VII-C017", "VII-C032"] }

theorem countermodel10_passes : countermodelPass countermodel10 = true := by
  decide

def countermodel11 : CountermodelFixture :=
  { fixtureId := "CM-11"
    name := "Observer occupancy omitted from budget"
    scenario := scenario22
    expectedStatus := .unpricedObserver
    shows := "Hidden observer resources defeat endogenous/native credit."
    candidateIds := ["VII-C011", "VII-C013", "VII-C029"] }

theorem countermodel11_passes : countermodelPass countermodel11 = true := by
  decide

def countermodel12 : CountermodelFixture :=
  { fixtureId := "CM-12"
    name := "Total-lens result fails on partial self-owned access"
    scenario := scenario23
    expectedStatus := .unlicensedTotalityTransfer
    shows := "Totality assumptions do not transfer silently."
    candidateIds := ["VII-C005", "VII-C020", "VII-C022", "VII-C024"] }

theorem countermodel12_passes : countermodelPass countermodel12 = true := by
  decide

def countermodel13 : CountermodelFixture :=
  { fixtureId := "CM-13"
    name := "Product/common refinement without strictness"
    scenario := scenario07
    expectedStatus := .commonRefinementNonstrict
    shows := "Common refinement is not anti-product novelty."
    candidateIds := ["VII-C008", "VII-C009", "VII-C026"] }

theorem countermodel13_passes : countermodelPass countermodel13 = true := by
  decide

def countermodel14 : CountermodelFixture :=
  { fixtureId := "CM-14"
    name := "Relabeling-only fake join"
    scenario := scenario15
    expectedStatus := .fakeJoinRelabeling
    shows := "Presentation change cannot manufacture strict content."
    candidateIds := ["VII-C007", "VII-C009"] }

theorem countermodel14_passes : countermodelPass countermodel14 = true := by
  decide

def countermodel15 : CountermodelFixture :=
  { fixtureId := "CM-15"
    name := "Strict extension without certified objecthood"
    scenario := scenario15
    expectedStatus := .fakeJoinRelabeling
    shows := "Nonfactorization does not imply closure/objecthood."
    candidateIds := ["VII-C009"] }

theorem countermodel15_passes : countermodelPass countermodel15 = true := by
  decide

def countermodel16 : CountermodelFixture :=
  { fixtureId := "CM-16"
    name := "Strict join without directionality"
    scenario := scenario08
    expectedStatus := .strictJoin
    shows := "Strict novelty does not imply a P6 arrow."
    candidateIds := ["VII-C009", "VII-C032"] }

theorem countermodel16_passes : countermodelPass countermodel16 = true := by
  decide

def countermodel17 : CountermodelFixture :=
  { fixtureId := "CM-17"
    name := "Theorist-triggered enablement is not endogenous"
    scenario := scenario02
    expectedStatus := .lawfulFirstExtension
    shows := "Execution by the analyst fails the carried-generator condition."
    candidateIds := ["VII-C012", "VII-C013", "VII-C014"] }

theorem countermodel17_passes : countermodelPass countermodel17 = true := by
  decide

def countermodel18 : CountermodelFixture :=
  { fixtureId := "CM-18"
    name := "Finite negative search with open family"
    scenario := scenario19
    expectedStatus := .soundUnreachable
    shows := "A bounded null does not prove a universal no-go."
    candidateIds := ["VII-C002", "VII-C021", "VII-C023", "VII-C024", "VII-C033"] }

theorem countermodel18_passes : countermodelPass countermodel18 = true := by
  decide

def countermodel19 : CountermodelFixture :=
  { fixtureId := "CM-19"
    name := "Shared carrier without lawful peer transport"
    scenario := scenario01
    expectedStatus := .bootstrapBlocked
    shows := "Co-location does not provide an executable bridge or first capability."
    candidateIds := ["VII-C003", "VII-C016", "VII-C035"] }

theorem countermodel19_passes : countermodelPass countermodel19 = true := by
  decide

def countermodel20 : CountermodelFixture :=
  { fixtureId := "CM-20"
    name := "Post-hoc prediction self-certification"
    scenario := scenario04
    expectedStatus := .retrospectiveSelfCertificationRejected
    shows := "Retrospective admission cannot earn prospective credit."
    candidateIds := ["VII-C003", "VII-C004", "VII-C006"] }

theorem countermodel20_passes : countermodelPass countermodel20 = true := by
  decide

def countermodel21 : CountermodelFixture :=
  { fixtureId := "CM-21"
    name := "Zero-cost join hides positive observer cost"
    scenario := scenario22
    expectedStatus := .unpricedObserver
    shows := "Unpriced occupancy invalidates no-cost credit."
    candidateIds := ["VII-C011", "VII-C029", "VII-C031", "VII-C035"] }

theorem countermodel21_passes : countermodelPass countermodel21 = true := by
  decide

def countermodel22 : CountermodelFixture :=
  { fixtureId := "CM-22"
    name := "Parent refinement destroys an admissible join"
    scenario := scenario24
    expectedStatus := .refinementDestroysJoin
    shows := "Join admissibility need not be monotone under parent refinement."
    candidateIds := ["VII-C015", "VII-C019", "VII-C030"] }

theorem countermodel22_passes : countermodelPass countermodel22 = true := by
  decide

def countermodel23 : CountermodelFixture :=
  { fixtureId := "CM-23"
    name := "Seed-dependent closure fixed points"
    scenario := scenario24
    expectedStatus := .refinementDestroysJoin
    shows := "Initial partition/seed can change the terminal package."
    candidateIds := ["VII-C015", "VII-C018"] }

theorem countermodel23_passes : countermodelPass countermodel23 = true := by
  decide

def countermodel24 : CountermodelFixture :=
  { fixtureId := "CM-24"
    name := "Identical members assembled in different orders"
    scenario := scenario16
    expectedStatus := .orderResidue
    shows := "Bracketing/order may change the audited result."
    candidateIds := ["VII-C017", "VII-C018", "VII-C027", "VII-C028", "VII-C032"] }

theorem countermodel24_passes : countermodelPass countermodel24 = true := by
  decide

def countermodel25 : CountermodelFixture :=
  { fixtureId := "CM-25"
    name := "Join manufactures a cross-term needle"
    scenario := scenario24
    expectedStatus := .refinementDestroysJoin
    shows := "Joining need not monotonically dissolve obstructions."
    candidateIds := ["VII-C019", "VII-C031", "VII-C036"] }

theorem countermodel25_passes : countermodelPass countermodel25 = true := by
  decide

def countermodel26 : CountermodelFixture :=
  { fixtureId := "CM-26"
    name := "One-lineage pseudo-join"
    scenario := scenario05
    expectedStatus := .independenceGateFailed
    shows := "Behavioral difference inside one lineage does not establish source independence."
    candidateIds := ["VII-C005", "VII-C010"] }

theorem countermodel26_passes : countermodelPass countermodel26 = true := by
  decide

def countermodel27 : CountermodelFixture :=
  { fixtureId := "CM-27"
    name := "Lawful parents with no common admissible package"
    scenario := scenario13
    expectedStatus := .certifiedNoninteraction
    shows := "Parent lawfulness does not guarantee join existence."
    candidateIds := ["VII-C008", "VII-C026", "VII-C033"] }

theorem countermodel27_passes : countermodelPass countermodel27 = true := by
  decide

def allCountermodels : List CountermodelFixture :=
  [countermodel01
  , countermodel02
  , countermodel03
  , countermodel04
  , countermodel05
  , countermodel06
  , countermodel07
  , countermodel08
  , countermodel09
  , countermodel10
  , countermodel11
  , countermodel12
  , countermodel13
  , countermodel14
  , countermodel15
  , countermodel16
  , countermodel17
  , countermodel18
  , countermodel19
  , countermodel20
  , countermodel21
  , countermodel22
  , countermodel23
  , countermodel24
  , countermodel25
  , countermodel26
  , countermodel27]

theorem all_countermodels_pass : allCountermodels.all countermodelPass = true := by
  decide

end FoundationsVII.Models.Finite
