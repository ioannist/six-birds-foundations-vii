import FoundationsVII.Join.NonInteraction

/-!
# FVII-SCI-03 join no-go fronts

Each no-go is structural over an exact typed profile and has a separately named
positive escape.  The collection is not conflated into one universal theorem.
-/

namespace FoundationsVII.NoGo

structure ResemblanceJoinProfile where
  resemblance : Bool
  witnessedContact : Bool
  sourceIndependent : Bool
  independenceSensitiveCredit : Bool
  deriving Repr, DecidableEq, BEq

namespace ResemblanceJoinProfile

def Eligible (profile : ResemblanceJoinProfile) : Prop :=
  profile.witnessedContact = true ∧
  profile.sourceIndependent = true ∧
  profile.independenceSensitiveCredit = true

instance (profile : ResemblanceJoinProfile) : Decidable (Eligible profile) := by
  unfold Eligible
  infer_instance

def ResemblanceOnly (profile : ResemblanceJoinProfile) : Prop :=
  profile.resemblance = true ∧
  profile.witnessedContact = false ∧
  profile.sourceIndependent = false

end ResemblanceJoinProfile

theorem NGVII_02_no_resemblance_only_independence_join
    (profile : ResemblanceJoinProfile)
    (hOnly : ResemblanceJoinProfile.ResemblanceOnly profile) :
    ¬ ResemblanceJoinProfile.Eligible profile := by
  intro hEligible
  have hContact : profile.witnessedContact = true := hEligible.1
  rw [hOnly.2.1] at hContact
  exact Bool.noConfusion hContact

private def resemblanceEscapeProfile : ResemblanceJoinProfile :=
  { resemblance := true
    witnessedContact := true
    sourceIndependent := true
    independenceSensitiveCredit := true }

theorem NGVII_02_escape_witnessed_independent_contact :
    ResemblanceJoinProfile.Eligible resemblanceEscapeProfile := by decide

structure ContactOnlyJoinProfile where
  evidencedContact : Bool
  compositeObject : Bool
  parentRetention : Bool
  antiProductNovelty : Bool
  strictJoinCredit : Bool
  deriving Repr, DecidableEq, BEq

namespace ContactOnlyJoinProfile

def StrictEligible (profile : ContactOnlyJoinProfile) : Prop :=
  profile.evidencedContact = true ∧
  profile.compositeObject = true ∧
  profile.parentRetention = true ∧
  profile.antiProductNovelty = true ∧
  profile.strictJoinCredit = true

instance (profile : ContactOnlyJoinProfile) : Decidable (StrictEligible profile) := by
  unfold StrictEligible
  infer_instance

def ContactOnly (profile : ContactOnlyJoinProfile) : Prop :=
  profile.evidencedContact = true ∧
  profile.compositeObject = false ∧
  profile.parentRetention = false ∧
  profile.antiProductNovelty = false

end ContactOnlyJoinProfile

theorem NGVII_06_no_join_from_contact_alone
    (profile : ContactOnlyJoinProfile)
    (hOnly : ContactOnlyJoinProfile.ContactOnly profile) :
    ¬ ContactOnlyJoinProfile.StrictEligible profile := by
  intro hStrict
  have hComposite : profile.compositeObject = true := hStrict.2.1
  rw [hOnly.2.1] at hComposite
  exact Bool.noConfusion hComposite

private def strictJoinEscapeProfile : ContactOnlyJoinProfile :=
  { evidencedContact := true
    compositeObject := true
    parentRetention := true
    antiProductNovelty := true
    strictJoinCredit := true }

theorem NGVII_06_escape_complete_strict_join_certificate :
    ContactOnlyJoinProfile.StrictEligible strictJoinEscapeProfile := by decide

structure ProductJoinProfile where
  commonRefinement : Bool
  factorsThroughDeclaredBaseline : Bool
  antiProductWitness : Bool
  strictnessCredit : Bool
  deriving Repr, DecidableEq, BEq

namespace ProductJoinProfile

def StrictEligible (profile : ProductJoinProfile) : Prop :=
  profile.commonRefinement = true ∧
  profile.factorsThroughDeclaredBaseline = false ∧
  profile.antiProductWitness = true ∧
  profile.strictnessCredit = true

instance (profile : ProductJoinProfile) : Decidable (StrictEligible profile) := by
  unfold StrictEligible
  infer_instance

def MereProduct (profile : ProductJoinProfile) : Prop :=
  profile.commonRefinement = true ∧
  profile.factorsThroughDeclaredBaseline = true ∧
  profile.antiProductWitness = false

end ProductJoinProfile

theorem NGVII_07_no_product_common_refinement_strictness_credit
    (profile : ProductJoinProfile)
    (hProduct : ProductJoinProfile.MereProduct profile) :
    ¬ ProductJoinProfile.StrictEligible profile := by
  intro hStrict
  have hNonfactor : profile.factorsThroughDeclaredBaseline = false := hStrict.2.1
  rw [hProduct.2.1] at hNonfactor
  exact Bool.noConfusion hNonfactor

private def antiProductEscapeProfile : ProductJoinProfile :=
  { commonRefinement := true
    factorsThroughDeclaredBaseline := false
    antiProductWitness := true
    strictnessCredit := true }

theorem NGVII_07_escape_anti_product_witness :
    ProductJoinProfile.StrictEligible antiProductEscapeProfile := by decide

structure LineageJoinCredit where
  sameLineage : Bool
  independentRootsCertified : Bool
  independenceSensitiveCredit : Bool
  deriving Repr, DecidableEq, BEq

namespace LineageJoinCredit

def Eligible (profile : LineageJoinCredit) : Prop :=
  profile.independentRootsCertified = true ∧
  profile.independenceSensitiveCredit = true

instance (profile : LineageJoinCredit) : Decidable (Eligible profile) := by
  unfold Eligible
  infer_instance

def OneLineage (profile : LineageJoinCredit) : Prop :=
  profile.sameLineage = true ∧
  profile.independentRootsCertified = false

end LineageJoinCredit

theorem NGVII_08_no_one_lineage_source_independence_credit
    (profile : LineageJoinCredit)
    (hOne : LineageJoinCredit.OneLineage profile) :
    ¬ LineageJoinCredit.Eligible profile := by
  intro hEligible
  have hIndependent : profile.independentRootsCertified = true := hEligible.1
  rw [hOne.2] at hIndependent
  exact Bool.noConfusion hIndependent

private def independentLineageEscape : LineageJoinCredit :=
  { sameLineage := false
    independentRootsCertified := true
    independenceSensitiveCredit := true }

theorem NGVII_08_escape_disjoint_root_certificate :
    LineageJoinCredit.Eligible independentLineageEscape := by decide

structure PaymentJoinCredit where
  positiveCost : Bool
  paid : Bool
  certifiedZeroCostChannel : Bool
  observerPriced : Bool
  joinCredit : Bool
  deriving Repr, DecidableEq, BEq

namespace PaymentJoinCredit

def Eligible (profile : PaymentJoinCredit) : Prop :=
  profile.joinCredit = true ∧
  profile.observerPriced = true ∧
  ((profile.positiveCost = true ∧ profile.paid = true) ∨
    (profile.positiveCost = false ∧
      profile.certifiedZeroCostChannel = true))

instance (profile : PaymentJoinCredit) : Decidable (Eligible profile) := by
  unfold Eligible
  infer_instance

def PositiveUnpaid (profile : PaymentJoinCredit) : Prop :=
  profile.positiveCost = true ∧
  profile.paid = false ∧
  profile.certifiedZeroCostChannel = false

end PaymentJoinCredit

theorem NGVII_09_no_positive_cost_join_credit_without_payment
    (profile : PaymentJoinCredit)
    (hUnpaid : PaymentJoinCredit.PositiveUnpaid profile) :
    ¬ PaymentJoinCredit.Eligible profile := by
  intro hEligible
  rcases hEligible.2.2 with hPositive | hZero
  · have hPaid : profile.paid = true := hPositive.2
    rw [hUnpaid.2.1] at hPaid
    exact Bool.noConfusion hPaid
  · have hZeroCost : profile.positiveCost = false := hZero.1
    rw [hUnpaid.1] at hZeroCost
    exact Bool.noConfusion hZeroCost

private def paidEscapeProfile : PaymentJoinCredit :=
  { positiveCost := true
    paid := true
    certifiedZeroCostChannel := false
    observerPriced := true
    joinCredit := true }

private def zeroCostEscapeProfile : PaymentJoinCredit :=
  { positiveCost := false
    paid := false
    certifiedZeroCostChannel := true
    observerPriced := true
    joinCredit := true }

theorem NGVII_09_escape_paid_channel :
    PaymentJoinCredit.Eligible paidEscapeProfile := by decide

theorem NGVII_09_escape_certified_zero_cost_channel :
    PaymentJoinCredit.Eligible zeroCostEscapeProfile := by decide

structure SelfBootstrapJoinProfile where
  requiredCapabilityAvailableBefore : Bool
  externalSeed : Bool
  declaredBridge : Bool
  joinExecutes : Bool
  deriving Repr, DecidableEq, BEq

namespace SelfBootstrapJoinProfile

def Lawful (profile : SelfBootstrapJoinProfile) : Prop :=
  profile.joinExecutes = true →
    profile.requiredCapabilityAvailableBefore = true ∨
    profile.externalSeed = true ∨
    profile.declaredBridge = true

instance (profile : SelfBootstrapJoinProfile) : Decidable (Lawful profile) := by
  unfold Lawful
  infer_instance

end SelfBootstrapJoinProfile

private def selfBootstrapProfile : SelfBootstrapJoinProfile :=
  { requiredCapabilityAvailableBefore := false
    externalSeed := false
    declaredBridge := false
    joinExecutes := true }

private def externalSeedJoinProfile : SelfBootstrapJoinProfile :=
  { requiredCapabilityAvailableBefore := false
    externalSeed := true
    declaredBridge := false
    joinExecutes := true }

theorem no_self_bootstrapping_join_without_seed_or_bridge :
    ¬ SelfBootstrapJoinProfile.Lawful selfBootstrapProfile := by decide

theorem self_bootstrap_escape_external_seed :
    SelfBootstrapJoinProfile.Lawful externalSeedJoinProfile := by decide

end FoundationsVII.NoGo
