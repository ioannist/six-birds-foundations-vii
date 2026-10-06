import SixBirdsFoundationsV.Definitional.ClosedLoopScope
import SixBirdsFoundationsV.Definitional.RepairJoin

namespace SixBirdsFoundationsV

/-!
E1 internalization setup.

This module is the setup layer only.  It reuses D4/D5 repair and closed-loop
scope definitions directly, introduces the F2 split-pair obstruction reading,
and defines the carried status-partition vocabulary for E1's later theorems.

As in E7, all host-governance facts not mechanized in Foundations V are
verification-shaped certified inputs.  They are represented as named structures
with concrete `holds` predicates, not as self-referential placeholder fields.
-/

def Delta {X : Type u} {Q : Type v} {FOut : Type w} {Readout : Type x}
    (q : X -> Q) (F_C : X -> FOut) (r : FOut -> Readout)
    (x x' : X) : Prop :=
  q x = q x' ∧ r (F_C x) ≠ r (F_C x')

/--
Certified measured-run input: the declared challenge class recurs at positive
density.  E1 does not derive recurrence from the kernel in this setup module.
-/
structure PositiveDensityRecurrence (History : Type u)
    (ChallengeClass : Type v) where
  holds : History -> ChallengeClass -> Prop

/--
Certified measured-run input: the F2 split-pair obstruction recurs for the
challenge class.  The concrete obstruction witnesses live in the host history.
-/
structure RecurringSplitPairObstruction (History : Type u)
    (ChallengeClass : Type v) where
  holds : History -> ChallengeClass -> Prop

/--
Certified measured-run input: declared viability probes descend by the horizon.
E1 treats this as a measured property of the run, not a goal attribution.
-/
structure ViabilityProbesDescendAtH (System : Type u) (History : Type v)
    (ChallengeClass : Type w) (Horizon : Type x) where
  holds : System -> History -> ChallengeClass -> Horizon -> Prop

/--
Certified measured-run input: the obstruction score is reduced after challenge
episodes, using a host readout such as CD_tau or residual trace.
-/
structure MeasuredObstructionDischarge (System : Type u) (History : Type v)
    (ChallengeClass : Type w) (Horizon : Type x) where
  holds : System -> History -> ChallengeClass -> Horizon -> Prop

def PersistentWithDischarge
    {System : Type u} {History : Type v} {ChallengeClass : Type w}
    {Horizon : Type x}
    (recurrence : PositiveDensityRecurrence History ChallengeClass)
    (obstruction : RecurringSplitPairObstruction History ChallengeClass)
    (descends :
      ViabilityProbesDescendAtH System History ChallengeClass Horizon)
    (discharge :
      MeasuredObstructionDischarge System History ChallengeClass Horizon)
    (S : System) (H : History) (C : ChallengeClass)
    (horizon : Horizon) : Prop :=
  recurrence.holds H C ∧ obstruction.holds H C ∧
    descends.holds S H C horizon ∧ discharge.holds S H C horizon

def CorePromotionGatesPass
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (z z' : S.T.Z) (defect : DefectRecord)
    (move : RepairMove S.T MovePayload LedgerEntry MoveRecord
      S.moveRecordPolicy)
    (auditRecord : AuditRecord) : Prop :=
  S.I_S.Detects z defect ∧
    S.I_S.GateAllows z defect move ∧
    S.AdmissibleMove S.Lambda_S z defect move ∧
    S.T.suppK z z' ∧
    S.I_S.ReAudits z move z' auditRecord

/--
Certified host input connecting an opaque D4 move payload to the refinement
object that E1 later reads as `R_t`.
-/
structure MovePayloadInstallsRefinement (MovePayload : Type u)
    (RepairRefinement : Type v) where
  holds : MovePayload -> RepairRefinement -> Prop

/--
Certified host input connecting the post-repair carrier state to the challenge
episode being repaired.  D4 checks the kernel transition; this predicate gives
the E1 episode-level bookkeeping.
-/
structure PostRepairStateForEpisode
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (ChallengeClass : Type z) (SourceQuotient : Type z')
    (DeclaredFamily : Type z'') (TargetReadout : Type z''')
    (ObstructionWitness : Type z'''') where
  holds :
    S.T.Z ->
      ChallengeEpisode ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness -> Prop

def EndogenousRepairOccurrence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (C : ChallengeClass) (t : Nat)
    (rho_t : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord)
    (R_t : RepairRefinement) : Prop :=
  ∃ episode :
      ChallengeEpisode ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness,
    episode ∈ H.episodes ∧
      rho_t ∈ H.repairAuditEntries ∧
      H.entryEpisode rho_t episode ∧
      episode.challengeClass = C ∧
      episode.time = t ∧
      RepairTypedAuditEntryCarried S rho_t ∧
      rho_t.entryClass.sourceTag = FineSourceTag.committed_state ∧
      rho_t.entryClass.generatedByS = true ∧
      rho_t.entryClass.inScope = true ∧
      ∃ z : S.T.Z, ∃ z' : S.T.Z,
        ∃ defect : DefectRecord, ∃ auditRecord : AuditRecord,
          rho_t =
            RepairTypedAuditEntry.move (S.R_S defect).moveRecord
              rho_t.entryClass ∧
          ESystem.RepairStep S z z' defect auditRecord ∧
          CorePromotionGatesPass S z z' defect (S.R_S defect)
            auditRecord ∧
          installs.holds (S.R_S defect).payload R_t ∧
          postState.holds z' episode

def InstallsRepairJoin {X : Type u} {Q : Type v}
    {RepairRefinement : Type w} {QNext : Type x}
    (Q_t : X -> Q) (R_t : X -> RepairRefinement)
    (Q_tplus1 : X -> QNext) : Prop :=
  FiberEquiv Q_tplus1 (repairJoin Q_t R_t)

def StrictSubset {A : Type u} (smaller larger : A -> Prop) : Prop :=
  (∀ a, smaller a -> larger a) ∧ ∃ a, larger a ∧ ¬ smaller a

def StrictChallengeDescent {X : Type u} {Q : Type v}
    {QNext : Type w} {FOut : Type x} {Readout : Type y}
    (Q_t : X -> Q) (Q_tplus1 : X -> QNext)
    (F_C : X -> FOut) (r : FOut -> Readout)
    (challengedFibers : X -> X -> Prop) : Prop :=
  StrictSubset
    (fun pair : X × X =>
      Delta Q_tplus1 F_C r pair.1 pair.2 ∧
        challengedFibers pair.1 pair.2)
    (fun pair : X × X =>
      Delta Q_t F_C r pair.1 pair.2 ∧
        challengedFibers pair.1 pair.2)

/--
Certified host input for finite-forcing generic novelty of a challenge class
relative to the current same-family closure.
-/
structure GenericallyNovelChallenge (ChallengeClass : Type u)
    (Sigma : Type v) where
  holds : ChallengeClass -> Sigma -> Prop

/--
Certified host input classifying a repair refinement as a strict
self-extension rather than a same-family reparameterization.
-/
structure StrictSelfExtension (RepairRefinement : Type u)
    (Sigma : Type v) where
  holds : RepairRefinement -> Sigma -> Prop

def InfinitelyManyStrictSelfExtensions {Entry : Type u}
    {X : Type v} {RepairRefinement : Type w} {Sigma : Type x}
    (strict : StrictSelfExtension (X -> RepairRefinement) Sigma)
    (family : Nat -> Option (Entry × (X -> RepairRefinement)))
    (Sigma_at : Nat -> Sigma) : Prop :=
  ∀ n : Nat, ∃ t : Nat, ∃ entry : Entry,
    ∃ R_t : X -> RepairRefinement,
      n ≤ t ∧ family t = some (entry, R_t) ∧
        strict.holds R_t (Sigma_at t)

/--
Certified imported finite-forcing schema.  Foundations V does not derive the
generic strictness theorem in this module.
-/
structure FiniteForcingStrictness (ChallengeClass : Type u)
    (Sigma : Type v) (RepairRefinement : Type w) where
  holds : ChallengeClass -> Sigma -> (Nat -> RepairRefinement) -> Prop

/--
Certified imported F12 bridge: no later behavior may depend on distinctions
not supplied by declared apparatus data.
-/
structure NoFreeDistinctionCertified (System : Type u) (History : Type v)
    (ChallengeClass : Type w) where
  holds : System -> History -> ChallengeClass -> Prop

/--
Certified imported finite-forcing obligation for the concrete run.  Unlike a
bare status proposition, this certificate is an implication about the actual
repair family produced by the internalization branch: generically novel
challenge classes force infinitely many carried refinements to be strict
self-extensions relative to the time-indexed same-family closure.
-/
structure FiniteForcingStrictnessCertified (System : Type u)
    (History : Type v) (ChallengeClass : Type w) (Sigma : Type x)
    (Entry : Type y) (X : Type y') (RepairRefinement : Type y'') where
  strictExtensions :
    ∀ (_S : System) (_H : History) (C : ChallengeClass)
      (Sigma_at : Nat -> Sigma)
      (family : Nat -> Option (Entry × (X -> RepairRefinement)))
      (generic : GenericallyNovelChallenge ChallengeClass Sigma)
      (strict : StrictSelfExtension (X -> RepairRefinement) Sigma),
      (∀ t, generic.holds C (Sigma_at t)) ->
        InfinitelyManyStrictSelfExtensions strict family Sigma_at

/--
Certified imported FIII promotion-gate soundness obligation.  D4 checks gate
fields; this predicate records the paper-side soundness bridge.
-/
structure CorePromotionGateSoundnessCertified (System : Type u)
    (History : Type v) (ChallengeClass : Type w) where
  holds : System -> History -> ChallengeClass -> Prop

/--
Certified family-level budget feasibility in the D4 carried ledger.  D4 checks
per-move ledger membership; E1 needs this horizon-level family predicate.
-/
structure FamilyBudgetFeasibleInLambda (Ledger : Type u)
    (Entry : Type v) (RepairRefinement : Type w) where
  holds : Ledger -> (Nat -> Option (Entry × RepairRefinement)) -> Prop

/--
Certified schedule-trap guard: the challenge response is not an exogenous
switching variable mis-typed as a carried repair.
-/
structure NoScheduleTrap (System : Type u) (History : Type v)
    (ChallengeClass : Type w) where
  holds : System -> History -> ChallengeClass -> Prop

/--
Certified host predicate: a repair-typed audit occurrence discharges the
challenge obstruction.
-/
structure DischargesChallengeObstruction (ChallengeClass : Type u)
    (DefectRecord : Type v) (MoveRecord : Type w)
    (AuditRecord : Type x) where
  holds :
    RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
      ChallengeClass -> Prop

/--
Certified host predicate: a repair-typed occurrence is not realized by the
system kernel.  D4's positive kernel check is `S.T.suppK`; this predicate
classifies the negative obstruction case for arbitrary audit occurrences.
-/
structure OffKernelRepairOccurrence (DefectRecord : Type u)
    (MoveRecord : Type v) (AuditRecord : Type w) where
  holds : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord -> Prop

def DeltaEndoBadSourceTag : FineSourceTag -> Prop
  | FineSourceTag.fallback => True
  | FineSourceTag.unknown => True
  | FineSourceTag.contradictory => True
  | FineSourceTag.independent_pair_witness => True
  | FineSourceTag.simulation_trace => True
  | FineSourceTag.ablation_record => True
  | FineSourceTag.committed_state => False
  | FineSourceTag.audited_cell_records => False

def Delta_endo
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (discharges :
      DischargesChallengeObstruction ChallengeClass DefectRecord MoveRecord
        AuditRecord)
    (offKernel : OffKernelRepairOccurrence DefectRecord MoveRecord AuditRecord)
    (C : ChallengeClass)
    (entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord) :
    Prop :=
  discharges.holds entry C ∧
    (DeltaEndoBadSourceTag entry.entryClass.sourceTag ∨
      entry.entryClass.generatedByS = false ∨
      entry.entryClass.inScope = false ∨
      ¬ RepairTypedAuditEntryCarried S entry ∨
      offKernel.holds entry ∨
      entry ∉ H.repairAuditEntries)

def DeltaEndoEmpty
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (discharges :
      DischargesChallengeObstruction ChallengeClass DefectRecord MoveRecord
        AuditRecord)
    (offKernel : OffKernelRepairOccurrence DefectRecord MoveRecord AuditRecord)
    (C : ChallengeClass) : Prop :=
  ∀ entry, ¬ Delta_endo S H discharges offKernel C entry

/--
Certified host input selecting defects attached to binding challenge episodes.
E1 uses it to state unreachable repair-generation without deriving the
challenge-to-defect attachment relation.
-/
structure BindingDefectForChallenge (History : Type u)
    (ChallengeClass : Type v) (Horizon : Type w)
    (DefectRecord : Type x) where
  holds : History -> ChallengeClass -> Horizon -> DefectRecord -> Prop

def NoReachableRepairGenerator
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {History : Type z} {ChallengeClass : Type z'} {Horizon : Type z''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (bindingDefect :
      BindingDefectForChallenge History ChallengeClass Horizon DefectRecord)
    (H : History) (C : ChallengeClass) (horizon : Horizon) : Prop :=
  ∀ defect : DefectRecord,
    bindingDefect.holds H C horizon defect ->
      ¬ ∃ z : S.T.Z, ∃ z' : S.T.Z, ∃ auditRecord : AuditRecord,
        ESystem.RepairStep S z z' defect auditRecord

inductive InternalizationStatus where
  | slack
  | externally_subsidized
  | endogenously_repairing
  | stressed
  | collapsing
  deriving DecidableEq, Repr

structure InternalizationStatusRecord
    (ChallengeClass : Type u) (Horizon : Type v)
    (StatusedResidualRecord : Type w)
    (DefectRecord : Type x) (MoveRecord : Type y)
    (AuditRecord : Type z) where
  challengeClass : ChallengeClass
  horizon : Horizon
  status : InternalizationStatus
  statusResidualRecord : StatusedResidualRecord
  supportingEntries : List (RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord)

def InternalizationStatusRecordCarriedAt
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {Horizon : Type z'}
    {StatusedResidualRecord : Type z''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (statusPolicy :
      CarriedRecordPolicy S.T
        (InternalizationStatusRecord ChallengeClass Horizon
          StatusedResidualRecord DefectRecord MoveRecord AuditRecord))
    (record :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord)
    (n0 : Nat) (sourceTag : FineSourceTag)
    (generatedByS inScope : Bool) : Prop :=
  CarriedRecordAt statusPolicy record n0 sourceTag generatedByS inScope

/--
Certified host predicate for status-record support entries that are explicitly
cited as external/off-audit evidence.  This is not a completeness field; it is
only the explicit support classifier used in `InternalizationStatusOccurrenceFor`.
-/
structure ExternalOffAuditStatusSupport
    (ChallengeClass : Type u) (Horizon : Type v)
    (StatusedResidualRecord : Type w)
    (DefectRecord : Type x) (MoveRecord : Type y)
    (AuditRecord : Type z) where
  holds :
    InternalizationStatusRecord ChallengeClass Horizon
      StatusedResidualRecord DefectRecord MoveRecord AuditRecord ->
    RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord -> Prop

def InternalizationStatusOccurrenceFor
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type z'''''}
    {StatusedResidualRecord : Type u'}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (InternalizationStatusRecord ChallengeClass Horizon
          StatusedResidualRecord DefectRecord MoveRecord AuditRecord))
    (externalSupport :
      ExternalOffAuditStatusSupport ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord)
    (C : ChallengeClass) (horizon : Horizon)
    (record :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord) :
    Prop :=
  record.challengeClass = C ∧
    record.horizon = horizon ∧
    (∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        InternalizationStatusRecordCarriedAt statusPolicy record n0
          sourceTag generatedByS inScope) ∧
    ∀ entry, entry ∈ record.supportingEntries ->
      entry ∈ H.repairAuditEntries ∨ externalSupport.holds record entry

/--
Certified host input: every challenged episode is measured as absent or below
the binding threshold through the horizon.
-/
structure MeasuredObstructionSlackThroughout (System : Type u)
    (History : Type v) (ChallengeClass : Type w)
    (Horizon : Type x) where
  holds : System -> History -> ChallengeClass -> Horizon -> Prop

/--
Certified host input: the challenge obstruction is relevant to declared
viability/readout probes within the horizon.
-/
structure ChallengeRelevantWithinHorizon (System : Type u)
    (History : Type v) (ChallengeClass : Type w)
    (Horizon : Type x) where
  holds : System -> History -> ChallengeClass -> Horizon -> Prop

def BindingChallengeByHorizon
    {System : Type u} {History : Type v} {ChallengeClass : Type w}
    {Horizon : Type x}
    (recurrence : PositiveDensityRecurrence History ChallengeClass)
    (obstruction : RecurringSplitPairObstruction History ChallengeClass)
    (relevance :
      ChallengeRelevantWithinHorizon System History ChallengeClass Horizon)
    (slack :
      MeasuredObstructionSlackThroughout System History ChallengeClass Horizon)
    (S : System) (H : History) (C : ChallengeClass)
    (horizon : Horizon) : Prop :=
  recurrence.holds H C ∧ obstruction.holds H C ∧
    relevance.holds S H C horizon ∧ ¬ slack.holds S H C horizon

def BindingPersistentWithDischarge
    {System : Type u} {History : Type v} {ChallengeClass : Type w}
    {Horizon : Type x}
    (recurrence : PositiveDensityRecurrence History ChallengeClass)
    (obstruction : RecurringSplitPairObstruction History ChallengeClass)
    (descends :
      ViabilityProbesDescendAtH System History ChallengeClass Horizon)
    (discharge :
      MeasuredObstructionDischarge System History ChallengeClass Horizon)
    (relevance :
      ChallengeRelevantWithinHorizon System History ChallengeClass Horizon)
    (slack :
      MeasuredObstructionSlackThroughout System History ChallengeClass Horizon)
    (S : System) (H : History) (C : ChallengeClass)
    (horizon : Horizon) : Prop :=
  PersistentWithDischarge recurrence obstruction descends discharge S H C
      horizon ∧
    BindingChallengeByHorizon recurrence obstruction relevance slack S H C
      horizon

def ChallengedEpisodeTime
    {ChallengeClass : Type u} {SourceQuotient : Type v}
    {DeclaredFamily : Type w} {TargetReadout : Type x}
    {ObstructionWitness : Type y} {DefectRecord : Type y'}
    {MoveRecord : Type y''} {AuditRecord : Type y'''}
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (C : ChallengeClass) (t : Nat) : Prop :=
  ∃ episode :
      ChallengeEpisode ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness,
    episode ∈ H.episodes ∧
      episode.challengeClass = C ∧
      episode.time = t ∧
      ∃ witness : ObstructionWitness,
        episode.obstructionWitness = some witness

def EndogenousRepairFamilyWitness
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type z'''''}
    {RepairRefinement : Type u'} {X : Type v'} {Q : Type w'}
    {QNext : Type x'} {FOut : Type y'} {Readout : Type y''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (Q_at : Nat -> X -> Q) (Q_next_at : Nat -> X -> QNext)
    (F_C : X -> FOut) (r : FOut -> Readout)
    (challengedFibersAt : Nat -> X -> X -> Prop)
    (installs :
      MovePayloadInstallsRefinement MovePayload (X -> RepairRefinement))
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (budget :
      FamilyBudgetFeasibleInLambda (CarriedLedger S.T LedgerEntry)
        (RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord)
        (X -> RepairRefinement))
    (family :
      Nat ->
        Option
          (RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ×
            (X -> RepairRefinement)))
    (C : ChallengeClass) (_horizon : Horizon) : Prop :=
  (∃ t, ChallengedEpisodeTime H C t) ∧
    (∀ t,
      ChallengedEpisodeTime H C t ->
        ∃ entry R_t,
          family t = some (entry, R_t) ∧
            EndogenousRepairOccurrence S H installs postState C t entry R_t ∧
            InstallsRepairJoin (Q_at t) R_t (Q_next_at t) ∧
            StrictChallengeDescent (Q_at t) (Q_next_at t) F_C r
              (challengedFibersAt t)) ∧
    (∀ t entry R_t,
      family t = some (entry, R_t) ->
        EndogenousRepairOccurrence S H installs postState C t entry R_t ∧
          InstallsRepairJoin (Q_at t) R_t (Q_next_at t) ∧
          StrictChallengeDescent (Q_at t) (Q_next_at t) F_C r
            (challengedFibersAt t)) ∧
    budget.holds S.Lambda_S family

def EndogenousRepairFamilyValid
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type z'''''}
    {RepairRefinement : Type u'} {X : Type v'} {Q : Type w'}
    {QNext : Type x'} {FOut : Type y'} {Readout : Type y''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (Q_at : Nat -> X -> Q) (Q_next_at : Nat -> X -> QNext)
    (F_C : X -> FOut) (r : FOut -> Readout)
    (challengedFibersAt : Nat -> X -> X -> Prop)
    (installs :
      MovePayloadInstallsRefinement MovePayload (X -> RepairRefinement))
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (budget :
      FamilyBudgetFeasibleInLambda (CarriedLedger S.T LedgerEntry)
        (RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord)
        (X -> RepairRefinement))
    (C : ChallengeClass) (horizon : Horizon) : Prop :=
  ∃ family,
    EndogenousRepairFamilyWitness S H Q_at Q_next_at F_C r
      challengedFibersAt installs postState budget family C horizon

/--
Certified bridge tying the defects used by an endogenous repair family to the
binding-defect relation used by `NoReachableRepairGenerator`.  The setup keeps
`EndogenousRepairOccurrence` episode-local, so this bridge is the theorem-level
governance certificate that no reachable generator really excludes an
endogenous family for the same class and horizon.
-/
def NoReachableRepairGeneratorExcludesEndogenousFamily
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type z'''''}
    {RepairRefinement : Type u'} {X : Type v'} {Q : Type w'}
    {QNext : Type x'} {FOut : Type y'} {Readout : Type y''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (bindingDefect : BindingDefectForChallenge
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon DefectRecord)
    (Q_at : Nat -> X -> Q) (Q_next_at : Nat -> X -> QNext)
    (F_C : X -> FOut) (r : FOut -> Readout)
    (challengedFibersAt : Nat -> X -> X -> Prop)
    (installs :
      MovePayloadInstallsRefinement MovePayload (X -> RepairRefinement))
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (budget :
      FamilyBudgetFeasibleInLambda (CarriedLedger S.T LedgerEntry)
        (RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord)
        (X -> RepairRefinement))
    (C : ChallengeClass) (horizon : Horizon) : Prop :=
  NoReachableRepairGenerator S bindingDefect H C horizon ->
    ¬ EndogenousRepairFamilyValid S H Q_at Q_next_at F_C r
      challengedFibersAt installs postState budget C horizon

/--
Certified host input: the carried ledger has accrued an unbounded or
threshold-exceeding statused residual for the challenge by the horizon.
-/
structure StatusedResidualAccrues (System : Type u) (History : Type v)
    (ChallengeClass : Type w) (Horizon : Type x) where
  holds : System -> History -> ChallengeClass -> Horizon -> Prop

/--
Certified bridge used by E1's positive branch to rule out the stressed case:
for this measured run/readout, measured obstruction discharge excludes an
unbounded or threshold-exceeding carried residual by the same horizon.
-/
def MeasuredDischargeExcludesResidualAccrual
    {System : Type u} {History : Type v} {ChallengeClass : Type w}
    {Horizon : Type x}
    (discharge :
      MeasuredObstructionDischarge System History ChallengeClass Horizon)
    (residualAccrues :
      StatusedResidualAccrues System History ChallengeClass Horizon)
    (S : System) (H : History) (C : ChallengeClass)
    (horizon : Horizon) : Prop :=
  discharge.holds S H C horizon ->
    ¬ residualAccrues.holds S H C horizon

def SlackEvidence
    {System : Type u} {History : Type v} {ChallengeClass : Type w}
    {Horizon : Type x}
    (recurrence : PositiveDensityRecurrence History ChallengeClass)
    (obstruction : RecurringSplitPairObstruction History ChallengeClass)
    (relevance :
      ChallengeRelevantWithinHorizon System History ChallengeClass Horizon)
    (slack :
      MeasuredObstructionSlackThroughout System History ChallengeClass Horizon)
    (S : System) (H : History) (C : ChallengeClass)
    (horizon : Horizon) : Prop :=
  ¬ BindingChallengeByHorizon recurrence obstruction relevance slack S H C
    horizon

def ExternallySubsidizedEvidence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type z'''''}
    {RepairRefinement : Type u'} {X : Type v'} {Q : Type w'}
    {QNext : Type x'} {FOut : Type y'} {Readout : Type y''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (recurrence : PositiveDensityRecurrence
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (obstruction : RecurringSplitPairObstruction
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (relevance : ChallengeRelevantWithinHorizon
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (slack : MeasuredObstructionSlackThroughout
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (descends : ViabilityProbesDescendAtH
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (discharge : MeasuredObstructionDischarge
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (discharges :
      DischargesChallengeObstruction ChallengeClass DefectRecord MoveRecord
        AuditRecord)
    (offKernel : OffKernelRepairOccurrence DefectRecord MoveRecord AuditRecord)
    (Q_at : Nat -> X -> Q) (Q_next_at : Nat -> X -> QNext)
    (F_C : X -> FOut) (r : FOut -> Readout)
    (challengedFibersAt : Nat -> X -> X -> Prop)
    (installs :
      MovePayloadInstallsRefinement MovePayload (X -> RepairRefinement))
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (budget :
      FamilyBudgetFeasibleInLambda (CarriedLedger S.T LedgerEntry)
        (RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord)
        (X -> RepairRefinement))
    (C : ChallengeClass) (horizon : Horizon) : Prop :=
  BindingChallengeByHorizon recurrence obstruction relevance slack S H C
      horizon ∧
    descends.holds S H C horizon ∧
    discharge.holds S H C horizon ∧
    (∃ entry, Delta_endo S H discharges offKernel C entry) ∧
    ¬ EndogenousRepairFamilyValid S H Q_at Q_next_at F_C r
      challengedFibersAt installs postState budget C horizon

def EndogenouslyRepairingEvidence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type z'''''}
    {RepairRefinement : Type u'} {X : Type v'} {Q : Type w'}
    {QNext : Type x'} {FOut : Type y'} {Readout : Type y''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (recurrence : PositiveDensityRecurrence
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (obstruction : RecurringSplitPairObstruction
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (relevance : ChallengeRelevantWithinHorizon
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (slack : MeasuredObstructionSlackThroughout
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (descends : ViabilityProbesDescendAtH
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (discharge : MeasuredObstructionDischarge
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (discharges :
      DischargesChallengeObstruction ChallengeClass DefectRecord MoveRecord
        AuditRecord)
    (offKernel : OffKernelRepairOccurrence DefectRecord MoveRecord AuditRecord)
    (Q_at : Nat -> X -> Q) (Q_next_at : Nat -> X -> QNext)
    (F_C : X -> FOut) (r : FOut -> Readout)
    (challengedFibersAt : Nat -> X -> X -> Prop)
    (installs :
      MovePayloadInstallsRefinement MovePayload (X -> RepairRefinement))
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (budget :
      FamilyBudgetFeasibleInLambda (CarriedLedger S.T LedgerEntry)
        (RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord)
        (X -> RepairRefinement))
    (C : ChallengeClass) (horizon : Horizon) : Prop :=
  BindingChallengeByHorizon recurrence obstruction relevance slack S H C
      horizon ∧
    DeltaEndoEmpty S H discharges offKernel C ∧
    descends.holds S H C horizon ∧
    discharge.holds S H C horizon ∧
    EndogenousRepairFamilyValid S H Q_at Q_next_at F_C r
      challengedFibersAt installs postState budget C horizon

def StressedEvidence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type z'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (recurrence : PositiveDensityRecurrence
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (obstruction : RecurringSplitPairObstruction
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (relevance : ChallengeRelevantWithinHorizon
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (slack : MeasuredObstructionSlackThroughout
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (descends : ViabilityProbesDescendAtH
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (discharges :
      DischargesChallengeObstruction ChallengeClass DefectRecord MoveRecord
        AuditRecord)
    (offKernel : OffKernelRepairOccurrence DefectRecord MoveRecord AuditRecord)
    (bindingDefect : BindingDefectForChallenge
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon DefectRecord)
    (residualAccrues : StatusedResidualAccrues
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (C : ChallengeClass) (horizon : Horizon) : Prop :=
  BindingChallengeByHorizon recurrence obstruction relevance slack S H C
      horizon ∧
    DeltaEndoEmpty S H discharges offKernel C ∧
    NoReachableRepairGenerator S bindingDefect H C horizon ∧
    descends.holds S H C horizon ∧
    residualAccrues.holds S H C horizon

def CollapsingEvidence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type z'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (recurrence : PositiveDensityRecurrence
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (obstruction : RecurringSplitPairObstruction
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (relevance : ChallengeRelevantWithinHorizon
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (slack : MeasuredObstructionSlackThroughout
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (descends : ViabilityProbesDescendAtH
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (bindingDefect : BindingDefectForChallenge
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon DefectRecord)
    (C : ChallengeClass) (horizon : Horizon) : Prop :=
  BindingChallengeByHorizon recurrence obstruction relevance slack S H C
      horizon ∧
    NoReachableRepairGenerator S bindingDefect H C horizon ∧
    ¬ descends.holds S H C horizon

def SlackCase
    {ChallengeClass : Type u} {Horizon : Type v}
    {StatusedResidualRecord : Type w}
    {DefectRecord : Type x} {MoveRecord : Type y}
    {AuditRecord : Type z}
    (occurrence :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord -> Prop)
    (evidence : Prop)
    (record :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord) : Prop :=
  occurrence record ∧
    record.status = InternalizationStatus.slack ∧
    evidence

def ExternallySubsidizedCase
    {ChallengeClass : Type u} {Horizon : Type v}
    {StatusedResidualRecord : Type w}
    {DefectRecord : Type x} {MoveRecord : Type y}
    {AuditRecord : Type z}
    (occurrence :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord -> Prop)
    (evidence : Prop)
    (record :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord) : Prop :=
  occurrence record ∧
    record.status = InternalizationStatus.externally_subsidized ∧
    evidence

def EndogenouslyRepairingCase
    {ChallengeClass : Type u} {Horizon : Type v}
    {StatusedResidualRecord : Type w}
    {DefectRecord : Type x} {MoveRecord : Type y}
    {AuditRecord : Type z}
    (occurrence :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord -> Prop)
    (evidence : Prop)
    (record :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord) : Prop :=
  occurrence record ∧
    record.status = InternalizationStatus.endogenously_repairing ∧
    evidence

def StressedCase
    {ChallengeClass : Type u} {Horizon : Type v}
    {StatusedResidualRecord : Type w}
    {DefectRecord : Type x} {MoveRecord : Type y}
    {AuditRecord : Type z}
    (occurrence :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord -> Prop)
    (evidence : Prop)
    (record :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord) : Prop :=
  occurrence record ∧
    record.status = InternalizationStatus.stressed ∧
    evidence

def CollapsingCase
    {ChallengeClass : Type u} {Horizon : Type v}
    {StatusedResidualRecord : Type w}
    {DefectRecord : Type x} {MoveRecord : Type y}
    {AuditRecord : Type z}
    (occurrence :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord -> Prop)
    (evidence : Prop)
    (record :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord) : Prop :=
  occurrence record ∧
    record.status = InternalizationStatus.collapsing ∧
    evidence

def SlackHolds
    {ChallengeClass : Type u} {Horizon : Type v}
    {StatusedResidualRecord : Type w}
    {DefectRecord : Type x} {MoveRecord : Type y}
    {AuditRecord : Type z}
    (occurrence :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord -> Prop)
    (evidence : Prop) : Prop :=
  ∃ record, SlackCase occurrence evidence record

def ExternallySubsidizedHolds
    {ChallengeClass : Type u} {Horizon : Type v}
    {StatusedResidualRecord : Type w}
    {DefectRecord : Type x} {MoveRecord : Type y}
    {AuditRecord : Type z}
    (occurrence :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord -> Prop)
    (evidence : Prop) : Prop :=
  ∃ record, ExternallySubsidizedCase occurrence evidence record

def EndogenouslyRepairingHolds
    {ChallengeClass : Type u} {Horizon : Type v}
    {StatusedResidualRecord : Type w}
    {DefectRecord : Type x} {MoveRecord : Type y}
    {AuditRecord : Type z}
    (occurrence :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord -> Prop)
    (evidence : Prop) : Prop :=
  ∃ record, EndogenouslyRepairingCase occurrence evidence record

def StressedHolds
    {ChallengeClass : Type u} {Horizon : Type v}
    {StatusedResidualRecord : Type w}
    {DefectRecord : Type x} {MoveRecord : Type y}
    {AuditRecord : Type z}
    (occurrence :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord -> Prop)
    (evidence : Prop) : Prop :=
  ∃ record, StressedCase occurrence evidence record

def CollapsingHolds
    {ChallengeClass : Type u} {Horizon : Type v}
    {StatusedResidualRecord : Type w}
    {DefectRecord : Type x} {MoveRecord : Type y}
    {AuditRecord : Type z}
    (occurrence :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord -> Prop)
    (evidence : Prop) : Prop :=
  ∃ record, CollapsingCase occurrence evidence record

def CompleteInternalizationStatus
    {ChallengeClass : Type u} {Horizon : Type v}
    {StatusedResidualRecord : Type w}
    {DefectRecord : Type x} {MoveRecord : Type y}
    {AuditRecord : Type z}
    (occurrence :
      InternalizationStatusRecord ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord -> Prop)
    (slackEvidence externalEvidence endogenousEvidence stressedEvidence
      collapsingEvidence : Prop) : Prop :=
  (∃ record,
    occurrence record ∧
      (SlackCase occurrence slackEvidence record ∨
        ExternallySubsidizedCase occurrence externalEvidence record ∨
        EndogenouslyRepairingCase occurrence endogenousEvidence record ∨
        StressedCase occurrence stressedEvidence record ∨
        CollapsingCase occurrence collapsingEvidence record)) ∧
    ∀ record1 record2,
      occurrence record1 -> occurrence record2 ->
        record1.status = record2.status

/--
Concrete five-way E1 status partition.  Unlike the generic setup combinators,
this theorem instantiates occurrence and branch evidence with the actual E1
predicates over the carried status occurrence, recurrence/slack data,
external/endogenous repair evidence, and no-generator residual evidence.
-/
theorem E1_StatusPartition
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type z'''''}
    {StatusedResidualRecord : Type u'} {RepairRefinement : Type v'}
    {X : Type w'} {Q : Type x'} {QNext : Type y'}
    {FOut : Type y'} {Readout : Type y''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (InternalizationStatusRecord ChallengeClass Horizon
          StatusedResidualRecord DefectRecord MoveRecord AuditRecord))
    (externalSupport :
      ExternalOffAuditStatusSupport ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord)
    (recurrence : PositiveDensityRecurrence
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (obstruction : RecurringSplitPairObstruction
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (relevance : ChallengeRelevantWithinHorizon
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (slack : MeasuredObstructionSlackThroughout
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (descends : ViabilityProbesDescendAtH
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (discharge : MeasuredObstructionDischarge
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (discharges :
      DischargesChallengeObstruction ChallengeClass DefectRecord MoveRecord
        AuditRecord)
    (offKernel : OffKernelRepairOccurrence DefectRecord MoveRecord AuditRecord)
    (Q_at : Nat -> X -> Q) (Q_next_at : Nat -> X -> QNext)
    (F_C : X -> FOut) (r : FOut -> Readout)
    (challengedFibersAt : Nat -> X -> X -> Prop)
    (installs :
      MovePayloadInstallsRefinement MovePayload (X -> RepairRefinement))
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (budget :
      FamilyBudgetFeasibleInLambda (CarriedLedger S.T LedgerEntry)
        (RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord)
        (X -> RepairRefinement))
    (bindingDefect : BindingDefectForChallenge
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon DefectRecord)
    (residualAccrues : StatusedResidualAccrues
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (C : ChallengeClass) (horizon : Horizon)
    (hComplete :
      CompleteInternalizationStatus
        (InternalizationStatusOccurrenceFor H statusPolicy externalSupport C
          horizon)
        (SlackEvidence recurrence obstruction relevance slack S H C horizon)
        (ExternallySubsidizedEvidence S H recurrence obstruction relevance
          slack descends discharge discharges offKernel Q_at Q_next_at F_C r
          challengedFibersAt installs postState budget C horizon)
        (EndogenouslyRepairingEvidence S H recurrence obstruction relevance
          slack descends discharge discharges offKernel Q_at Q_next_at F_C r
          challengedFibersAt installs postState budget C horizon)
        (StressedEvidence S H recurrence obstruction relevance slack descends
          discharges offKernel bindingDefect residualAccrues C horizon)
        (CollapsingEvidence S H recurrence obstruction relevance slack
          descends bindingDefect C horizon)) :
    let occurrence :=
      InternalizationStatusOccurrenceFor H statusPolicy externalSupport C
        horizon
    let slackEvidence :=
      SlackEvidence recurrence obstruction relevance slack S H C horizon
    let externalEvidence :=
      ExternallySubsidizedEvidence S H recurrence obstruction relevance slack
        descends discharge discharges offKernel Q_at Q_next_at F_C r
        challengedFibersAt installs postState budget C horizon
    let endogenousEvidence :=
      EndogenouslyRepairingEvidence S H recurrence obstruction relevance slack
        descends discharge discharges offKernel Q_at Q_next_at F_C r
        challengedFibersAt installs postState budget C horizon
    let stressedEvidence :=
      StressedEvidence S H recurrence obstruction relevance slack descends
        discharges offKernel bindingDefect residualAccrues C horizon
    let collapsingEvidence :=
      CollapsingEvidence S H recurrence obstruction relevance slack descends
        bindingDefect C horizon
    (SlackHolds occurrence slackEvidence ∧
        ¬ ExternallySubsidizedHolds occurrence externalEvidence ∧
        ¬ EndogenouslyRepairingHolds occurrence endogenousEvidence ∧
        ¬ StressedHolds occurrence stressedEvidence ∧
        ¬ CollapsingHolds occurrence collapsingEvidence) ∨
      (ExternallySubsidizedHolds occurrence externalEvidence ∧
        ¬ SlackHolds occurrence slackEvidence ∧
        ¬ EndogenouslyRepairingHolds occurrence endogenousEvidence ∧
        ¬ StressedHolds occurrence stressedEvidence ∧
        ¬ CollapsingHolds occurrence collapsingEvidence) ∨
      (EndogenouslyRepairingHolds occurrence endogenousEvidence ∧
        ¬ SlackHolds occurrence slackEvidence ∧
        ¬ ExternallySubsidizedHolds occurrence externalEvidence ∧
        ¬ StressedHolds occurrence stressedEvidence ∧
        ¬ CollapsingHolds occurrence collapsingEvidence) ∨
      (StressedHolds occurrence stressedEvidence ∧
        ¬ SlackHolds occurrence slackEvidence ∧
        ¬ ExternallySubsidizedHolds occurrence externalEvidence ∧
        ¬ EndogenouslyRepairingHolds occurrence endogenousEvidence ∧
        ¬ CollapsingHolds occurrence collapsingEvidence) ∨
      (CollapsingHolds occurrence collapsingEvidence ∧
        ¬ SlackHolds occurrence slackEvidence ∧
        ¬ ExternallySubsidizedHolds occurrence externalEvidence ∧
        ¬ EndogenouslyRepairingHolds occurrence endogenousEvidence ∧
        ¬ StressedHolds occurrence stressedEvidence) := by
  let occurrence :=
    InternalizationStatusOccurrenceFor H statusPolicy externalSupport C
      horizon
  let slackEvidence :=
    SlackEvidence recurrence obstruction relevance slack S H C horizon
  let externalEvidence :=
    ExternallySubsidizedEvidence S H recurrence obstruction relevance slack
      descends discharge discharges offKernel Q_at Q_next_at F_C r
      challengedFibersAt installs postState budget C horizon
  let endogenousEvidence :=
    EndogenouslyRepairingEvidence S H recurrence obstruction relevance slack
      descends discharge discharges offKernel Q_at Q_next_at F_C r
      challengedFibersAt installs postState budget C horizon
  let stressedEvidence :=
    StressedEvidence S H recurrence obstruction relevance slack descends
      discharges offKernel bindingDefect residualAccrues C horizon
  let collapsingEvidence :=
    CollapsingEvidence S H recurrence obstruction relevance slack descends
      bindingDefect C horizon
  let hUnique := hComplete.2
  rcases hComplete.1 with ⟨record, _hOccurrence, hBranch⟩
  rcases hBranch with hSlackCase | hRest
  · have hSlack : SlackHolds occurrence slackEvidence := ⟨record, hSlackCase⟩
    have hStatus : record.status = InternalizationStatus.slack :=
      hSlackCase.2.1
    have hNotExternal : ¬ ExternallySubsidizedHolds occurrence externalEvidence := by
      intro hOther
      rcases hOther with ⟨other, hOtherCase⟩
      have hsame := hUnique record other hSlackCase.1 hOtherCase.1
      rw [hStatus, hOtherCase.2.1] at hsame
      cases hsame
    have hNotEndogenous : ¬ EndogenouslyRepairingHolds occurrence endogenousEvidence := by
      intro hOther
      rcases hOther with ⟨other, hOtherCase⟩
      have hsame := hUnique record other hSlackCase.1 hOtherCase.1
      rw [hStatus, hOtherCase.2.1] at hsame
      cases hsame
    have hNotStressed : ¬ StressedHolds occurrence stressedEvidence := by
      intro hOther
      rcases hOther with ⟨other, hOtherCase⟩
      have hsame := hUnique record other hSlackCase.1 hOtherCase.1
      rw [hStatus, hOtherCase.2.1] at hsame
      cases hsame
    have hNotCollapsing : ¬ CollapsingHolds occurrence collapsingEvidence := by
      intro hOther
      rcases hOther with ⟨other, hOtherCase⟩
      have hsame := hUnique record other hSlackCase.1 hOtherCase.1
      rw [hStatus, hOtherCase.2.1] at hsame
      cases hsame
    exact
      Or.inl
        ⟨hSlack, hNotExternal, hNotEndogenous, hNotStressed,
          hNotCollapsing⟩
  · rcases hRest with hExternalCase | hRest
    · have hExternal :
          ExternallySubsidizedHolds occurrence externalEvidence :=
        ⟨record, hExternalCase⟩
      have hStatus :
          record.status = InternalizationStatus.externally_subsidized :=
        hExternalCase.2.1
      have hNotSlack : ¬ SlackHolds occurrence slackEvidence := by
        intro hOther
        rcases hOther with ⟨other, hOtherCase⟩
        have hsame := hUnique record other hExternalCase.1 hOtherCase.1
        rw [hStatus, hOtherCase.2.1] at hsame
        cases hsame
      have hNotEndogenous : ¬ EndogenouslyRepairingHolds occurrence endogenousEvidence := by
        intro hOther
        rcases hOther with ⟨other, hOtherCase⟩
        have hsame := hUnique record other hExternalCase.1 hOtherCase.1
        rw [hStatus, hOtherCase.2.1] at hsame
        cases hsame
      have hNotStressed : ¬ StressedHolds occurrence stressedEvidence := by
        intro hOther
        rcases hOther with ⟨other, hOtherCase⟩
        have hsame := hUnique record other hExternalCase.1 hOtherCase.1
        rw [hStatus, hOtherCase.2.1] at hsame
        cases hsame
      have hNotCollapsing : ¬ CollapsingHolds occurrence collapsingEvidence := by
        intro hOther
        rcases hOther with ⟨other, hOtherCase⟩
        have hsame := hUnique record other hExternalCase.1 hOtherCase.1
        rw [hStatus, hOtherCase.2.1] at hsame
        cases hsame
      exact
        Or.inr
          (Or.inl
            ⟨hExternal, hNotSlack, hNotEndogenous, hNotStressed,
              hNotCollapsing⟩)
    · rcases hRest with hEndogenousCase | hRest
      · have hEndogenous :
            EndogenouslyRepairingHolds occurrence endogenousEvidence :=
          ⟨record, hEndogenousCase⟩
        have hStatus :
            record.status = InternalizationStatus.endogenously_repairing :=
          hEndogenousCase.2.1
        have hNotSlack : ¬ SlackHolds occurrence slackEvidence := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hEndogenousCase.1 hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        have hNotExternal :
            ¬ ExternallySubsidizedHolds occurrence externalEvidence := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hEndogenousCase.1 hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        have hNotStressed : ¬ StressedHolds occurrence stressedEvidence := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hEndogenousCase.1 hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        have hNotCollapsing : ¬ CollapsingHolds occurrence collapsingEvidence := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hEndogenousCase.1 hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        exact
          Or.inr
            (Or.inr
              (Or.inl
                ⟨hEndogenous, hNotSlack, hNotExternal, hNotStressed,
                  hNotCollapsing⟩))
      · rcases hRest with hStressedCase | hCollapsingCase
        · have hStressed : StressedHolds occurrence stressedEvidence :=
            ⟨record, hStressedCase⟩
          have hStatus : record.status = InternalizationStatus.stressed :=
            hStressedCase.2.1
          have hNotSlack : ¬ SlackHolds occurrence slackEvidence := by
            intro hOther
            rcases hOther with ⟨other, hOtherCase⟩
            have hsame := hUnique record other hStressedCase.1 hOtherCase.1
            rw [hStatus, hOtherCase.2.1] at hsame
            cases hsame
          have hNotExternal :
              ¬ ExternallySubsidizedHolds occurrence externalEvidence := by
            intro hOther
            rcases hOther with ⟨other, hOtherCase⟩
            have hsame := hUnique record other hStressedCase.1 hOtherCase.1
            rw [hStatus, hOtherCase.2.1] at hsame
            cases hsame
          have hNotEndogenous :
              ¬ EndogenouslyRepairingHolds occurrence endogenousEvidence := by
            intro hOther
            rcases hOther with ⟨other, hOtherCase⟩
            have hsame := hUnique record other hStressedCase.1 hOtherCase.1
            rw [hStatus, hOtherCase.2.1] at hsame
            cases hsame
          have hNotCollapsing :
              ¬ CollapsingHolds occurrence collapsingEvidence := by
            intro hOther
            rcases hOther with ⟨other, hOtherCase⟩
            have hsame := hUnique record other hStressedCase.1 hOtherCase.1
            rw [hStatus, hOtherCase.2.1] at hsame
            cases hsame
          exact
            Or.inr
              (Or.inr
                (Or.inr
                  (Or.inl
                    ⟨hStressed, hNotSlack, hNotExternal, hNotEndogenous,
                      hNotCollapsing⟩)))
        · have hCollapsing :
              CollapsingHolds occurrence collapsingEvidence :=
            ⟨record, hCollapsingCase⟩
          have hStatus : record.status = InternalizationStatus.collapsing :=
            hCollapsingCase.2.1
          have hNotSlack : ¬ SlackHolds occurrence slackEvidence := by
            intro hOther
            rcases hOther with ⟨other, hOtherCase⟩
            have hsame := hUnique record other hCollapsingCase.1 hOtherCase.1
            rw [hStatus, hOtherCase.2.1] at hsame
            cases hsame
          have hNotExternal :
              ¬ ExternallySubsidizedHolds occurrence externalEvidence := by
            intro hOther
            rcases hOther with ⟨other, hOtherCase⟩
            have hsame := hUnique record other hCollapsingCase.1 hOtherCase.1
            rw [hStatus, hOtherCase.2.1] at hsame
            cases hsame
          have hNotEndogenous :
              ¬ EndogenouslyRepairingHolds occurrence endogenousEvidence := by
            intro hOther
            rcases hOther with ⟨other, hOtherCase⟩
            have hsame := hUnique record other hCollapsingCase.1 hOtherCase.1
            rw [hStatus, hOtherCase.2.1] at hsame
            cases hsame
          have hNotStressed : ¬ StressedHolds occurrence stressedEvidence := by
            intro hOther
            rcases hOther with ⟨other, hOtherCase⟩
            have hsame := hUnique record other hCollapsingCase.1 hOtherCase.1
            rw [hStatus, hOtherCase.2.1] at hsame
            cases hsame
          exact
            Or.inr
              (Or.inr
                (Or.inr
                  (Or.inr
                    ⟨hCollapsing, hNotSlack, hNotExternal,
                      hNotEndogenous, hNotStressed⟩)))

/--
E1 positive internalization branch.  The proof uses the already-mechanized
five-way status partition and eliminates the four non-positive statuses with
the explicit setup bridges: binding excludes slack, `DeltaEndoEmpty` excludes
external subsidy, measured discharge excludes residual accrual, and viability
descent excludes collapse.
-/
theorem E1_Internalization
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type z'''''}
    {StatusedResidualRecord : Type u'} {RepairRefinement : Type v'}
    {X : Type w'} {Q : Type x'} {QNext : Type y'}
    {FOut : Type y'} {Readout : Type y''} {Sigma : Type z}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (InternalizationStatusRecord ChallengeClass Horizon
          StatusedResidualRecord DefectRecord MoveRecord AuditRecord))
    (externalSupport :
      ExternalOffAuditStatusSupport ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord)
    (recurrence : PositiveDensityRecurrence
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (obstruction : RecurringSplitPairObstruction
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (relevance : ChallengeRelevantWithinHorizon
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (slack : MeasuredObstructionSlackThroughout
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (descends : ViabilityProbesDescendAtH
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (discharge : MeasuredObstructionDischarge
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (discharges :
      DischargesChallengeObstruction ChallengeClass DefectRecord MoveRecord
        AuditRecord)
    (offKernel : OffKernelRepairOccurrence DefectRecord MoveRecord AuditRecord)
    (Q_at : Nat -> X -> Q) (Q_next_at : Nat -> X -> QNext)
    (F_C : X -> FOut) (r : FOut -> Readout)
    (challengedFibersAt : Nat -> X -> X -> Prop)
    (installs :
      MovePayloadInstallsRefinement MovePayload (X -> RepairRefinement))
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (budget :
      FamilyBudgetFeasibleInLambda (CarriedLedger S.T LedgerEntry)
        (RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord)
        (X -> RepairRefinement))
    (bindingDefect : BindingDefectForChallenge
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon DefectRecord)
    (residualAccrues : StatusedResidualAccrues
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (noFree : NoFreeDistinctionCertified
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (_finiteForcing : FiniteForcingStrictnessCertified
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Sigma
      (RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord) X
      RepairRefinement)
    (promotionSoundness : CorePromotionGateSoundnessCertified
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (noSchedule : NoScheduleTrap
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (C : ChallengeClass) (horizon : Horizon)
    (_hClosedLoop : ClosedLoopScope S H)
    (hBindingPersistent :
      BindingPersistentWithDischarge recurrence obstruction descends
        discharge relevance slack S H C horizon)
    (_hNoFree : noFree.holds S H C)
    (_hPromotionSoundness : promotionSoundness.holds S H C)
    (_hNoSchedule : noSchedule.holds S H C)
    (hDeltaEmpty : DeltaEndoEmpty S H discharges offKernel C)
    (hDischargeExcludes :
      MeasuredDischargeExcludesResidualAccrual discharge residualAccrues
        S H C horizon)
    (hComplete :
      CompleteInternalizationStatus
        (InternalizationStatusOccurrenceFor H statusPolicy externalSupport C
          horizon)
        (SlackEvidence recurrence obstruction relevance slack S H C horizon)
        (ExternallySubsidizedEvidence S H recurrence obstruction relevance
          slack descends discharge discharges offKernel Q_at Q_next_at F_C r
          challengedFibersAt installs postState budget C horizon)
        (EndogenouslyRepairingEvidence S H recurrence obstruction relevance
          slack descends discharge discharges offKernel Q_at Q_next_at F_C r
          challengedFibersAt installs postState budget C horizon)
        (StressedEvidence S H recurrence obstruction relevance slack descends
          discharges offKernel bindingDefect residualAccrues C horizon)
        (CollapsingEvidence S H recurrence obstruction relevance slack
          descends bindingDefect C horizon)) :
    let occurrence :=
      InternalizationStatusOccurrenceFor H statusPolicy externalSupport C
        horizon
    let endogenousEvidence :=
      EndogenouslyRepairingEvidence S H recurrence obstruction relevance slack
        descends discharge discharges offKernel Q_at Q_next_at F_C r
        challengedFibersAt installs postState budget C horizon
    EndogenouslyRepairingHolds occurrence endogenousEvidence ∧
      EndogenousRepairFamilyValid S H Q_at Q_next_at F_C r
        challengedFibersAt installs postState budget C horizon := by
  let occurrence :=
    InternalizationStatusOccurrenceFor H statusPolicy externalSupport C
      horizon
  let slackEvidence :=
    SlackEvidence recurrence obstruction relevance slack S H C horizon
  let externalEvidence :=
    ExternallySubsidizedEvidence S H recurrence obstruction relevance slack
      descends discharge discharges offKernel Q_at Q_next_at F_C r
      challengedFibersAt installs postState budget C horizon
  let endogenousEvidence :=
    EndogenouslyRepairingEvidence S H recurrence obstruction relevance slack
      descends discharge discharges offKernel Q_at Q_next_at F_C r
      challengedFibersAt installs postState budget C horizon
  let stressedEvidence :=
    StressedEvidence S H recurrence obstruction relevance slack descends
      discharges offKernel bindingDefect residualAccrues C horizon
  let collapsingEvidence :=
    CollapsingEvidence S H recurrence obstruction relevance slack descends
      bindingDefect C horizon
  have hPartition :=
    E1_StatusPartition H statusPolicy externalSupport recurrence obstruction
      relevance slack descends discharge discharges offKernel Q_at Q_next_at
      F_C r challengedFibersAt installs postState budget bindingDefect
      residualAccrues C horizon hComplete
  dsimp only at hPartition
  have hBinding :
      BindingChallengeByHorizon recurrence obstruction relevance slack S H C
        horizon := hBindingPersistent.2
  have hPersistent :
      PersistentWithDischarge recurrence obstruction descends discharge S H C
        horizon := hBindingPersistent.1
  have hDescends : descends.holds S H C horizon := hPersistent.2.2.1
  have hDischarge : discharge.holds S H C horizon := hPersistent.2.2.2
  have hNotSlack : ¬ SlackHolds occurrence slackEvidence := by
    intro hSlack
    rcases hSlack with ⟨record, hCase⟩
    exact hCase.2.2 hBinding
  have hNotExternal :
      ¬ ExternallySubsidizedHolds occurrence externalEvidence := by
    intro hExternal
    rcases hExternal with ⟨record, hCase⟩
    rcases hCase.2.2 with
      ⟨_hBinding, _hDescends, _hDischarge, hDelta, _hNoFamily⟩
    rcases hDelta with ⟨entry, hEntry⟩
    exact hDeltaEmpty entry hEntry
  have hNotStressed : ¬ StressedHolds occurrence stressedEvidence := by
    intro hStressed
    rcases hStressed with ⟨record, hCase⟩
    rcases hCase.2.2 with
      ⟨_hBinding, _hDeltaEmpty, _hNoReachable, _hDescends, hResidual⟩
    exact (hDischargeExcludes hDischarge) hResidual
  have hNotCollapsing : ¬ CollapsingHolds occurrence collapsingEvidence := by
    intro hCollapsing
    rcases hCollapsing with ⟨record, hCase⟩
    rcases hCase.2.2 with ⟨_hBinding, _hNoReachable, hNotDescends⟩
    exact hNotDescends hDescends
  rcases hPartition with hSlackBranch | hRest
  · exact False.elim (hNotSlack hSlackBranch.1)
  · rcases hRest with hExternalBranch | hRest
    · exact False.elim (hNotExternal hExternalBranch.1)
    · rcases hRest with hEndogenousBranch | hRest
      · have hEndogenous :
            EndogenouslyRepairingHolds occurrence endogenousEvidence :=
          hEndogenousBranch.1
        rcases hEndogenous with ⟨record, hCase⟩
        rcases hCase.2.2 with
          ⟨_hBinding, _hDeltaEmpty, _hDescends, _hDischarge, hFamily⟩
        exact ⟨⟨record, hCase⟩, hFamily⟩
      · rcases hRest with hStressedBranch | hCollapsingBranch
        · exact False.elim (hNotStressed hStressedBranch.1)
        · exact False.elim (hNotCollapsing hCollapsingBranch.1)

theorem E1_StrictSelfExtension
    {System : Type u} {History : Type v} {ChallengeClass : Type w}
    {Sigma : Type x} {Entry : Type y} {X : Type y'}
    {RepairRefinement : Type y''}
    (finiteForcing :
      FiniteForcingStrictnessCertified System History ChallengeClass Sigma
        Entry X RepairRefinement)
    (S : System) (H : History) (C : ChallengeClass)
    (Sigma_at : Nat -> Sigma)
    (family : Nat -> Option (Entry × (X -> RepairRefinement)))
    (generic : GenericallyNovelChallenge ChallengeClass Sigma)
    (strict : StrictSelfExtension (X -> RepairRefinement) Sigma)
    (hGenericAlong : ∀ t, generic.holds C (Sigma_at t)) :
    InfinitelyManyStrictSelfExtensions strict family Sigma_at :=
  finiteForcing.strictExtensions S H C Sigma_at family generic strict
    hGenericAlong

theorem E1_NoGeneratorDichotomy
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type z'''''}
    {StatusedResidualRecord : Type u'} {RepairRefinement : Type v'}
    {X : Type w'} {Q : Type x'} {QNext : Type y'}
    {FOut : Type y'} {Readout : Type y''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (InternalizationStatusRecord ChallengeClass Horizon
          StatusedResidualRecord DefectRecord MoveRecord AuditRecord))
    (externalSupport :
      ExternalOffAuditStatusSupport ChallengeClass Horizon
        StatusedResidualRecord DefectRecord MoveRecord AuditRecord)
    (recurrence : PositiveDensityRecurrence
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (obstruction : RecurringSplitPairObstruction
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass)
    (relevance : ChallengeRelevantWithinHorizon
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (slack : MeasuredObstructionSlackThroughout
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (descends : ViabilityProbesDescendAtH
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (discharge : MeasuredObstructionDischarge
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (discharges :
      DischargesChallengeObstruction ChallengeClass DefectRecord MoveRecord
        AuditRecord)
    (offKernel : OffKernelRepairOccurrence DefectRecord MoveRecord AuditRecord)
    (Q_at : Nat -> X -> Q) (Q_next_at : Nat -> X -> QNext)
    (F_C : X -> FOut) (r : FOut -> Readout)
    (challengedFibersAt : Nat -> X -> X -> Prop)
    (installs :
      MovePayloadInstallsRefinement MovePayload (X -> RepairRefinement))
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (budget :
      FamilyBudgetFeasibleInLambda (CarriedLedger S.T LedgerEntry)
        (RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord)
        (X -> RepairRefinement))
    (bindingDefect : BindingDefectForChallenge
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon DefectRecord)
    (residualAccrues : StatusedResidualAccrues
      (ESystem FData RuleFamily ResidualFamily AuditAccessData
        InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
        AuditRecord)
      (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
      ChallengeClass Horizon)
    (C : ChallengeClass) (horizon : Horizon)
    (_hClosedLoop : ClosedLoopScope S H)
    (hNoReachable : NoReachableRepairGenerator S bindingDefect H C horizon)
    (hDeltaEmpty : DeltaEndoEmpty S H discharges offKernel C)
    (hNoEndogenousFamily :
      NoReachableRepairGeneratorExcludesEndogenousFamily S H bindingDefect
        Q_at Q_next_at F_C r challengedFibersAt installs postState budget C
        horizon)
    (hComplete :
      CompleteInternalizationStatus
        (InternalizationStatusOccurrenceFor H statusPolicy externalSupport C
          horizon)
        (SlackEvidence recurrence obstruction relevance slack S H C horizon)
        (ExternallySubsidizedEvidence S H recurrence obstruction relevance
          slack descends discharge discharges offKernel Q_at Q_next_at F_C r
          challengedFibersAt installs postState budget C horizon)
        (EndogenouslyRepairingEvidence S H recurrence obstruction relevance
          slack descends discharge discharges offKernel Q_at Q_next_at F_C r
          challengedFibersAt installs postState budget C horizon)
        (StressedEvidence S H recurrence obstruction relevance slack descends
          discharges offKernel bindingDefect residualAccrues C horizon)
        (CollapsingEvidence S H recurrence obstruction relevance slack
          descends bindingDefect C horizon)) :
    let occurrence :=
      InternalizationStatusOccurrenceFor H statusPolicy externalSupport C
        horizon
    let slackEvidence :=
      SlackEvidence recurrence obstruction relevance slack S H C horizon
    let stressedEvidence :=
      StressedEvidence S H recurrence obstruction relevance slack descends
        discharges offKernel bindingDefect residualAccrues C horizon
    let collapsingEvidence :=
      CollapsingEvidence S H recurrence obstruction relevance slack descends
        bindingDefect C horizon
    (SlackHolds occurrence slackEvidence ∧
        ¬ StressedHolds occurrence stressedEvidence ∧
        ¬ CollapsingHolds occurrence collapsingEvidence) ∨
      (StressedHolds occurrence stressedEvidence ∧
        ¬ SlackHolds occurrence slackEvidence ∧
        ¬ CollapsingHolds occurrence collapsingEvidence) ∨
      (CollapsingHolds occurrence collapsingEvidence ∧
        ¬ SlackHolds occurrence slackEvidence ∧
        ¬ StressedHolds occurrence stressedEvidence) := by
  let occurrence :=
    InternalizationStatusOccurrenceFor H statusPolicy externalSupport C
      horizon
  let slackEvidence :=
    SlackEvidence recurrence obstruction relevance slack S H C horizon
  let externalEvidence :=
    ExternallySubsidizedEvidence S H recurrence obstruction relevance slack
      descends discharge discharges offKernel Q_at Q_next_at F_C r
      challengedFibersAt installs postState budget C horizon
  let endogenousEvidence :=
    EndogenouslyRepairingEvidence S H recurrence obstruction relevance slack
      descends discharge discharges offKernel Q_at Q_next_at F_C r
      challengedFibersAt installs postState budget C horizon
  let stressedEvidence :=
    StressedEvidence S H recurrence obstruction relevance slack descends
      discharges offKernel bindingDefect residualAccrues C horizon
  let collapsingEvidence :=
    CollapsingEvidence S H recurrence obstruction relevance slack descends
      bindingDefect C horizon
  have hPartition :=
    E1_StatusPartition H statusPolicy externalSupport recurrence obstruction
      relevance slack descends discharge discharges offKernel Q_at Q_next_at
      F_C r challengedFibersAt installs postState budget bindingDefect
      residualAccrues C horizon hComplete
  dsimp only at hPartition
  have hNotExternal :
      ¬ ExternallySubsidizedHolds occurrence externalEvidence := by
    intro hExternal
    rcases hExternal with ⟨record, hCase⟩
    rcases hCase.2.2 with
      ⟨_hBinding, _hDescends, _hDischarge, hDelta, _hNoFamily⟩
    rcases hDelta with ⟨entry, hEntry⟩
    exact hDeltaEmpty entry hEntry
  have hNotEndogenous :
      ¬ EndogenouslyRepairingHolds occurrence endogenousEvidence := by
    intro hEndogenous
    rcases hEndogenous with ⟨record, hCase⟩
    rcases hCase.2.2 with
      ⟨_hBinding, _hDeltaEmpty, _hDescends, _hDischarge, hFamily⟩
    exact (hNoEndogenousFamily hNoReachable) hFamily
  rcases hPartition with hSlackBranch | hRest
  · rcases hSlackBranch with
      ⟨hSlack, _hNotExternal, _hNotEndogenous, hNotStressed,
        hNotCollapsing⟩
    exact Or.inl ⟨hSlack, hNotStressed, hNotCollapsing⟩
  · rcases hRest with hExternalBranch | hRest
    · exact False.elim (hNotExternal hExternalBranch.1)
    · rcases hRest with hEndogenousBranch | hRest
      · exact False.elim (hNotEndogenous hEndogenousBranch.1)
      · rcases hRest with hStressedBranch | hCollapsingBranch
        · rcases hStressedBranch with
            ⟨hStressed, hNotSlack, _hNotExternal, _hNotEndogenous,
              hNotCollapsing⟩
          exact
            Or.inr
              (Or.inl ⟨hStressed, hNotSlack, hNotCollapsing⟩)
        · rcases hCollapsingBranch with
            ⟨hCollapsing, hNotSlack, _hNotExternal, _hNotEndogenous,
              hNotStressed⟩
          exact
            Or.inr
              (Or.inr ⟨hCollapsing, hNotSlack, hNotStressed⟩)

end SixBirdsFoundationsV
