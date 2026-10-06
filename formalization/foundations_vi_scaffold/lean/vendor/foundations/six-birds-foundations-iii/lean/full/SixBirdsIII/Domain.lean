import SixBirdsIII.Status

namespace SixBirdsIII

inductive ThresholdTag where
  | exactZero
  | nonzero
  | atMostTolerance
  | atLeastTolerance
  | member
  | notMember
  | pass
  | source
  | bridge
  | audit
  | visibility
  deriving DecidableEq, Repr

inductive VisibilityTag where
  | visible
  | suppressed
  | outside
  | unknown
  deriving DecidableEq, Repr

inductive SourceTag where
  | real
  | fallback
  | dirty
  | proxy
  | missing
  deriving DecidableEq, Repr

inductive AuditTag where
  | passes
  | missing
  | failed
  | sourceFailure
  | visibilityFailure
  | thresholdFailure
  | nonclaimFailure
  | circular
  deriving DecidableEq, Repr

structure Profile where
  actorLevel : Level
  informantLevel : Level
  host : Host
  isLocal : Bool
  deriving Repr

structure Instrument where
  host : Host
  level : Level
  canBridgeSuppressed : Bool
  auditRequired : Bool
  deriving Repr

def baseProfile : Profile :=
  { actorLevel := Level.behavioral
    informantLevel := Level.behavioral
    host := Host.fin
    isLocal := true }

def baseInstrument : Instrument :=
  { host := Host.fin
    level := Level.verification
    canBridgeSuppressed := false
    auditRequired := true }

end SixBirdsIII
