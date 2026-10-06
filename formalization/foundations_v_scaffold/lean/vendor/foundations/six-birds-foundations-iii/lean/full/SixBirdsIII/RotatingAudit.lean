namespace SixBirdsIII

structure InstrumentStack where
  length : Nat
  finiteRecords : Bool
  admissibleLowerStack : Bool
  strictlyIncreasingLevels : Bool
  stackDefectEmpty : Bool
deriving Repr

structure RotatingAuditExtension where
  lower : InstrumentStack
  extensionInstrumentPresent : Bool
  extensionLevelHigher : Bool
  targetScopeCoversLowerStack : Bool
  bridgeAdmissible : Bool
  reportAccepted : Bool
  stackDefectEmpty : Bool
  complianceAccepted : Bool
  selfSoundnessAccepted : Bool
deriving Repr

def oneLevelRotatingAuditExtension
    (stack : InstrumentStack)
    (_hfinite : stack.finiteRecords = true)
    (_hadm : stack.admissibleLowerStack = true)
    (_hlevels : stack.strictlyIncreasingLevels = true) :
    RotatingAuditExtension :=
  { lower := stack
    extensionInstrumentPresent := true
    extensionLevelHigher := true
    targetScopeCoversLowerStack := true
    bridgeAdmissible := true
    reportAccepted := true
    stackDefectEmpty := stack.stackDefectEmpty
    complianceAccepted := stack.stackDefectEmpty
    selfSoundnessAccepted := false }

theorem finite_rotating_audit
    (stack : InstrumentStack)
    (hfinite : stack.finiteRecords = true)
    (hadm : stack.admissibleLowerStack = true)
    (hlevels : stack.strictlyIncreasingLevels = true) :
    exists ext : RotatingAuditExtension,
      ext.lower = stack /\
      ext.extensionInstrumentPresent = true /\
      ext.extensionLevelHigher = true /\
      ext.bridgeAdmissible = true /\
      ext.reportAccepted = true /\
      (ext.complianceAccepted = true <-> ext.stackDefectEmpty = true) /\
      ext.selfSoundnessAccepted = false := by
  refine ⟨oneLevelRotatingAuditExtension stack hfinite hadm hlevels, ?_⟩
  simp [oneLevelRotatingAuditExtension]

def toyCleanInstrumentStack : InstrumentStack :=
  { length := 2
    finiteRecords := true
    admissibleLowerStack := true
    strictlyIncreasingLevels := true
    stackDefectEmpty := true }

def toyDefectiveInstrumentStack : InstrumentStack :=
  { toyCleanInstrumentStack with
    stackDefectEmpty := false }

end SixBirdsIII
