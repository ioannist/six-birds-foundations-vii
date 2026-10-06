import SixBirdsFoundationsV.Definitional.ESystem

namespace SixBirdsFoundationsV

/-!
D5 closed-loop scope.

The closed-loop check is over source-labeled audit occurrences, not bare record
values.  Each repair-typed entry carries the audit's own declared read-off time
and source classification, and carriedness is checked with `CarriedRecordAt`.
-/

structure RepairEntryClass where
  n0 : Nat
  sourceTag : FineSourceTag
  generatedByS : Bool
  inScope : Bool
  deriving Repr

inductive RepairTypedAuditEntry
    (DefectRecord : Type u) (MoveRecord : Type v) (AuditRecord : Type w) where
  | defect (record : DefectRecord) (entryClass : RepairEntryClass)
  | move (record : MoveRecord) (entryClass : RepairEntryClass)
  | audit (record : AuditRecord) (entryClass : RepairEntryClass)
  deriving Repr

def RepairTypedAuditEntry.entryClass
    {DefectRecord : Type u} {MoveRecord : Type v} {AuditRecord : Type w} :
    RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
      RepairEntryClass
  | RepairTypedAuditEntry.defect _ entryClass => entryClass
  | RepairTypedAuditEntry.move _ entryClass => entryClass
  | RepairTypedAuditEntry.audit _ entryClass => entryClass

inductive SameRepairRecordValue
    {DefectRecord : Type u} {MoveRecord : Type v} {AuditRecord : Type w} :
    RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
      RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord -> Prop where
  | defect {record₁ record₂ : DefectRecord}
      {class₁ class₂ : RepairEntryClass} :
      record₁ = record₂ ->
      SameRepairRecordValue
        (RepairTypedAuditEntry.defect record₁ class₁)
        (RepairTypedAuditEntry.defect record₂ class₂)
  | move {record₁ record₂ : MoveRecord}
      {class₁ class₂ : RepairEntryClass} :
      record₁ = record₂ ->
      SameRepairRecordValue
        (RepairTypedAuditEntry.move record₁ class₁)
        (RepairTypedAuditEntry.move record₂ class₂)
  | audit {record₁ record₂ : AuditRecord}
      {class₁ class₂ : RepairEntryClass} :
      record₁ = record₂ ->
      SameRepairRecordValue
        (RepairTypedAuditEntry.audit record₁ class₁)
        (RepairTypedAuditEntry.audit record₂ class₂)

def RepairTypedAuditEntryCarried
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord) :
    RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord -> Prop
  | RepairTypedAuditEntry.defect record entryClass =>
      CarriedRecordAt S.defectRecordPolicy record entryClass.n0
        entryClass.sourceTag entryClass.generatedByS entryClass.inScope
  | RepairTypedAuditEntry.move record entryClass =>
      CarriedRecordAt S.moveRecordPolicy record entryClass.n0
        entryClass.sourceTag entryClass.generatedByS entryClass.inScope
  | RepairTypedAuditEntry.audit record entryClass =>
      CarriedRecordAt S.auditRecordPolicy record entryClass.n0
        entryClass.sourceTag entryClass.generatedByS entryClass.inScope

structure ChallengeEpisode
    (ChallengeClass : Type u) (SourceQuotient : Type v)
    (DeclaredFamily : Type w) (TargetReadout : Type x)
    (ObstructionWitness : Type y) where
  time : Nat
  challengeClass : ChallengeClass
  sourceQuotient : SourceQuotient
  declaredFamily : DeclaredFamily
  targetReadout : TargetReadout
  obstructionWitness : Option ObstructionWitness

structure ChallengeHistory
    (ChallengeClass : Type u) (SourceQuotient : Type v)
    (DeclaredFamily : Type w) (TargetReadout : Type x)
    (ObstructionWitness : Type y)
    (DefectRecord : Type y') (MoveRecord : Type y'')
    (AuditRecord : Type y''') where
  episodes :
    List
      (ChallengeEpisode ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness)
  repairAuditEntries :
    List (RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord)
  entryEpisode :
    RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
      ChallengeEpisode ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness -> Prop
  entryEpisodeDeclared :
    ∀ entry, entry ∈ repairAuditEntries ->
      ∃ episode, episode ∈ episodes ∧ entryEpisode entry episode
  CompleteChallengeAuditHistory : Prop

def ClosedLoopScope
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord) :
    Prop :=
  H.CompleteChallengeAuditHistory ∧
  ∀ entry, entry ∈ H.repairAuditEntries ->
    RepairTypedAuditEntryCarried S entry

theorem closedLoopScope_complete
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord}
    (h : ClosedLoopScope S H) :
    H.CompleteChallengeAuditHistory :=
  h.1

theorem closedLoopScope_entry_carried
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord}
    {entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (h : ClosedLoopScope S H)
    (hmem : entry ∈ H.repairAuditEntries) :
    RepairTypedAuditEntryCarried S entry :=
  h.2 entry hmem

theorem carriedRecordAt_carriedSource
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {Record : Type y}
    {policy : CarriedRecordPolicy T Record}
    {record : Record} {entryClass : RepairEntryClass}
    (h :
      CarriedRecordAt policy record entryClass.n0 entryClass.sourceTag
        entryClass.generatedByS entryClass.inScope) :
    CarriedSource entryClass.sourceTag entryClass.generatedByS
      entryClass.inScope :=
  h.2.2

theorem not_carriedRecordAt_of_source_fallback
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {Record : Type y}
    {policy : CarriedRecordPolicy T Record}
    {record : Record} {entryClass : RepairEntryClass}
    (hsource : entryClass.sourceTag = FineSourceTag.fallback) :
    ¬ CarriedRecordAt policy record entryClass.n0 entryClass.sourceTag
      entryClass.generatedByS entryClass.inScope := by
  intro h
  have hcarriedSource := carriedRecordAt_carriedSource h
  rw [hsource] at hcarriedSource
  exact not_carriedSource_fallback entryClass.generatedByS
    entryClass.inScope hcarriedSource

theorem not_carriedRecordAt_of_source_unknown
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {Record : Type y}
    {policy : CarriedRecordPolicy T Record}
    {record : Record} {entryClass : RepairEntryClass}
    (hsource : entryClass.sourceTag = FineSourceTag.unknown) :
    ¬ CarriedRecordAt policy record entryClass.n0 entryClass.sourceTag
      entryClass.generatedByS entryClass.inScope := by
  intro h
  have hcarriedSource := carriedRecordAt_carriedSource h
  rw [hsource] at hcarriedSource
  exact not_carriedSource_unknown entryClass.generatedByS
    entryClass.inScope hcarriedSource

theorem not_carriedRecordAt_of_source_contradictory
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {Record : Type y}
    {policy : CarriedRecordPolicy T Record}
    {record : Record} {entryClass : RepairEntryClass}
    (hsource : entryClass.sourceTag = FineSourceTag.contradictory) :
    ¬ CarriedRecordAt policy record entryClass.n0 entryClass.sourceTag
      entryClass.generatedByS entryClass.inScope := by
  intro h
  have hcarriedSource := carriedRecordAt_carriedSource h
  rw [hsource] at hcarriedSource
  exact not_carriedSource_contradictory entryClass.generatedByS
    entryClass.inScope hcarriedSource

theorem not_carriedRecordAt_of_generatedByS_false
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {Record : Type y}
    {policy : CarriedRecordPolicy T Record}
    {record : Record} {entryClass : RepairEntryClass}
    (hgenerated : entryClass.generatedByS = false) :
    ¬ CarriedRecordAt policy record entryClass.n0 entryClass.sourceTag
      entryClass.generatedByS entryClass.inScope := by
  intro h
  have hcarriedSource := carriedRecordAt_carriedSource h
  rw [hgenerated] at hcarriedSource
  cases hcarriedSource.2.1

theorem not_carriedRecordAt_of_inScope_false
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {Record : Type y}
    {policy : CarriedRecordPolicy T Record}
    {record : Record} {entryClass : RepairEntryClass}
    (hscope : entryClass.inScope = false) :
    ¬ CarriedRecordAt policy record entryClass.n0 entryClass.sourceTag
      entryClass.generatedByS entryClass.inScope := by
  intro h
  have hcarriedSource := carriedRecordAt_carriedSource h
  rw [hscope] at hcarriedSource
  cases hcarriedSource.2.2

theorem not_repairTypedAuditEntryCarried_of_source_fallback
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (hsource : entry.entryClass.sourceTag = FineSourceTag.fallback) :
    ¬ RepairTypedAuditEntryCarried S entry := by
  cases entry with
  | defect record entryClass =>
      exact not_carriedRecordAt_of_source_fallback hsource
  | move record entryClass =>
      exact not_carriedRecordAt_of_source_fallback hsource
  | audit record entryClass =>
      exact not_carriedRecordAt_of_source_fallback hsource

theorem not_repairTypedAuditEntryCarried_of_source_unknown
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (hsource : entry.entryClass.sourceTag = FineSourceTag.unknown) :
    ¬ RepairTypedAuditEntryCarried S entry := by
  cases entry with
  | defect record entryClass =>
      exact not_carriedRecordAt_of_source_unknown hsource
  | move record entryClass =>
      exact not_carriedRecordAt_of_source_unknown hsource
  | audit record entryClass =>
      exact not_carriedRecordAt_of_source_unknown hsource

theorem not_repairTypedAuditEntryCarried_of_source_contradictory
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (hsource : entry.entryClass.sourceTag = FineSourceTag.contradictory) :
    ¬ RepairTypedAuditEntryCarried S entry := by
  cases entry with
  | defect record entryClass =>
      exact not_carriedRecordAt_of_source_contradictory hsource
  | move record entryClass =>
      exact not_carriedRecordAt_of_source_contradictory hsource
  | audit record entryClass =>
      exact not_carriedRecordAt_of_source_contradictory hsource

theorem not_repairTypedAuditEntryCarried_of_source_independent_pair_witness
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (hsource :
      entry.entryClass.sourceTag = FineSourceTag.independent_pair_witness) :
    ¬ RepairTypedAuditEntryCarried S entry := by
  cases entry with
  | defect record entryClass =>
      intro h
      have hcarriedSource := carriedRecordAt_carriedSource h
      have hsource' :
          entryClass.sourceTag = FineSourceTag.independent_pair_witness := by
        simpa [RepairTypedAuditEntry.entryClass] using hsource
      rw [hsource'] at hcarriedSource
      exact not_carriedSource_independent_pair_witness
        entryClass.generatedByS entryClass.inScope hcarriedSource
  | move record entryClass =>
      intro h
      have hcarriedSource := carriedRecordAt_carriedSource h
      have hsource' :
          entryClass.sourceTag = FineSourceTag.independent_pair_witness := by
        simpa [RepairTypedAuditEntry.entryClass] using hsource
      rw [hsource'] at hcarriedSource
      exact not_carriedSource_independent_pair_witness
        entryClass.generatedByS entryClass.inScope hcarriedSource
  | audit record entryClass =>
      intro h
      have hcarriedSource := carriedRecordAt_carriedSource h
      have hsource' :
          entryClass.sourceTag = FineSourceTag.independent_pair_witness := by
        simpa [RepairTypedAuditEntry.entryClass] using hsource
      rw [hsource'] at hcarriedSource
      exact not_carriedSource_independent_pair_witness
        entryClass.generatedByS entryClass.inScope hcarriedSource

theorem not_repairTypedAuditEntryCarried_of_source_simulation_trace
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (hsource : entry.entryClass.sourceTag = FineSourceTag.simulation_trace) :
    ¬ RepairTypedAuditEntryCarried S entry := by
  cases entry with
  | defect record entryClass =>
      intro h
      have hcarriedSource := carriedRecordAt_carriedSource h
      have hsource' :
          entryClass.sourceTag = FineSourceTag.simulation_trace := by
        simpa [RepairTypedAuditEntry.entryClass] using hsource
      rw [hsource'] at hcarriedSource
      exact not_carriedSource_simulation_trace entryClass.generatedByS
        entryClass.inScope hcarriedSource
  | move record entryClass =>
      intro h
      have hcarriedSource := carriedRecordAt_carriedSource h
      have hsource' :
          entryClass.sourceTag = FineSourceTag.simulation_trace := by
        simpa [RepairTypedAuditEntry.entryClass] using hsource
      rw [hsource'] at hcarriedSource
      exact not_carriedSource_simulation_trace entryClass.generatedByS
        entryClass.inScope hcarriedSource
  | audit record entryClass =>
      intro h
      have hcarriedSource := carriedRecordAt_carriedSource h
      have hsource' :
          entryClass.sourceTag = FineSourceTag.simulation_trace := by
        simpa [RepairTypedAuditEntry.entryClass] using hsource
      rw [hsource'] at hcarriedSource
      exact not_carriedSource_simulation_trace entryClass.generatedByS
        entryClass.inScope hcarriedSource

theorem not_repairTypedAuditEntryCarried_of_source_ablation_record
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (hsource : entry.entryClass.sourceTag = FineSourceTag.ablation_record) :
    ¬ RepairTypedAuditEntryCarried S entry := by
  cases entry with
  | defect record entryClass =>
      intro h
      have hcarriedSource := carriedRecordAt_carriedSource h
      have hsource' :
          entryClass.sourceTag = FineSourceTag.ablation_record := by
        simpa [RepairTypedAuditEntry.entryClass] using hsource
      rw [hsource'] at hcarriedSource
      exact not_carriedSource_ablation_record entryClass.generatedByS
        entryClass.inScope hcarriedSource
  | move record entryClass =>
      intro h
      have hcarriedSource := carriedRecordAt_carriedSource h
      have hsource' :
          entryClass.sourceTag = FineSourceTag.ablation_record := by
        simpa [RepairTypedAuditEntry.entryClass] using hsource
      rw [hsource'] at hcarriedSource
      exact not_carriedSource_ablation_record entryClass.generatedByS
        entryClass.inScope hcarriedSource
  | audit record entryClass =>
      intro h
      have hcarriedSource := carriedRecordAt_carriedSource h
      have hsource' :
          entryClass.sourceTag = FineSourceTag.ablation_record := by
        simpa [RepairTypedAuditEntry.entryClass] using hsource
      rw [hsource'] at hcarriedSource
      exact not_carriedSource_ablation_record entryClass.generatedByS
        entryClass.inScope hcarriedSource

theorem not_repairTypedAuditEntryCarried_of_generatedByS_false
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (hgenerated : entry.entryClass.generatedByS = false) :
    ¬ RepairTypedAuditEntryCarried S entry := by
  cases entry with
  | defect record entryClass =>
      exact not_carriedRecordAt_of_generatedByS_false hgenerated
  | move record entryClass =>
      exact not_carriedRecordAt_of_generatedByS_false hgenerated
  | audit record entryClass =>
      exact not_carriedRecordAt_of_generatedByS_false hgenerated

theorem not_repairTypedAuditEntryCarried_of_inScope_false
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (hscope : entry.entryClass.inScope = false) :
    ¬ RepairTypedAuditEntryCarried S entry := by
  cases entry with
  | defect record entryClass =>
      exact not_carriedRecordAt_of_inScope_false hscope
  | move record entryClass =>
      exact not_carriedRecordAt_of_inScope_false hscope
  | audit record entryClass =>
      exact not_carriedRecordAt_of_inScope_false hscope

theorem not_closedLoopScope_of_listed_source_fallback
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord}
    {entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (hmem : entry ∈ H.repairAuditEntries)
    (hsource : entry.entryClass.sourceTag = FineSourceTag.fallback) :
    ¬ ClosedLoopScope S H := by
  intro h
  exact not_repairTypedAuditEntryCarried_of_source_fallback hsource
    (closedLoopScope_entry_carried h hmem)

theorem not_closedLoopScope_of_listed_source_unknown
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord}
    {entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (hmem : entry ∈ H.repairAuditEntries)
    (hsource : entry.entryClass.sourceTag = FineSourceTag.unknown) :
    ¬ ClosedLoopScope S H := by
  intro h
  exact not_repairTypedAuditEntryCarried_of_source_unknown hsource
    (closedLoopScope_entry_carried h hmem)

theorem not_closedLoopScope_of_listed_source_contradictory
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord}
    {entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (hmem : entry ∈ H.repairAuditEntries)
    (hsource : entry.entryClass.sourceTag = FineSourceTag.contradictory) :
    ¬ ClosedLoopScope S H := by
  intro h
  exact not_repairTypedAuditEntryCarried_of_source_contradictory hsource
    (closedLoopScope_entry_carried h hmem)

theorem not_closedLoopScope_of_listed_generatedByS_false
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord}
    {entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (hmem : entry ∈ H.repairAuditEntries)
    (hgenerated : entry.entryClass.generatedByS = false) :
    ¬ ClosedLoopScope S H := by
  intro h
  exact not_repairTypedAuditEntryCarried_of_generatedByS_false hgenerated
    (closedLoopScope_entry_carried h hmem)

theorem not_closedLoopScope_of_listed_inScope_false
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord}
    {entry : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (hmem : entry ∈ H.repairAuditEntries)
    (hscope : entry.entryClass.inScope = false) :
    ¬ ClosedLoopScope S H := by
  intro h
  exact not_repairTypedAuditEntryCarried_of_inScope_false hscope
    (closedLoopScope_entry_carried h hmem)

theorem fallback_entry_cannot_borrow_carriedness
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {carriedEntry fallbackEntry :
      RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord}
    (_sameValue : SameRepairRecordValue carriedEntry fallbackEntry)
    (_carriedOther : RepairTypedAuditEntryCarried S carriedEntry)
    (hfallback :
      fallbackEntry.entryClass.sourceTag = FineSourceTag.fallback) :
    ¬ RepairTypedAuditEntryCarried S fallbackEntry :=
  not_repairTypedAuditEntryCarried_of_source_fallback hfallback

end SixBirdsFoundationsV
