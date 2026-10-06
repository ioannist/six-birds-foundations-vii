import FoundationsVII.Prior.Metadata
import SixBirdsFoundationsV.Definitional.ESystem
import SixBirdsFoundationsV.Laws.E6E9PricedAccess
import ClosureLadder.Basic
import SixBirds.Admissibility

/-!
# Inherited foundational-object anchors

`TheoryPackage` has an exact inherited declaration.  `InterfaceLens` is an
inherited composite role rather than one local declaration in the supplied
scaffold; Phase 1 anchors it to the access-policy and closure/interface
surfaces without claiming a definitional identification.
-/

#check SixBirdsFoundationsV.TheoryPackage
#check SixBirdsFoundationsV.AccessPolicy
#check ClosureOp
#check ClosureLadder
#check SixBirds.ClaimRecord
#check SixBirds.NonclaimRecord

namespace FoundationsVII.Prior

structure FoundationalObjectAnchor where
  objectId : String
  status : String
  sourceModules : List String
  sourceDeclarations : List String
  exactSingleDeclaration : Bool
  nonclaims : List String
  deriving Repr, DecidableEq, BEq

def theoryPackageAnchor : FoundationalObjectAnchor :=
  { objectId := "VII-O01"
    status := "INHERITED_EXACT_DECLARATION"
    sourceModules := ["SixBirdsFoundationsV.Definitional.ESystem"]
    sourceDeclarations := ["SixBirdsFoundationsV.TheoryPackage"]
    exactSingleDeclaration := true
    nonclaims := ["The Phase-1 kernel does not replace the inherited theory package."] }

def interfaceLensAnchor : FoundationalObjectAnchor :=
  { objectId := "VII-O02"
    status := "INHERITED_COMPOSITE_INTERFACE_ROLE"
    sourceModules := ["SixBirdsFoundationsV.Laws.E6E9PricedAccess", "ClosureLadder.Basic"]
    sourceDeclarations := ["SixBirdsFoundationsV.AccessPolicy", "ClosureOp", "ClosureLadder"]
    exactSingleDeclaration := false
    nonclaims := ["No single inherited declaration is asserted to be definitionally equal to every VII interface lens."] }

def auditRecordAnchor : FoundationalObjectAnchor :=
  { objectId := "VII-O03"
    status := "INHERITED_ROLE_WITH_VII_APPEND_ONLY_DATA_MODEL"
    sourceModules := ["SixBirds.Admissibility"]
    sourceDeclarations := ["SixBirds.ClaimRecord", "SixBirds.NonclaimRecord"]
    exactSingleDeclaration := false
    nonclaims := ["FoundationsVII.AuditRecord is a local append-only representation, not a theorem identifying all inherited audit objects."] }

end FoundationsVII.Prior
