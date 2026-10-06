import SixBirdsIII.CoreInteraction
import SixBirdsIII.Defects
import SixBirdsIII.CompletionExamples
import SixBirdsIII.Definability
import SixBirdsIII.FiniteProbability
import SixBirdsIII.GraphCohomology
import SixBirdsIII.Promotion
import SixBirdsIII.InstrumentClaims
import SixBirdsIII.RotatingAudit
import SixBirdsIII.AbstractInterpretation
import SixBirdsIII.HighStructure
import SixBirdsIII.ModelRealizations
import SixBirdsIII.MechanizationFeasibility

namespace SixBirdsIII

theorem action_ne_blocked : CellStatus.action ≠ CellStatus.blocked := by
  intro h
  cases h

theorem accepted_ne_failed_audit : ClaimStatus.accepted ≠ ClaimStatus.failedAudit := by
  intro h
  cases h

theorem malformed_directed_cell_rejected :
    ¬ WellFormedDirectedCell malformedDirectedCell := by
  intro h
  cases h.left

theorem audited_directed_cell_well_formed :
    WellFormedDirectedCell auditedDirectedCell := by
  exact ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩

theorem primitive_label_count_six : primitiveLabels.length = 6 := primitiveLabels_length

theorem malformed_missing_witness_rejected :
    ¬ WellFormedDirectedCell missingWitnessCell := by
  intro h
  cases h.right.right.left

theorem classifier_outside_scope_priority :
    CellClassify outsideAndActionCell = CellStatus.outsideScope := by
  simp [outsideAndActionCell, CellClassify]

theorem classifier_blocked_before_action :
    CellClassify blockedCell = CellStatus.blocked := by
  simp [blockedCell, CellClassify, auditedDirectedCell]

theorem classifier_default_action :
    CellClassify actionReadyCell = CellStatus.action := by
  simp [actionReadyCell, CellClassify, auditedDirectedCell]

theorem active_role_counterexample_not_action :
    ∃ roleCell : RoleChannelRecord, ∃ cell : DirectedCellRecord,
      roleCell.status = RoleStatus.activeProjection ∧
      CellClassify cell ≠ CellStatus.action :=
  active_role_channel_not_cell_action

theorem cell_action_pair_blocked_counterexample :
    ∃ cell : DirectedCellRecord, ∃ pair : PairObservableRecord,
      CellClassify cell = CellStatus.action ∧
      pair.status = PairStatus.blocked :=
  cell_action_not_pair_real

inductive TinyState where
  | left
  | right
  | extra
deriving DecidableEq

inductive TinyMacro where
  | one
  | two
deriving DecidableEq

def tinyQuotient : TinyState -> TinyMacro
  | TinyState.left => TinyMacro.one
  | TinyState.right => TinyMacro.one
  | TinyState.extra => TinyMacro.two

def tinyUpdate : TinyState -> TinyState
  | TinyState.left => TinyState.left
  | TinyState.right => TinyState.left
  | TinyState.extra => TinyState.extra

def tinyDefectiveUpdate : TinyState -> TinyState
  | TinyState.left => TinyState.left
  | TinyState.right => TinyState.extra
  | TinyState.extra => TinyState.extra

def tinySeparatedMap : TinyState -> TinyMacro
  | TinyState.left => TinyMacro.one
  | TinyState.right => TinyMacro.two
  | TinyState.extra => TinyMacro.two

theorem zero_descent_defect_allows_descent :
    DescendsToImage tinyQuotient tinyUpdate := by
  exact (descent_defect_empty_iff_descends tinyQuotient tinyUpdate).mp (by
    intro h
    rcases h with ⟨x, x', _hx, hneq⟩
    cases x <;> cases x' <;> first | exact hneq rfl | contradiction)

theorem descent_defect_blocks_descent :
    HasDescentDefect tinyQuotient tinyDefectiveUpdate := by
  exact ⟨TinyState.left, TinyState.right, rfl, by decide⟩

theorem completion_example_idempotent_left :
    IdempotentEndomap addBIfA :=
  addBIfA_idempotent

theorem completion_example_idempotent_right :
    IdempotentEndomap addCIfB :=
  addCIfB_idempotent

theorem completion_example_defect_observable :
    CompletionPastingDefect addBIfA addCIfB :=
  completion_example_has_pasting_defect

theorem factorization_mismatch_witness :
    HasFactorizationDefect tinyQuotient tinySeparatedMap := by
  exact ⟨TinyState.left, TinyState.right, rfl, by decide⟩

theorem factorization_mismatch_blocks_factorization :
    ¬ FactorsThroughImage tinyQuotient tinySeparatedMap := by
  exact (factorization_defect_equivalence tinyQuotient tinySeparatedMap).mp
    factorization_mismatch_witness

theorem tiny_fixed_interface_encoding_injective :
    Function.Injective (fixedInterfaceEncode tinyQuotient) :=
  fixedInterfaceEncode_injective tinyQuotient

inductive ToyMacroKernel where
  | conditional
  | alternative

def toyKernelAdmissible : ToyMacroKernel -> Prop
  | ToyMacroKernel.conditional => True
  | ToyMacroKernel.alternative => True

def toyKernelLoss : ToyMacroKernel -> Nat
  | ToyMacroKernel.conditional => 3
  | ToyMacroKernel.alternative => 5

def toyKernelExcess : ToyMacroKernel -> Nat
  | ToyMacroKernel.conditional => 0
  | ToyMacroKernel.alternative => 2

def toyClosureProfile : FiniteMarkovClosureProfile ToyMacroKernel Nat where
  admissible := toyKernelAdmissible
  conditionalMacroKernel := ToyMacroKernel.conditional
  predictiveClosureLoss := toyKernelLoss
  conditionalMutualInformation := 3
  excessLoss := toyKernelExcess
  zero := 0
  add := Nat.add
  leq := Nat.le
  conditional_admissible := trivial
  loss_decomposition := by
    intro K _hK
    cases K <;> rfl
  excess_nonnegative := by
    intro K _hK
    cases K <;> exact Nat.zero_le _
  conditional_excess_zero := rfl
  add_zero_cmi := rfl
  cmi_le_add_nonnegative := by
    intro e _he
    exact Nat.le_add_right 3 e

theorem toy_probability_loss_equals_cmi :
    toyClosureProfile.predictiveClosureLoss toyClosureProfile.conditionalMacroKernel =
      toyClosureProfile.conditionalMutualInformation :=
  (finite_markov_closure_deficit toyClosureProfile).right

theorem toy_probability_conditional_kernel_minimizes :
    IsLossMinimum toyClosureProfile.leq
      toyClosureProfile.admissible
      toyClosureProfile.predictiveClosureLoss
      toyClosureProfile.conditionalMacroKernel :=
  (finite_markov_closure_deficit toyClosureProfile).left

inductive LoopCycle where
  | loop

def forestToyGraph : GraphCohomologySupport where
  Cycle := Empty
  Cochain0 := Unit
  Cochain1 := Unit
  Scalar := Bool
  zero := false
  exact := fun a => a = ()
  classZero := fun a => a = ()
  integral := fun _ gamma => nomatch gamma
  betaOneZero := True
  noCycles := True
  finiteGraphHost := true
  graphInstrument := true

def forestToyPairing : PairingNondegenerate forestToyGraph := by
  intro a
  constructor
  · intro h
    exfalso
    cases a
    exact h rfl
  · intro h
    rcases h with ⟨gamma, _hgamma⟩
    cases gamma

def forestToySupport : ForestNoCohomologySupport forestToyGraph := by
  constructor
  · exact ⟨rfl, rfl, trivial, trivial⟩
  · intro a
    cases a
    rfl

theorem forest_toy_no_cycle_drive :
    NoCycleSupportedDrive forestToyGraph :=
  forest_no_drive forestToyGraph forestToySupport forestToyPairing

def loopToyGraph : GraphCohomologySupport where
  Cycle := LoopCycle
  Cochain0 := Unit
  Cochain1 := Bool
  Scalar := Bool
  zero := false
  exact := fun a => a = false
  classZero := fun a => a = false
  integral := fun a _gamma => a
  betaOneZero := False
  noCycles := False
  finiteGraphHost := true
  graphInstrument := true

def loopToyPairing : PairingNondegenerate loopToyGraph := by
  intro a
  cases a
  · constructor
    · intro h
      exfalso
      exact h rfl
    · intro h
      rcases h with ⟨gamma, hgamma⟩
      cases gamma
      exact False.elim (hgamma rfl)
  · constructor
    · intro _h
      exact ⟨LoopCycle.loop, by
        intro h
        cases h⟩
    · intro _h hzero
      cases hzero

theorem loop_toy_has_cycle_drive :
    HasCycleSupportedDrive loopToyGraph true := by
  exact ⟨LoopCycle.loop, by
    intro h
    cases h⟩

theorem loop_toy_has_cohomological_drive :
    CohomologicalDriveClass loopToyGraph true :=
  (nonzero_affinity_equivalence loopToyGraph loopToyPairing true).mpr
    loop_toy_has_cycle_drive

theorem exact_toy_null_drive :
    forall gamma : loopToyGraph.Cycle,
      loopToyGraph.integral false gamma = loopToyGraph.zero := by
  exact exact_form_null_drive loopToyGraph
    (by
      intro a ha gamma
      cases gamma
      exact ha)
    false
    rfl

def toyForestGate : GraphGate where
  source := loopToyGraph
  target := forestToyGraph
  admissible := true
  forestProducing := True
  cycleRankLossRecorded := true

theorem toy_forest_gate_suppresses_drive :
    NoCycleSupportedDrive toyForestGate.target :=
  gating_affinity_suppression toyForestGate rfl rfl
    forestToySupport
    forestToyPairing

theorem toy22_promotion_is_strict :
    Promote toy22Bridge = PromotionStatus.strict :=
  toy22_bridge_strict

theorem toy22_promotion_has_factorization_defect :
    HasFactorizationDefect toy22Pi0 toy22Pi1 :=
  toy22_factorization_defect

def failedAuditPromotionGates : PromotionGateResults :=
  { toy22Gates with audit := GateStatus.fail }

def failedAuditPromotionBridge :
    PromotionBridgeData Toy22Carrier Toy22O0 Toy22O1 :=
  { toy22Bridge with gates := failedAuditPromotionGates }

theorem failed_audit_promotion_not_accepted :
    Promote failedAuditPromotionBridge ≠ PromotionStatus.accepted := by
  simp [Promote, PromotionAcceptedCoreBool, RequiredCoreGatesPassBool,
    failedAuditPromotionBridge, failedAuditPromotionGates,
    toy22Bridge, toy22Gates]

theorem suppressed_unbridged_claim_blocked :
    ClaimClassify suppressedUnbridgedClaim = ClaimStatus.blocked := by
  simp [ClaimClassify, suppressedUnbridgedClaim]

theorem accepted_visible_claim_has_no_overread :
    acceptedVisibleClaim.hasSuppressedUnbridgedUse = false :=
  no_overreading_suppression acceptedVisibleClaim (by
    simp [ClaimClassify, acceptedVisibleClaim, suppressedUnbridgedClaim])

theorem outside_claim_priority_over_blocked :
    ClaimClassify outsideAndSuppressedClaim = ClaimStatus.outsideScope := by
  simp [ClaimClassify, outsideAndSuppressedClaim, suppressedUnbridgedClaim]

theorem circular_self_audit_is_undefined :
    SameLevelSelfAuditClassify circularSelfAuditClaim =
      ClaimStatus.undefinedCircular := by
  simp [SameLevelSelfAuditClassify, circularSelfAuditClaim]

theorem outside_scope_self_audit_is_outside :
    SameLevelSelfAuditClassify outsideScopeSelfAuditClaim =
      ClaimStatus.outsideScope := by
  simp [SameLevelSelfAuditClassify, outsideScopeSelfAuditClaim]

theorem same_level_self_audit_not_accepted :
    SameLevelSelfAuditClassify circularSelfAuditClaim ≠ ClaimStatus.accepted :=
  same_level_self_audit_failure circularSelfAuditClaim rfl

theorem toy_rotating_audit_extension_nonfinal :
    exists ext : RotatingAuditExtension,
      ext.reportAccepted = true /\
      ext.selfSoundnessAccepted = false := by
  rcases finite_rotating_audit toyCleanInstrumentStack rfl rfl rfl with
    ⟨ext, _hlower, _hpresent, _hhigher, _hbridge, hreport, _hcompliance, hself⟩
  exact ⟨ext, hreport, hself⟩

def toyAIHost : AIHost where
  C := Unit
  A := Unit
  leC := fun _ _ => True
  leA := fun _ _ => True
  alpha := fun _ => ()
  gamma := fun _ => ()
  rho := fun _ => ()
  F := fun _ => ()
  Fsharp := fun _ => ()
  finiteC := true
  finiteA := true
  auditPresent := true
  rho_eq := by intro c; cases c; rfl
  leC_trans := by intro _ _ _ _ _; trivial
  leC_antisymm := by intro x y _ _; cases x; cases y; rfl
  leA_trans := by intro _ _ _ _ _; trivial
  alpha_mono := by intro _ _ _; trivial
  gamma_mono := by intro _ _ _; trivial
  unit := by intro _; trivial
  counit := by intro _; trivial
  F_mono := by intro _ _ _; trivial
  Fsharp_mono := by intro _ _ _; trivial
  adjunction := by intro _ _; exact Iff.intro (fun _ => trivial) (fun _ => trivial)
  gamma_fixed := by intro a; cases a; rfl

theorem toy_ai_closure_operator :
    ClosureOperatorOn toyAIHost toyAIHost.rho :=
  ai_closure_as_packaging toyAIHost rfl rfl rfl

theorem toy_ai_soundness_equivalence :
    AbstractSoundness toyAIHost <-> ConcreteSoundness toyAIHost :=
  ai_descent_as_sound_transformer toyAIHost

theorem toy_ai_representability_fixedness :
    forall p : toyAIHost.C, Representable toyAIHost p <-> FixedByRho toyAIHost p :=
  ai_representability_as_fixedness toyAIHost

inductive ToyAIHostId where
  | only

def toyAIModelFamily : AIModelFamily where
  HostId := ToyAIHostId
  host := fun _ => toyAIHost
  finiteFamily := true
  allHostsAdmissible := true
  packagingRole := by intro _; exact toy_ai_closure_operator
  descentRole := by intro _; exact toy_ai_soundness_equivalence
  representabilityRole := by intro _; exact toy_ai_representability_fixedness
  auditPresent := true
  nonclaimsRecorded := true

theorem toy_ai_model_family_realizes_fragment :
    RealizesAIFragment toyAIModelFamily :=
  ai_model_family toyAIModelFamily rfl rfl rfl rfl

theorem tiny_descent_square_recovers_descent :
    (exists Fs : ImageOf tinyQuotient -> ImageOf tinyQuotient,
      DescentSquareExact tinyQuotient tinyUpdate Fs) <->
        DescendsToImage tinyQuotient tinyUpdate :=
  descent_square_recovery tinyQuotient tinyUpdate

theorem toy_completion_square_obstructed :
    CompletionSquareObstructed addBIfA addCIfB :=
  completion_example_has_pasting_defect

theorem toy22_no_exact_filler :
    NoExactFiller toy22Pi0 toy22Pi1 := by
  exact (strict_extension_as_no_filler toy22Pi0 toy22Pi1).mpr
    toy22_factorization_defect

theorem toy_pica_realizes_fragment :
    PICARealizesCellPairProvenance toyPICARealization := by
  exact ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩

theorem bad_pica_raw_override_rejected :
    ¬ PICARealizesCellPairProvenance toyBadPICARealization := by
  intro h
  exact Bool.noConfusion h.right.right.right.right.right.left

theorem toy_pica_model_realization_exists :
    exists R : FragmentRealization,
      R.verdict = ModelVerdict.modelRealization :=
  let h := pica_model_realization toyPICARealization toy_pica_realizes_fragment
  Exists.elim h (fun R hR => ⟨R, hR.left⟩)

theorem toy_cantor_bridge_is_strict :
    Promote toyCantorStrictBridgeRealization.bridge = PromotionStatus.strict :=
  toy22_bridge_strict

theorem toy_cantor_model_realization_exists :
    exists R : FragmentRealization,
      R.verdict = ModelVerdict.modelRealization := by
  rcases cantor_strict_bridge_realization
      toyCantorStrictBridgeRealization rfl rfl rfl rfl rfl
      toy_cantor_bridge_is_strict with
    ⟨R, hR, _hfinite, _haudit, _hnonclaims⟩
  exact ⟨R, hR⟩

theorem final_mechanization_record_feasible :
    MechanizationTargetFeasible finalMechanizationTargetRecord :=
  mechanization_target_feasibility

end SixBirdsIII
