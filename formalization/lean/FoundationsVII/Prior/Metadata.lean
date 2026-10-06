/-!
Machine-auditable metadata for narrow inherited adapters.  The metadata is not a
proof of transport; it records exactly what a later bridge must preserve.
-/

namespace FoundationsVII.Prior

structure AdapterMetadata where
  adapterId : String
  formalizationTarget : String
  sourceModule : String
  sourceDeclaration : String
  sourceType : String
  targetType : String
  preservedHypotheses : List String
  addedHypotheses : List String
  lostHypotheses : List String
  trustDependencies : List String
  deriving Repr, DecidableEq, BEq

end FoundationsVII.Prior
