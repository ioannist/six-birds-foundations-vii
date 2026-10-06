import SixBirdsFoundationsV.Definitional.CarriedRecord

namespace SixBirdsFoundationsV

/-!
D4 endogenous closure systems.

The theory package is deliberately parametric and Mathlib-free.  Formedness,
ledger completeness, admissibility, and instrument gating are certified inputs,
not derived here.  Carried records and carried instruments reuse D3 directly.
-/

def RepairSort : Type :=
  { p : SixBirdsIII.Primitive // p ≠ SixBirdsIII.Primitive.P6 }

structure TheoryPackage
    (FData : Type u) (RuleFamily : Type v)
    (ResidualFamily : Type w) (AuditAccessData : Type x) where
  Z : Type z
  suppK : Z -> Z -> Prop
  LegitimateStart : (Nat -> Z) -> Nat -> Prop
  tau : Nat -> Z
  StepInScope : Nat -> Prop
  nStart : Nat
  f : FData
  Sigma_f : RuleFamily
  E : ResidualFamily
  A : AuditAccessData
  FormedPackage : Prop
  formed : FormedPackage

structure CarriedRecordPolicy
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    (T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData)
    (Record : Type y) where
  coordinateDeclared : (T.Z -> Record) -> Prop
  rhoOf : T.Z -> Record

def CarriedRecordAt
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {Record : Type y}
    (policy : CarriedRecordPolicy T Record)
    (rho : Record) (n0 : Nat)
    (sourceTag : FineSourceTag) (generatedByS inScope : Bool) : Prop :=
  CarriedRecord policy.coordinateDeclared policy.rhoOf rho
    T.LegitimateStart T.suppK T.tau T.StepInScope T.nStart n0
    sourceTag generatedByS inScope

structure CarriedRecordEvidence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {Record : Type y}
    (policy : CarriedRecordPolicy T Record) (rho : Record) where
  n0 : Nat
  sourceTag : FineSourceTag
  generatedByS : Bool
  inScope : Bool
  carried : CarriedRecordAt policy rho n0 sourceTag generatedByS inScope

def HasCarriedRecordEvidence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {Record : Type y}
    (policy : CarriedRecordPolicy T Record) (rho : Record) : Prop :=
  Nonempty (CarriedRecordEvidence policy rho)

structure CarriedLedger
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    (T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData)
    (LedgerEntry : Type y) where
  ledgerPolicy : CarriedRecordPolicy T LedgerEntry
  ledgerEntries : List LedgerEntry
  completeLedgerInventory : Prop
  ledgerComplete : completeLedgerInventory
  ledgerCarried :
    ∀ entry : LedgerEntry, entry ∈ ledgerEntries ->
      HasCarriedRecordEvidence ledgerPolicy entry

structure RepairMove
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    (T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData)
    (MovePayload : Type y) (LedgerEntry : Type y') (MoveRecord : Type y'')
    (moveRecordPolicy : CarriedRecordPolicy T MoveRecord) where
  sort : RepairSort
  payload : MovePayload
  moveRecord : MoveRecord
  moveRecordCarried : HasCarriedRecordEvidence moveRecordPolicy moveRecord
  budgetLine : LedgerEntry

structure ActiveCarriedInstrument
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    (T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData)
    (InstrumentRecord : Type y) (DefectRecord : Type y')
    (MovePayload : Type y'') (LedgerEntry : Type y''')
    (MoveRecord : Type y'''') (AuditRecord : Type y''''')
    (moveRecordPolicy : CarriedRecordPolicy T MoveRecord) where
  instrument : SixBirdsIII.Instrument
  instrumentRecordCarried : InstrumentRecord -> Prop
  recordsAreCompleteInventory : Prop
  visibilityRecords : List InstrumentRecord
  thresholdRecords : List InstrumentRecord
  checkRuleRecords : List (CheckRuleRecord InstrumentRecord)
  carried :
    CarriedInstrument instrumentRecordCarried instrument
      recordsAreCompleteInventory visibilityRecords thresholdRecords
      checkRuleRecords
  Detects : T.Z -> DefectRecord -> Prop
  GateAllows :
    T.Z -> DefectRecord ->
      RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy -> Prop
  ReAudits :
    T.Z -> RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy ->
      T.Z -> AuditRecord -> Prop

structure LawfulRepairStep
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (ledger : CarriedLedger T LedgerEntry)
    (defectRecordPolicy : CarriedRecordPolicy T DefectRecord)
    (moveRecordPolicy : CarriedRecordPolicy T MoveRecord)
    (auditRecordPolicy : CarriedRecordPolicy T AuditRecord)
    (I_S :
      ActiveCarriedInstrument T InstrumentRecord DefectRecord MovePayload
        LedgerEntry MoveRecord AuditRecord moveRecordPolicy)
    (AdmissibleMove :
      CarriedLedger T LedgerEntry -> T.Z -> DefectRecord ->
        RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy -> Prop)
    (z z' : T.Z) (defect : DefectRecord)
    (move : RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy)
    (auditRecord : AuditRecord) : Prop where
  defectCarried : HasCarriedRecordEvidence defectRecordPolicy defect
  detected : I_S.Detects z defect
  gateAllowed : I_S.GateAllows z defect move
  admissible : AdmissibleMove ledger z defect move
  budgetLineInLedger : move.budgetLine ∈ ledger.ledgerEntries
  realizedByKernel : T.suppK z z'
  reAudited : I_S.ReAudits z move z' auditRecord
  auditRecordCarried : HasCarriedRecordEvidence auditRecordPolicy auditRecord

def RepairGeneratorStep
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (ledger : CarriedLedger T LedgerEntry)
    (defectRecordPolicy : CarriedRecordPolicy T DefectRecord)
    (moveRecordPolicy : CarriedRecordPolicy T MoveRecord)
    (auditRecordPolicy : CarriedRecordPolicy T AuditRecord)
    (I_S :
      ActiveCarriedInstrument T InstrumentRecord DefectRecord MovePayload
        LedgerEntry MoveRecord AuditRecord moveRecordPolicy)
    (AdmissibleMove :
      CarriedLedger T LedgerEntry -> T.Z -> DefectRecord ->
        RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy -> Prop)
    (R_S :
      DefectRecord ->
        RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy)
    (z z' : T.Z) (defect : DefectRecord)
    (auditRecord : AuditRecord) : Prop :=
  LawfulRepairStep ledger defectRecordPolicy moveRecordPolicy auditRecordPolicy
    I_S AdmissibleMove z z' defect (R_S defect) auditRecord

structure ESystem
    (FData : Type u) (RuleFamily : Type v)
    (ResidualFamily : Type w) (AuditAccessData : Type x)
    (InstrumentRecord : Type y) (LedgerEntry : Type y')
    (DefectRecord : Type y'') (MovePayload : Type y''')
    (MoveRecord : Type y'''') (AuditRecord : Type y''''') where
  T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData
  defectRecordPolicy : CarriedRecordPolicy T DefectRecord
  moveRecordPolicy : CarriedRecordPolicy T MoveRecord
  auditRecordPolicy : CarriedRecordPolicy T AuditRecord
  I_S :
    ActiveCarriedInstrument T InstrumentRecord DefectRecord MovePayload
      LedgerEntry MoveRecord AuditRecord moveRecordPolicy
  Lambda_S : CarriedLedger T LedgerEntry
  R_S :
    DefectRecord ->
      RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy
  AdmissibleMove :
    CarriedLedger T LedgerEntry -> T.Z -> DefectRecord ->
      RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy -> Prop

def ESystem.RepairStep
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (z z' : S.T.Z) (defect : DefectRecord) (auditRecord : AuditRecord) : Prop :=
  RepairGeneratorStep S.Lambda_S S.defectRecordPolicy S.moveRecordPolicy
    S.auditRecordPolicy S.I_S S.AdmissibleMove S.R_S
    z z' defect auditRecord

theorem repairSort_ne_p6 (sort : RepairSort) :
    sort.val ≠ SixBirdsIII.Primitive.P6 :=
  sort.property

theorem no_repairSort_p6 (sort : RepairSort)
    (h : sort.val = SixBirdsIII.Primitive.P6) : False :=
  sort.property h

theorem carriedLedger_has_complete_inventory
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {LedgerEntry : Type y}
    (ledger : CarriedLedger T LedgerEntry) :
    ledger.completeLedgerInventory :=
  ledger.ledgerComplete

theorem no_carriedLedger_with_false_inventory
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {LedgerEntry : Type y}
    (ledger : CarriedLedger T LedgerEntry)
    (hfalse : ledger.completeLedgerInventory = False) : False := by
  have hcomplete : ledger.completeLedgerInventory := ledger.ledgerComplete
  rw [hfalse] at hcomplete
  exact hcomplete

theorem carriedRecordEvidence_uses_policy
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {Record : Type y}
    {policy : CarriedRecordPolicy T Record} {rho : Record}
    (h : CarriedRecordEvidence policy rho) :
    CarriedRecordAt policy rho h.n0 h.sourceTag h.generatedByS h.inScope :=
  h.carried

theorem hasCarriedRecordEvidence_uses_policy
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {Record : Type y}
    {policy : CarriedRecordPolicy T Record} {rho : Record}
    (h : HasCarriedRecordEvidence policy rho) :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policy rho n0 sourceTag generatedByS inScope := by
  cases h with
  | intro evidence =>
      exact
        ⟨evidence.n0, evidence.sourceTag, evidence.generatedByS,
          evidence.inScope, evidence.carried⟩

theorem not_hasCarriedRecordEvidence_without_policy_witness
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {Record : Type y}
    {policy : CarriedRecordPolicy T Record} {rho : Record}
    (hnot :
      ∀ n0 : Nat, ∀ sourceTag : FineSourceTag,
        ∀ generatedByS inScope : Bool,
          ¬ CarriedRecordAt policy rho n0 sourceTag generatedByS inScope) :
    ¬ HasCarriedRecordEvidence policy rho := by
  intro h
  cases h with
  | intro evidence =>
      exact
        hnot evidence.n0 evidence.sourceTag evidence.generatedByS
          evidence.inScope evidence.carried

theorem carriedLedger_entry_uses_policy
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {LedgerEntry : Type y}
    (ledger : CarriedLedger T LedgerEntry)
    {entry : LedgerEntry} (hmem : entry ∈ ledger.ledgerEntries) :
    HasCarriedRecordEvidence ledger.ledgerPolicy entry :=
  ledger.ledgerCarried entry hmem

theorem repairMove_record_uses_policy
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {MovePayload : Type y} {LedgerEntry : Type y'} {MoveRecord : Type y''}
    {moveRecordPolicy : CarriedRecordPolicy T MoveRecord}
    (move : RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy) :
    HasCarriedRecordEvidence moveRecordPolicy move.moveRecord :=
  move.moveRecordCarried

theorem activeCarriedInstrument_has_carried_instrument
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {InstrumentRecord : Type y} {DefectRecord : Type y'}
    {MovePayload : Type y''} {LedgerEntry : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {moveRecordPolicy : CarriedRecordPolicy T MoveRecord}
    (I_S :
      ActiveCarriedInstrument T InstrumentRecord DefectRecord MovePayload
        LedgerEntry MoveRecord AuditRecord moveRecordPolicy) :
    CarriedInstrument I_S.instrumentRecordCarried I_S.instrument
      I_S.recordsAreCompleteInventory I_S.visibilityRecords
      I_S.thresholdRecords I_S.checkRuleRecords :=
  I_S.carried

theorem lawfulRepairStep_requires_detection
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ledger : CarriedLedger T LedgerEntry}
    {defectRecordPolicy : CarriedRecordPolicy T DefectRecord}
    {moveRecordPolicy : CarriedRecordPolicy T MoveRecord}
    {auditRecordPolicy : CarriedRecordPolicy T AuditRecord}
    {I_S :
      ActiveCarriedInstrument T InstrumentRecord DefectRecord MovePayload
        LedgerEntry MoveRecord AuditRecord moveRecordPolicy}
    {AdmissibleMove :
      CarriedLedger T LedgerEntry -> T.Z -> DefectRecord ->
        RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy -> Prop}
    {z z' : T.Z} {defect : DefectRecord}
    {move : RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy}
    {auditRecord : AuditRecord}
    (h :
      LawfulRepairStep ledger defectRecordPolicy moveRecordPolicy
        auditRecordPolicy I_S AdmissibleMove z z' defect move
        auditRecord) :
    I_S.Detects z defect :=
  h.detected

theorem lawfulRepairStep_requires_gate
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ledger : CarriedLedger T LedgerEntry}
    {defectRecordPolicy : CarriedRecordPolicy T DefectRecord}
    {moveRecordPolicy : CarriedRecordPolicy T MoveRecord}
    {auditRecordPolicy : CarriedRecordPolicy T AuditRecord}
    {I_S :
      ActiveCarriedInstrument T InstrumentRecord DefectRecord MovePayload
        LedgerEntry MoveRecord AuditRecord moveRecordPolicy}
    {AdmissibleMove :
      CarriedLedger T LedgerEntry -> T.Z -> DefectRecord ->
        RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy -> Prop}
    {z z' : T.Z} {defect : DefectRecord}
    {move : RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy}
    {auditRecord : AuditRecord}
    (h :
      LawfulRepairStep ledger defectRecordPolicy moveRecordPolicy
        auditRecordPolicy I_S AdmissibleMove z z' defect move
        auditRecord) :
    I_S.GateAllows z defect move :=
  h.gateAllowed

theorem lawfulRepairStep_requires_kernel_transition
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ledger : CarriedLedger T LedgerEntry}
    {defectRecordPolicy : CarriedRecordPolicy T DefectRecord}
    {moveRecordPolicy : CarriedRecordPolicy T MoveRecord}
    {auditRecordPolicy : CarriedRecordPolicy T AuditRecord}
    {I_S :
      ActiveCarriedInstrument T InstrumentRecord DefectRecord MovePayload
        LedgerEntry MoveRecord AuditRecord moveRecordPolicy}
    {AdmissibleMove :
      CarriedLedger T LedgerEntry -> T.Z -> DefectRecord ->
        RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy -> Prop}
    {z z' : T.Z} {defect : DefectRecord}
    {move : RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy}
    {auditRecord : AuditRecord}
    (h :
      LawfulRepairStep ledger defectRecordPolicy moveRecordPolicy
        auditRecordPolicy I_S AdmissibleMove z z' defect move
        auditRecord) :
    T.suppK z z' :=
  h.realizedByKernel

theorem lawfulRepairStep_requires_reaudit
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ledger : CarriedLedger T LedgerEntry}
    {defectRecordPolicy : CarriedRecordPolicy T DefectRecord}
    {moveRecordPolicy : CarriedRecordPolicy T MoveRecord}
    {auditRecordPolicy : CarriedRecordPolicy T AuditRecord}
    {I_S :
      ActiveCarriedInstrument T InstrumentRecord DefectRecord MovePayload
        LedgerEntry MoveRecord AuditRecord moveRecordPolicy}
    {AdmissibleMove :
      CarriedLedger T LedgerEntry -> T.Z -> DefectRecord ->
        RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy -> Prop}
    {z z' : T.Z} {defect : DefectRecord}
    {move : RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy}
    {auditRecord : AuditRecord}
    (h :
      LawfulRepairStep ledger defectRecordPolicy moveRecordPolicy
        auditRecordPolicy I_S AdmissibleMove z z' defect move
        auditRecord) :
    I_S.ReAudits z move z' auditRecord :=
  h.reAudited

theorem not_lawfulRepairStep_without_detection
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ledger : CarriedLedger T LedgerEntry}
    {defectRecordPolicy : CarriedRecordPolicy T DefectRecord}
    {moveRecordPolicy : CarriedRecordPolicy T MoveRecord}
    {auditRecordPolicy : CarriedRecordPolicy T AuditRecord}
    {I_S :
      ActiveCarriedInstrument T InstrumentRecord DefectRecord MovePayload
        LedgerEntry MoveRecord AuditRecord moveRecordPolicy}
    {AdmissibleMove :
      CarriedLedger T LedgerEntry -> T.Z -> DefectRecord ->
        RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy -> Prop}
    {z z' : T.Z} {defect : DefectRecord}
    {move : RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy}
    {auditRecord : AuditRecord}
    (hnot : ¬ I_S.Detects z defect) :
    ¬ LawfulRepairStep ledger defectRecordPolicy moveRecordPolicy
      auditRecordPolicy I_S AdmissibleMove z z' defect move auditRecord := by
  intro h
  exact hnot h.detected

theorem not_lawfulRepairStep_without_gate
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ledger : CarriedLedger T LedgerEntry}
    {defectRecordPolicy : CarriedRecordPolicy T DefectRecord}
    {moveRecordPolicy : CarriedRecordPolicy T MoveRecord}
    {auditRecordPolicy : CarriedRecordPolicy T AuditRecord}
    {I_S :
      ActiveCarriedInstrument T InstrumentRecord DefectRecord MovePayload
        LedgerEntry MoveRecord AuditRecord moveRecordPolicy}
    {AdmissibleMove :
      CarriedLedger T LedgerEntry -> T.Z -> DefectRecord ->
        RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy -> Prop}
    {z z' : T.Z} {defect : DefectRecord}
    {move : RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy}
    {auditRecord : AuditRecord}
    (hnot : ¬ I_S.GateAllows z defect move) :
    ¬ LawfulRepairStep ledger defectRecordPolicy moveRecordPolicy
      auditRecordPolicy I_S AdmissibleMove z z' defect move auditRecord := by
  intro h
  exact hnot h.gateAllowed

theorem not_lawfulRepairStep_without_kernel_transition
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ledger : CarriedLedger T LedgerEntry}
    {defectRecordPolicy : CarriedRecordPolicy T DefectRecord}
    {moveRecordPolicy : CarriedRecordPolicy T MoveRecord}
    {auditRecordPolicy : CarriedRecordPolicy T AuditRecord}
    {I_S :
      ActiveCarriedInstrument T InstrumentRecord DefectRecord MovePayload
        LedgerEntry MoveRecord AuditRecord moveRecordPolicy}
    {AdmissibleMove :
      CarriedLedger T LedgerEntry -> T.Z -> DefectRecord ->
        RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy -> Prop}
    {z z' : T.Z} {defect : DefectRecord}
    {move : RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy}
    {auditRecord : AuditRecord}
    (hnot : ¬ T.suppK z z') :
    ¬ LawfulRepairStep ledger defectRecordPolicy moveRecordPolicy
      auditRecordPolicy I_S AdmissibleMove z z' defect move auditRecord := by
  intro h
  exact hnot h.realizedByKernel

theorem not_lawfulRepairStep_without_reaudit
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ledger : CarriedLedger T LedgerEntry}
    {defectRecordPolicy : CarriedRecordPolicy T DefectRecord}
    {moveRecordPolicy : CarriedRecordPolicy T MoveRecord}
    {auditRecordPolicy : CarriedRecordPolicy T AuditRecord}
    {I_S :
      ActiveCarriedInstrument T InstrumentRecord DefectRecord MovePayload
        LedgerEntry MoveRecord AuditRecord moveRecordPolicy}
    {AdmissibleMove :
      CarriedLedger T LedgerEntry -> T.Z -> DefectRecord ->
        RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy -> Prop}
    {z z' : T.Z} {defect : DefectRecord}
    {move : RepairMove T MovePayload LedgerEntry MoveRecord moveRecordPolicy}
    {auditRecord : AuditRecord}
    (hnot : ¬ I_S.ReAudits z move z' auditRecord) :
    ¬ LawfulRepairStep ledger defectRecordPolicy moveRecordPolicy
      auditRecordPolicy I_S AdmissibleMove z z' defect move auditRecord := by
  intro h
  exact hnot h.reAudited

end SixBirdsFoundationsV
