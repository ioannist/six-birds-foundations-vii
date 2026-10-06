import SixBirdsMetaMath.FoundationsIV.Stability.SufficiencyClosure
import SixBirdsMetaMath.FoundationsIV.Transport.LocalGlobalObstruction

/-!
F40 Anomaly / Symmetry Obstruction.

Layer-agnostic anomaly: a would-be symmetry source fails to become a symmetry
of a formed layer because descent, gluing, group-law, readout, audit, or
residual-status preservation fails.
-/

namespace SixBirdsMetaMath.FoundationsIV.Symmetry.Anomaly

open SixBirdsMetaMath.FoundationsIV.Transport.DescentRepair
open SixBirdsMetaMath.FoundationsIV.Stability.SufficiencyClosure
open SixBirdsMetaMath.FoundationsIV.Transport.LocalGlobalObstruction

/-- Same layer object, different transformed layer object. -/
def SymmetryDescentSplit {G H Q : Type} (q : H → Q) (act : G → H → H) :
    G × (H × H) → Prop :=
  fun item =>
    q item.2.1 = q item.2.2 ∧
      q (act item.1 item.2.1) ≠ q (act item.1 item.2.2)

/-- A raw symmetry action descends through the layer quotient. -/
def SymmetryDescends {G H Q : Type} (q : H → Q) (act : G → H → H) :
    Prop :=
  ∀ g : G, FactorsThroughQ q (fun h => q (act g h))

/-- No symmetry descent obstruction is present. -/
def SymmetryDescentObstructionEmpty {G H Q : Type} (q : H → Q)
    (act : G → H → H) : Prop :=
  ObstructionEmpty (SymmetryDescentSplit q act)

/-- Domain admissibility for a partial symmetry action descends through the
layer quotient. Boolean domains avoid adding decidability hypotheses. -/
def DomainDescends {G H Q : Type} (q : H → Q) (domain : G → H → Bool) :
    Prop :=
  ∀ g : G, FactorsThroughQ q (domain g)

/-- Same layer object, different symmetry-domain admissibility. -/
def DomainDescentSplit {G H Q : Type} (q : H → Q)
    (domain : G → H → Bool) : G × (H × H) → Prop :=
  fun item =>
    q item.2.1 = q item.2.2 ∧
      domain item.1 item.2.1 ≠ domain item.1 item.2.2

/-- No domain-descent obstruction is present. -/
def DomainObstructionEmpty {G H Q : Type} (q : H → Q)
    (domain : G → H → Bool) : Prop :=
  ObstructionEmpty (DomainDescentSplit q domain)

/-- Descended actions preserve the declared group/monoid law. -/
def GroupLawPreserved {G Q : Type} (mul : G → G → G) (actQ : G → Q → Q) :
    Prop :=
  ∀ g h : G, ∀ q : Q, actQ (mul g h) q = actQ g (actQ h q)

/-- Group-law/cocycle obstruction at the layer. -/
def GroupLawObstruction {G Q : Type} (mul : G → G → G) (actQ : G → Q → Q) :
    G × (G × Q) → Prop :=
  fun item =>
    actQ (mul item.1 item.2.1) item.2.2 ≠
      actQ item.1 (actQ item.2.1 item.2.2)

/-- No group-law/cocycle obstruction is present. -/
def GroupLawObstructionEmpty {G Q : Type} (mul : G → G → G)
    (actQ : G → Q → Q) : Prop :=
  ObstructionEmpty (GroupLawObstruction mul actQ)

/-- A readout is invariant/covariant under the raw symmetry action. -/
def ReadoutPreserved {G H V : Type} (readout : H → V) (act : G → H → H)
    (rho : G → V → V) : Prop :=
  ∀ g : G, ∀ h : H, readout (act g h) = rho g (readout h)

/-- Readout/law preservation obstruction. -/
def ReadoutObstruction {G H V : Type} (readout : H → V) (act : G → H → H)
    (rho : G → V → V) : G × H → Prop :=
  fun item => readout (act item.1 item.2) ≠ rho item.1 (readout item.2)

/-- No readout preservation obstruction is present. -/
def ReadoutObstructionEmpty {G H V : Type} (readout : H → V)
    (act : G → H → H) (rho : G → V → V) : Prop :=
  ObstructionEmpty (ReadoutObstruction readout act rho)

/-- Residual/audit status preservation under a symmetry action. -/
def AuditPreserved {G Rec Status : Type} (status : Rec → Status)
    (actRec : G → Rec → Rec) (actStatus : G → Status → Status) : Prop :=
  ∀ g : G, ∀ r : Rec, status (actRec g r) = actStatus g (status r)

/-- Audit/residual status preservation obstruction. -/
def AuditObstruction {G Rec Status : Type} (status : Rec → Status)
    (actRec : G → Rec → Rec) (actStatus : G → Status → Status) :
    G × Rec → Prop :=
  fun item => status (actRec item.1 item.2) ≠ actStatus item.1 (status item.2)

/-- No audit preservation obstruction is present. -/
def AuditObstructionEmpty {G Rec Status : Type} (status : Rec → Status)
    (actRec : G → Rec → Rec) (actStatus : G → Status → Status) : Prop :=
  ObstructionEmpty (AuditObstruction status actRec actStatus)

/-- A local symmetry family globalizes when it lies in the declared image of the
global restriction map. -/
def LocalSymmetryGlobalizes {Global Local : Type} (restrict : Global → Local)
    (localData : Local) : Prop :=
  ∃ global : Global, restrict global = localData

/-- Image-membership spelling of local-global symmetry gluing. -/
def InGlobalSymmetryImage {Global Local : Type} (restrict : Global → Local)
    (localData : Local) : Prop :=
  InDeclaredImage restrict localData

/-- Local symmetry gluing obstruction: compatible local data not in the global
restriction image. -/
def SymmetryGluingObstruction {Global Local : Type} (compatible : Local → Prop)
    (restrict : Global → Local) (localData : Local) : Prop :=
  compatible localData ∧ ¬ LocalSymmetryGlobalizes restrict localData

/-- Gates that must pass for a would-be symmetry to be a formed layer symmetry. -/
structure SymmetryGateProfile where
  symmetrySourceClaimed : Prop
  explicitBreakingRecorded : Prop
  domainDescent : Prop
  actionDescent : Prop
  groupLaw : Prop
  readoutPreservation : Prop
  auditPreservation : Prop
  localGlobalGluing : Prop

/-- A lawful layer symmetry has all declared gates passing. -/
def LawfulLayerSymmetry (profile : SymmetryGateProfile) : Prop :=
  profile.domainDescent ∧ profile.actionDescent ∧ profile.groupLaw ∧
    profile.readoutPreservation ∧ profile.auditPreservation ∧
      profile.localGlobalGluing

/-- An anomaly is a claimed symmetry source with failed layer realization, not
merely explicit breaking. -/
def Anomaly (profile : SymmetryGateProfile) : Prop :=
  profile.symmetrySourceClaimed ∧ ¬ profile.explicitBreakingRecorded ∧
    ¬ LawfulLayerSymmetry profile

/-- F40 anomaly status vocabulary. -/
inductive AnomalyStatus where
  | exactLayerSymmetry
  | covariantSymmetry
  | projectiveOrExtendedSymmetry
  | explicitSymmetryBreaking
  | descentAnomaly
  | domainAnomaly
  | cocycleAnomaly
  | lawSymmetryAnomaly
  | measureOrLedgerAnomaly
  | auditAnomaly
  | localGlobalAnomaly
  | boundarySymmetryAnomaly
  | anomalyCancelled
  | budgetedSymmetry
  | hiddenRestoredSymmetry
  | presentationArtifact
  | protocolSymmetryArtifact
  | anomalyOverread
deriving DecidableEq

/-- Meaning of each anomaly status. -/
def AnomalyStatusHolds (exact covariant projective explicitBreaking descent
    domain cocycle law ledger audit localGlobal boundary cancelled budgeted
    hiddenRestored presentationArtifact protocolArtifact overread : Prop) :
    AnomalyStatus → Prop
  | AnomalyStatus.exactLayerSymmetry => exact
  | AnomalyStatus.covariantSymmetry => covariant
  | AnomalyStatus.projectiveOrExtendedSymmetry => projective
  | AnomalyStatus.explicitSymmetryBreaking => explicitBreaking
  | AnomalyStatus.descentAnomaly => descent
  | AnomalyStatus.domainAnomaly => domain
  | AnomalyStatus.cocycleAnomaly => cocycle
  | AnomalyStatus.lawSymmetryAnomaly => law
  | AnomalyStatus.measureOrLedgerAnomaly => ledger
  | AnomalyStatus.auditAnomaly => audit
  | AnomalyStatus.localGlobalAnomaly => localGlobal
  | AnomalyStatus.boundarySymmetryAnomaly => boundary
  | AnomalyStatus.anomalyCancelled => cancelled
  | AnomalyStatus.budgetedSymmetry => budgeted
  | AnomalyStatus.hiddenRestoredSymmetry => hiddenRestored
  | AnomalyStatus.presentationArtifact => presentationArtifact
  | AnomalyStatus.protocolSymmetryArtifact => protocolArtifact
  | AnomalyStatus.anomalyOverread => overread

/-- Raw action descent is equivalent to absence of the symmetry descent
split-pair obstruction. -/
theorem symmetry_descends_iff_no_obstruction {G H Q : Type} (q : H → Q)
    (act : G → H → H) (hq : Function.Surjective q) :
    SymmetryDescends q act ↔ SymmetryDescentObstructionEmpty q act := by
  constructor
  · intro hdesc item hsplit
    rcases hdesc item.1 with ⟨actBar, hcomm⟩
    have hx : actBar (q item.2.1) = q (act item.1 item.2.1) :=
      congrFun hcomm item.2.1
    have hy : actBar (q item.2.2) = q (act item.1 item.2.2) :=
      congrFun hcomm item.2.2
    exact hsplit.2 (by
      calc
        q (act item.1 item.2.1) = actBar (q item.2.1) := hx.symm
        _ = actBar (q item.2.2) := by rw [hsplit.1]
        _ = q (act item.1 item.2.2) := hy)
  · intro hempty g
    have hclosed : PackageClosed q (fun h => q (act g h)) := by
      intro x y hxy
      exact Classical.byContradiction (fun hneq =>
        hempty (g, (x, y)) ⟨hxy, hneq⟩)
    exact (sufficiency_closure q (fun h => q (act g h)) hq).1.1 hclosed

/-- Partial-domain descent is equivalent to absence of domain obstruction. -/
theorem domain_descends_iff_no_obstruction {G H Q : Type} (q : H → Q)
    (domain : G → H → Bool) (hq : Function.Surjective q) :
    DomainDescends q domain ↔ DomainObstructionEmpty q domain := by
  constructor
  · intro hdesc item hsplit
    rcases hdesc item.1 with ⟨domainBar, hcomm⟩
    have hx : domainBar (q item.2.1) = domain item.1 item.2.1 :=
      congrFun hcomm item.2.1
    have hy : domainBar (q item.2.2) = domain item.1 item.2.2 :=
      congrFun hcomm item.2.2
    exact hsplit.2 (by
      calc
        domain item.1 item.2.1 = domainBar (q item.2.1) := hx.symm
        _ = domainBar (q item.2.2) := by rw [hsplit.1]
        _ = domain item.1 item.2.2 := hy)
  · intro hempty g
    have hclosed : PackageClosed q (domain g) := by
      intro x y hxy
      exact Classical.byContradiction (fun hneq =>
        hempty (g, (x, y)) ⟨hxy, hneq⟩)
    exact (sufficiency_closure q (domain g) hq).1.1 hclosed

/-- Group-law preservation is equivalent to empty group-law obstruction. -/
theorem group_law_iff_no_obstruction {G Q : Type} (mul : G → G → G)
    (actQ : G → Q → Q) :
    GroupLawPreserved mul actQ ↔ GroupLawObstructionEmpty mul actQ := by
  constructor
  · intro hpres item hobs
    exact hobs (hpres item.1 item.2.1 item.2.2)
  · intro hempty g h q
    exact Classical.byContradiction (fun hneq =>
      hempty (g, (h, q)) hneq)

/-- Readout/law preservation is equivalent to empty readout obstruction. -/
theorem readout_preserved_iff_no_obstruction {G H V : Type} (readout : H → V)
    (act : G → H → H) (rho : G → V → V) :
    ReadoutPreserved readout act rho ↔
      ReadoutObstructionEmpty readout act rho := by
  constructor
  · intro hpres item hobs
    exact hobs (hpres item.1 item.2)
  · intro hempty g h
    exact Classical.byContradiction (fun hneq =>
      hempty (g, h) hneq)

/-- Audit preservation is equivalent to empty audit obstruction. -/
theorem audit_preserved_iff_no_obstruction {G Rec Status : Type}
    (status : Rec → Status) (actRec : G → Rec → Rec)
    (actStatus : G → Status → Status) :
    AuditPreserved status actRec actStatus ↔
      AuditObstructionEmpty status actRec actStatus := by
  constructor
  · intro hpres item hobs
    exact hobs (hpres item.1 item.2)
  · intro hempty g r
    exact Classical.byContradiction (fun hneq =>
      hempty (g, r) hneq)

/-- Local symmetry data globalizes exactly when it lies in the image of the
global restriction map. -/
theorem local_symmetry_globalizes_iff_image {Global Local : Type}
    (restrict : Global → Local) (localData : Local) :
    LocalSymmetryGlobalizes restrict localData ↔
      InGlobalSymmetryImage restrict localData := by
  rfl

/-- The gate profile expands to the six formed-layer symmetry gates. -/
theorem lawful_layer_symmetry_iff_gates (profile : SymmetryGateProfile) :
    LawfulLayerSymmetry profile ↔
      profile.domainDescent ∧ profile.actionDescent ∧ profile.groupLaw ∧
        profile.readoutPreservation ∧ profile.auditPreservation ∧
          profile.localGlobalGluing := by
  rfl

/-- The anomaly predicate expands to source-present, not explicit breaking, and
failed formed-layer symmetry. -/
theorem anomaly_iff_failed_gate (profile : SymmetryGateProfile) :
    Anomaly profile ↔
      profile.symmetrySourceClaimed ∧ ¬ profile.explicitBreakingRecorded ∧
        ¬ LawfulLayerSymmetry profile := by
  rfl

/--
Anomaly / Symmetry Obstruction Normal Form. A raw/local/upstairs symmetry is a
formed layer symmetry exactly when descent, domain, group-law, readout, audit,
and local-global gates pass. Each gate is characterized by an empty typed
obstruction; anomaly means a symmetry source is claimed, explicit breaking is
not the status, and at least one formed-layer gate fails.
-/
theorem anomaly_symmetry_obstruction {G H Q V Rec Status Global Local : Type}
    (q : H → Q) (act : G → H → H) (domain : G → H → Bool)
    (hq : Function.Surjective q)
    (mul : G → G → G) (actQ : G → Q → Q)
    (readout : H → V) (rho : G → V → V)
    (status : Rec → Status) (actRec : G → Rec → Rec)
    (actStatus : G → Status → Status)
    (restrict : Global → Local) (localData : Local)
    (profile : SymmetryGateProfile) :
    (SymmetryDescends q act ↔ SymmetryDescentObstructionEmpty q act) ∧
      (DomainDescends q domain ↔ DomainObstructionEmpty q domain) ∧
        (GroupLawPreserved mul actQ ↔ GroupLawObstructionEmpty mul actQ) ∧
          (ReadoutPreserved readout act rho ↔
            ReadoutObstructionEmpty readout act rho) ∧
            (AuditPreserved status actRec actStatus ↔
              AuditObstructionEmpty status actRec actStatus) ∧
              (LocalSymmetryGlobalizes restrict localData ↔
                InGlobalSymmetryImage restrict localData) ∧
                (LawfulLayerSymmetry profile ↔
                  profile.domainDescent ∧ profile.actionDescent ∧
                    profile.groupLaw ∧ profile.readoutPreservation ∧
                      profile.auditPreservation ∧ profile.localGlobalGluing) ∧
                  (Anomaly profile ↔
                    profile.symmetrySourceClaimed ∧
                      ¬ profile.explicitBreakingRecorded ∧
                        ¬ LawfulLayerSymmetry profile) := by
  exact ⟨symmetry_descends_iff_no_obstruction q act hq,
    domain_descends_iff_no_obstruction q domain hq,
    group_law_iff_no_obstruction mul actQ,
    readout_preserved_iff_no_obstruction readout act rho,
    audit_preserved_iff_no_obstruction status actRec actStatus,
    local_symmetry_globalizes_iff_image restrict localData,
    lawful_layer_symmetry_iff_gates profile,
    anomaly_iff_failed_gate profile⟩

end SixBirdsMetaMath.FoundationsIV.Symmetry.Anomaly
