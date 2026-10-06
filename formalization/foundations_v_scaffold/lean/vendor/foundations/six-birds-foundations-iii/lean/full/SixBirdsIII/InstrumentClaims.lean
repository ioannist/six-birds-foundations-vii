import SixBirdsIII.Status

namespace SixBirdsIII

structure InstrumentClaimRecord where
  inScope : Bool
  hasOutsideUse : Bool
  hasUnknownUse : Bool
  hasSuppressedUnbridgedUse : Bool
  hasWeakBridge : Bool
  absentWithRecord : Bool
  auditPasses : Bool
  circularSameLevel : Bool
  belowThreshold : Bool
  rejectedByEvidence : Bool
  provisionalEvidence : Bool
deriving Repr

def ClaimClassify (claim : InstrumentClaimRecord) : ClaimStatus :=
  if claim.inScope = false ∨ claim.hasOutsideUse = true then ClaimStatus.outsideScope
  else if claim.hasSuppressedUnbridgedUse = true ∨
      claim.hasWeakBridge = true ∨
      claim.hasUnknownUse = true then ClaimStatus.blocked
  else if claim.absentWithRecord = true then ClaimStatus.absentWithRecord
  else if claim.auditPasses = false then ClaimStatus.failedAudit
  else if claim.circularSameLevel = true then ClaimStatus.undefinedCircular
  else if claim.belowThreshold = true then ClaimStatus.belowThreshold
  else if claim.rejectedByEvidence = true then ClaimStatus.rejected
  else if claim.provisionalEvidence = true then ClaimStatus.provisional
  else ClaimStatus.accepted

theorem no_overreading_suppression (claim : InstrumentClaimRecord) :
    ClaimClassify claim = ClaimStatus.accepted ->
      claim.hasSuppressedUnbridgedUse = false := by
  intro haccepted
  unfold ClaimClassify at haccepted
  by_cases hscope : claim.inScope = false ∨ claim.hasOutsideUse = true
  · simp [hscope] at haccepted
  · simp [hscope] at haccepted
    by_cases hvis : claim.hasSuppressedUnbridgedUse = true ∨
        claim.hasWeakBridge = true ∨
        claim.hasUnknownUse = true
    · simp [hvis] at haccepted
    · have hnotTrue : claim.hasSuppressedUnbridgedUse ≠ true := by
        intro htrue
        exact hvis (Or.inl htrue)
      cases hsu : claim.hasSuppressedUnbridgedUse
      · rfl
      · exact False.elim (hnotTrue hsu)

structure SameLevelSelfAuditClaim where
  inClaimTypes : Bool
  selfDependent : Bool
  hasLevelShiftBridge : Bool
deriving Repr

def SameLevelSelfAuditClassify (claim : SameLevelSelfAuditClaim) : ClaimStatus :=
  if claim.hasLevelShiftBridge = true then ClaimStatus.provisional
  else if claim.inClaimTypes = false then ClaimStatus.outsideScope
  else if claim.selfDependent = true then ClaimStatus.undefinedCircular
  else ClaimStatus.undefinedCircular

theorem same_level_self_audit_failure
    (claim : SameLevelSelfAuditClaim)
    (hnoShift : claim.hasLevelShiftBridge = false) :
  SameLevelSelfAuditClassify claim ≠ ClaimStatus.accepted := by
  unfold SameLevelSelfAuditClassify
  cases claim.inClaimTypes <;> cases claim.selfDependent <;> simp [hnoShift]

def suppressedUnbridgedClaim : InstrumentClaimRecord :=
  { inScope := true
    hasOutsideUse := false
    hasUnknownUse := false
    hasSuppressedUnbridgedUse := true
    hasWeakBridge := false
    absentWithRecord := false
    auditPasses := true
    circularSameLevel := false
    belowThreshold := false
    rejectedByEvidence := false
    provisionalEvidence := false }

def outsideAndSuppressedClaim : InstrumentClaimRecord :=
  { suppressedUnbridgedClaim with
    hasOutsideUse := true }

def acceptedVisibleClaim : InstrumentClaimRecord :=
  { suppressedUnbridgedClaim with
    hasSuppressedUnbridgedUse := false }

def circularSelfAuditClaim : SameLevelSelfAuditClaim :=
  { inClaimTypes := true
    selfDependent := true
    hasLevelShiftBridge := false }

def outsideScopeSelfAuditClaim : SameLevelSelfAuditClaim :=
  { inClaimTypes := false
    selfDependent := false
    hasLevelShiftBridge := false }

end SixBirdsIII
