import FoundationsVII.Core.Audit

/-!
# Domain state and the seven access coordinates

Expressibility, presence, exposure, recoverability, admissibility,
reachability, and occurrence are separate fields.  `Coherent` records only the
Phase-1 implication spine; later phases may add domain-specific hypotheses.
-/

namespace FoundationsVII

structure DomainState where
  theoryId : TheoryId
  interfaceId : InterfaceId
  scopeId : ScopeId
  timestamp : Timestamp
  expressible : Bool
  present : Bool
  exposed : Bool
  recoverable : Bool
  admissible : Bool
  reachable : Bool
  occurrent : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace DomainState

def Coherent (state : DomainState) : Prop :=
  (state.occurrent = true → state.reachable = true) ∧
  (state.reachable = true → state.admissible = true) ∧
  (state.admissible = true → state.present = true) ∧
  (state.recoverable = true → state.exposed = true) ∧
  (state.exposed = true → state.present = true) ∧
  (state.present = true → state.expressible = true) ∧
  state.audit.entries ≠ []

instance (state : DomainState) : Decidable (Coherent state) := by
  unfold Coherent
  infer_instance


theorem constructed_coherent (state : DomainState)
    (hOccurrence : state.occurrent = true → state.reachable = true)
    (hReachability : state.reachable = true → state.admissible = true)
    (hAdmission : state.admissible = true → state.present = true)
    (hRecovery : state.recoverable = true → state.exposed = true)
    (hExposure : state.exposed = true → state.present = true)
    (hPresence : state.present = true → state.expressible = true)
    (hAudit : state.audit.entries ≠ []) : Coherent state := by
  exact ⟨hOccurrence, hReachability, hAdmission, hRecovery, hExposure,
    hPresence, hAudit⟩

theorem occurrence_implies_reachability {state : DomainState}
    (h : Coherent state) (hOccurrent : state.occurrent = true) :
    state.reachable = true := h.1 hOccurrent

theorem reachability_implies_admissibility {state : DomainState}
    (h : Coherent state) (hReachable : state.reachable = true) :
    state.admissible = true := h.2.1 hReachable

theorem admissibility_implies_presence {state : DomainState}
    (h : Coherent state) (hAdmissible : state.admissible = true) :
    state.present = true := h.2.2.1 hAdmissible

theorem recoverability_implies_exposure {state : DomainState}
    (h : Coherent state) (hRecoverable : state.recoverable = true) :
    state.exposed = true := h.2.2.2.1 hRecoverable

theorem exposure_implies_presence {state : DomainState}
    (h : Coherent state) (hExposed : state.exposed = true) :
    state.present = true := h.2.2.2.2.1 hExposed

theorem presence_implies_expressibility {state : DomainState}
    (h : Coherent state) (hPresent : state.present = true) :
    state.expressible = true := h.2.2.2.2.2.1 hPresent

end DomainState

end FoundationsVII
