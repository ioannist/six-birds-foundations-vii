"""E8 control-price sweep against the pre-registered predictions.

The configuration is fixed by
``formalization/notes/sweeps/E8_control_price_predictions.md``.  This module
evaluates deterministic component, field, summary, budget-audit, Xi/Omega, and
E2 tower fixtures with exact ``Fraction`` arithmetic.  Status labels are
computed by the priority-normalized case predicates; they are not copied from
the prediction table.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Callable

from sixbirds_foundations_v.carried_records import FineSourceTag, carried_source
from sixbirds_foundations_v.sweeps.e2_bounded_reflexivity_sweep import (
    LEVELS,
    capacity_admissible,
    capacity_bound_holds,
    capacity_realizable_tower,
    capacity_saturated,
    tower_footprint,
)
from sixbirds_foundations_v.sweeps.e6_e9_probe_shop import (
    allocation_argmax,
    kll_dagger_alloc,
    marginal_ratios,
)
from sixbirds_foundations_v.sweeps.e7_alarm_sweep import blind_spot_excess


F = Fraction

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESULTS_PATH = (
    REPO_ROOT
    / "formalization"
    / "notes"
    / "sweeps"
    / "E8_control_price_results.md"
)

DECLARED_CONSTRAINTS = ("c_cpu", "c_mem", "c_net", "c_io", "c_proxy", "c_aux")

MAIN_COMPARISON_ORDER = (
    "claim_component_cpu_lawful",
    "claim_field_ops_lawful",
    "claim_summary_ops_lawful",
    "claim_summary_slack_obstructed",
    "claim_component_io_slack",
    "claim_component_proxy",
    "claim_summary_redescription",
    "claim_field_incomplete",
)

BUDGET_COMPARISON_ORDER = (
    "claim_shared_discharge",
    "claim_shared_capture",
    "claim_no_capture_rejected",
    "claim_capacity_blocked",
    "claim_missing_meta_audit",
)


class ClaimKind(str, Enum):
    component = "component"
    field = "field"
    summary = "summary"


class ControlPriceStatus(str, Enum):
    slack_obstructed = "slack_obstructed"
    proxy_obstructed = "proxy_obstructed"
    summary_redescription = "summary_redescription"
    component_lawful = "component_lawful"
    field_lawful = "field_lawful"
    summary_lawful = "summary_lawful"
    incomplete_or_unpriced = "incomplete_or_unpriced"
    unclassified = "unclassified"


class BudgetAuditStatus(str, Enum):
    residual_discharge_verified = "residual_discharge_verified"
    capture_detected = "capture_detected"
    capture_claim_rejected = "capture_claim_rejected"
    meta_audit_capacity_blocked = "meta_audit_capacity_blocked"
    meta_audit_missing = "meta_audit_missing"
    unclassified = "unclassified"


@dataclass(frozen=True)
class ControlSignalRecord:
    name: str
    constraint_ref: str
    value: Fraction
    active: bool
    ledger_spend: Fraction
    ledger_budget: Fraction


@dataclass(frozen=True)
class PriceComponentRecord:
    name: str
    constraint_ref: str
    lambda_value: Fraction


@dataclass(frozen=True)
class SlackResidualExplanationRecord:
    name: str
    signal_ref: str
    component_ref: str
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class KKTWitness:
    lambda_value: Fraction
    mu: Fraction = F(0)


@dataclass(frozen=True)
class ControlPriceComponent:
    name: str
    constraint_record: str
    signal_record: ControlSignalRecord
    component_record: PriceComponentRecord
    spend: Fraction
    budget: Fraction
    selected_probe: str
    marginal_discharge: Fraction
    marginal_cost: Fraction
    kkt: KKTWitness
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class ControlPriceFieldRecord:
    name: str
    component_refs: tuple[str, ...]


@dataclass(frozen=True)
class ControlPriceField:
    name: str
    field_record: ControlPriceFieldRecord
    declared_constraints: tuple[str, ...]
    components: tuple[str, ...]
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class CompressedSummaryRecord:
    name: str
    field_ref: str
    value: Fraction
    shadow_component: Fraction
    slack_baseline: Fraction


@dataclass(frozen=True)
class PolicySupportReadoutRecord:
    name: str
    external_observation_key: str
    policy_support: frozenset[str]


@dataclass(frozen=True)
class HeldOutPredictionRecord:
    name: str
    expected_signal: Fraction | None = None
    expected_added_support: frozenset[str] = frozenset()
    hit: bool = True


@dataclass(frozen=True)
class DualStabilityRecord:
    name: str
    max_perturbation: Fraction = F(0)
    lambda_drift: Fraction = F(0)
    max_shadow_drift: Fraction = F(0)
    summary_ref: str | None = None


@dataclass(frozen=True)
class CompressedControlSummary:
    name: str
    summary_record: CompressedSummaryRecord
    field: str
    quotient_key: str
    readout_before: PolicySupportReadoutRecord
    readout_after: PolicySupportReadoutRecord
    prediction: HeldOutPredictionRecord
    stability: DualStabilityRecord
    perturbations: tuple[Fraction, ...]
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class BudgetSettingMoveRecord:
    name: str


@dataclass(frozen=True)
class EndogenousBudgetSettingMove:
    name: str
    move_record: BudgetSettingMoveRecord
    old_budget: Fraction
    new_budget: Fraction
    reported_inflated: bool | None = None
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class OmegaLineageRecord:
    name: str
    budget_move_ref: str
    no_capture_certificate: bool = False


@dataclass(frozen=True)
class BlindSpotAuditRecord:
    name: str
    lineage_ref: str
    hazard: int


@dataclass(frozen=True)
class ReportedLedgerHealthRecord:
    name: str
    lineage_ref: str
    reports_healthy: bool


@dataclass(frozen=True)
class MetaAuditRecord:
    name: str
    budget_move_ref: str
    lineage_ref: str | None


@dataclass(frozen=True)
class ResidualDischargeAudit:
    name: str
    meta_audit_record: str
    budget_move: str
    lineage_record: str
    residual_before: Fraction
    residual_after: Fraction


@dataclass(frozen=True)
class BudgetInflationAudit:
    name: str
    meta_audit_record: str
    budget_move: str
    lineage_record: str
    blind_spot_record: str
    reported_health: str


@dataclass(frozen=True)
class NoCaptureLineageAudit:
    name: str
    budget_move: str
    lineage_record: str
    reported_health: str
    blind_spot_record: str
    claimed_capture_record: str


@dataclass(frozen=True)
class MetaAuditBoundedByE2:
    name: str
    budget_move: str
    lineage_record: str | None
    health_record: str | None
    levels: tuple[object, ...]
    cap: int


@dataclass(frozen=True)
class ControlPriceClaimRef:
    kind: ClaimKind
    record: str


@dataclass(frozen=True)
class BudgetAuditClaimRef:
    budget_move_record: str
    lineage_record: str | None
    health_record: str | None


@dataclass(frozen=True)
class ControlPriceStatusRecord:
    name: str
    claim_kind: ClaimKind
    component_record: str | None
    field_record: str | None
    summary_record: str | None
    status: ControlPriceStatus
    supporting_ledger_entries: tuple[str, ...] = ()
    supporting_audit_records: tuple[str, ...] = ()
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class BudgetAuditStatusRecord:
    name: str
    budget_move_record: str | None
    lineage_record: str | None
    health_record: str | None
    meta_audit_record: str | None
    status: BudgetAuditStatus
    supporting_ledger_entries: tuple[str, ...] = ()
    supporting_audit_records: tuple[str, ...] = ()
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class LedgerAlignmentComparator:
    def aligned(
        self,
        signal: ControlSignalRecord,
        constraint: str,
        spend: Fraction,
        budget: Fraction,
        lambda_value: Fraction,
    ) -> bool:
        return (
            signal.constraint_ref == constraint
            and signal.value == lambda_value
            and signal.ledger_spend == spend
            and signal.ledger_budget == budget
        )


@dataclass(frozen=True)
class HeldOutPredictionComparator:
    def predicts(self, signal: ControlSignalRecord, prediction: HeldOutPredictionRecord) -> bool:
        return prediction.expected_signal == signal.value and prediction.hit is True


@dataclass(frozen=True)
class DualStabilityComparator:
    def stable(self, signal: ControlSignalRecord, stability: DualStabilityRecord) -> bool:
        return stability.max_perturbation <= F(1, 10) and stability.lambda_drift <= F(1, 20)


@dataclass(frozen=True)
class SummaryLegitimacyComparators:
    def same_external_observation(
        self,
        quotient_key: str,
        before: PolicySupportReadoutRecord,
        after: PolicySupportReadoutRecord,
    ) -> bool:
        return before.external_observation_key == quotient_key and after.external_observation_key == quotient_key

    def summary_separates(
        self,
        summary: CompressedSummaryRecord,
        before: PolicySupportReadoutRecord,
        after: PolicySupportReadoutRecord,
    ) -> bool:
        return summary.value != 0 and before.policy_support != after.policy_support

    def policy_support_changes(
        self,
        before: PolicySupportReadoutRecord,
        after: PolicySupportReadoutRecord,
    ) -> bool:
        return before.policy_support != after.policy_support

    def held_out_predicts(
        self,
        prediction: HeldOutPredictionRecord,
        before: PolicySupportReadoutRecord,
        after: PolicySupportReadoutRecord,
    ) -> bool:
        return (
            prediction.expected_added_support == after.policy_support - before.policy_support
            and prediction.hit is True
        )

    def dual_stable_held_out(
        self,
        stability: DualStabilityRecord,
        summary: CompressedSummaryRecord,
        perturbations: tuple[Fraction, ...],
    ) -> bool:
        return (
            bool(perturbations)
            and all(abs(item) <= F(1, 10) for item in perturbations)
            and stability.max_shadow_drift <= F(1, 20)
            and stability.summary_ref == summary.name
        )


@dataclass(frozen=True)
class LedgerLineageAgreementComparator:
    def agrees(self, health: ReportedLedgerHealthRecord, lineage: OmegaLineageRecord) -> bool:
        return (
            health.lineage_ref == lineage.name
            and health.reports_healthy is True
            and lineage.no_capture_certificate is True
        )


@dataclass(frozen=True)
class MainStatusRow:
    claim: str
    claim_ref: ControlPriceClaimRef
    record: str
    slack_obstructed: bool
    proxy_obstructed: bool
    summary_redescription: bool
    component_lawful: bool
    field_lawful: bool
    summary_lawful: bool
    incomplete_or_unpriced: bool
    status: str


@dataclass(frozen=True)
class BudgetStatusRow:
    claim: str
    claim_ref: BudgetAuditClaimRef
    record: str
    capture_claim_rejected: bool
    capture_detected: bool
    residual_discharge_verified: bool
    meta_audit_capacity_blocked: bool
    meta_audit_missing: bool
    status: str


@dataclass(frozen=True)
class ControlRow:
    name: str
    passed_control: bool
    observed: str
    expected: str


@dataclass(frozen=True)
class Comparison:
    name: str
    passed: bool
    observed: str
    expected: str


@dataclass(frozen=True)
class SweepResults:
    main_rows: tuple[MainStatusRow, ...]
    budget_rows: tuple[BudgetStatusRow, ...]
    controls: tuple[ControlRow, ...]
    actual_scope_discipline: bool
    no_hardcoded_status_discipline: bool
    comparisons: tuple[Comparison, ...]


@dataclass(frozen=True)
class Fixture:
    components: dict[str, ControlPriceComponent]
    proxy_prediction_records: dict[str, HeldOutPredictionRecord]
    proxy_stability_records: dict[str, DualStabilityRecord]
    slack_residual_explanations: dict[str, SlackResidualExplanationRecord]
    fields: dict[str, ControlPriceField]
    summaries: dict[str, CompressedControlSummary]
    control_claims: dict[str, ControlPriceClaimRef]
    control_status_records: dict[str, ControlPriceStatusRecord]
    budget_moves: dict[str, EndogenousBudgetSettingMove]
    lineages: dict[str, OmegaLineageRecord]
    blind_spot_audits: dict[str, BlindSpotAuditRecord]
    health_records: dict[str, ReportedLedgerHealthRecord]
    meta_audit_records: dict[str, MetaAuditRecord]
    residual_audits: dict[str, ResidualDischargeAudit]
    budget_inflation_audits: dict[str, BudgetInflationAudit]
    no_capture_audits: dict[str, NoCaptureLineageAudit]
    e2_bounds: dict[str, MetaAuditBoundedByE2]
    budget_claims: dict[str, BudgetAuditClaimRef]
    budget_status_records: dict[str, BudgetAuditStatusRecord]
    ledger_entries: frozenset[str]
    audit_records: frozenset[str]
    carried_control_status_records: frozenset[str]
    carried_budget_status_records: frozenset[str]
    ledger_comparator: LedgerAlignmentComparator
    prediction_comparator: HeldOutPredictionComparator
    stability_comparator: DualStabilityComparator
    summary_comparators: SummaryLegitimacyComparators
    lineage_agreement_comparator: LedgerLineageAgreementComparator
    e6_allocation_weight: tuple[Fraction, Fraction]
    e6_allocation_ratios: tuple[Fraction, Fraction]


def _ratio(discharge: Fraction, cost: Fraction) -> Fraction:
    if cost == 0:
        raise ValueError("marginal cost must be positive")
    return discharge / cost


def _component(
    name: str,
    constraint: str,
    spend: Fraction,
    budget: Fraction,
    lambda_value: Fraction,
    signal_value: Fraction,
    signal_active: bool,
    selected_probe: str,
    marginal_discharge: Fraction,
    marginal_cost: Fraction,
) -> ControlPriceComponent:
    computed_lambda = _ratio(marginal_discharge, marginal_cost) if spend == budget else F(0)
    return ControlPriceComponent(
        name=name,
        constraint_record=constraint,
        signal_record=ControlSignalRecord(
            name=f"signal_{name}",
            constraint_ref=constraint,
            value=signal_value,
            active=signal_active,
            ledger_spend=spend,
            ledger_budget=budget,
        ),
        component_record=PriceComponentRecord(
            name=f"{name}.componentRecord",
            constraint_ref=constraint,
            lambda_value=lambda_value,
        ),
        spend=spend,
        budget=budget,
        selected_probe=selected_probe,
        marginal_discharge=marginal_discharge,
        marginal_cost=marginal_cost,
        kkt=KKTWitness(computed_lambda),
    )


def build_fixture() -> Fixture:
    allocation = allocation_argmax(F(1))
    _ = kll_dagger_alloc(allocation.weight)
    e6_ratios = marginal_ratios(allocation.weight)

    components = {
        "cmp_cpu_bind": _component("cmp_cpu_bind", "c_cpu", F(1), F(1), F(3, 2), F(3, 2), True, "probe_cpu", F(3), F(2)),
        "cmp_mem_bind": _component("cmp_mem_bind", "c_mem", F(1), F(1), F(1), F(1), True, "probe_mem", F(1), F(1)),
        "cmp_net_slack_zero": _component("cmp_net_slack_zero", "c_net", F(1, 2), F(1), F(0), F(0), False, "probe_net", F(0), F(1)),
        "cmp_aux_slack_zero": _component("cmp_aux_slack_zero", "c_aux", F(1, 4), F(1), F(0), F(0), False, "probe_aux", F(0), F(1)),
        "cmp_io_slack_violation": _component("cmp_io_slack_violation", "c_io", F(1, 2), F(1), F(0), F(1, 4), True, "probe_io", F(0), F(1)),
        "cmp_proxy_bind": _component("cmp_proxy_bind", "c_proxy", F(1), F(1), F(4, 5), F(9, 10), True, "probe_proxy", F(4), F(5)),
        "cmp_unrelated_slack_violation": _component("cmp_unrelated_slack_violation", "c_aux", F(1, 3), F(1), F(0), F(1, 3), True, "probe_aux_unrelated", F(0), F(1)),
    }
    proxy_prediction_records = {
        name: HeldOutPredictionRecord(
            f"prediction_{name}",
            expected_signal=component.signal_record.value,
            hit=(name != "cmp_proxy_bind"),
        )
        for name, component in components.items()
    }
    proxy_stability_records = {
        name: DualStabilityRecord(
            f"stability_{name}",
            max_perturbation=F(1, 10),
            lambda_drift=F(1, 5) if name == "cmp_proxy_bind" else F(0),
        )
        for name in components
    }

    fields = {
        "field_ops_lawful": ControlPriceField(
            "field_ops_lawful",
            ControlPriceFieldRecord(
                "field_ops_lawful.fieldRecord",
                (
                    components["cmp_cpu_bind"].component_record.name,
                    components["cmp_mem_bind"].component_record.name,
                    components["cmp_net_slack_zero"].component_record.name,
                ),
            ),
            ("c_cpu", "c_mem", "c_net"),
            ("cmp_cpu_bind", "cmp_mem_bind", "cmp_net_slack_zero"),
        ),
        "field_member_slack": ControlPriceField(
            "field_member_slack",
            ControlPriceFieldRecord(
                "field_member_slack.fieldRecord",
                (
                    components["cmp_cpu_bind"].component_record.name,
                    components["cmp_io_slack_violation"].component_record.name,
                ),
            ),
            ("c_cpu", "c_io"),
            ("cmp_cpu_bind", "cmp_io_slack_violation"),
        ),
        "field_unrelated_clean": ControlPriceField(
            "field_unrelated_clean",
            ControlPriceFieldRecord(
                "field_unrelated_clean.fieldRecord",
                (
                    components["cmp_cpu_bind"].component_record.name,
                    components["cmp_mem_bind"].component_record.name,
                ),
            ),
            ("c_cpu", "c_mem"),
            ("cmp_cpu_bind", "cmp_mem_bind"),
        ),
        "field_summary_slack": ControlPriceField(
            "field_summary_slack",
            ControlPriceFieldRecord(
                "field_summary_slack.fieldRecord",
                (
                    components["cmp_net_slack_zero"].component_record.name,
                    components["cmp_aux_slack_zero"].component_record.name,
                ),
            ),
            ("c_net", "c_aux"),
            ("cmp_net_slack_zero", "cmp_aux_slack_zero"),
        ),
        "field_incomplete": ControlPriceField(
            "field_incomplete",
            ControlPriceFieldRecord(
                "field_incomplete.fieldRecord",
                (components["cmp_cpu_bind"].component_record.name,),
            ),
            ("c_cpu", "c_mem", "c_net"),
            ("cmp_cpu_bind",),
        ),
    }

    before = PolicySupportReadoutRecord("readout_before_basic", "obs_low", frozenset({"basic"}))
    after_burst = PolicySupportReadoutRecord(
        "readout_after_burst", "obs_low", frozenset({"basic", "burst"})
    )
    after_same = PolicySupportReadoutRecord("readout_after_same", "obs_low", frozenset({"basic"}))
    prediction_hit = HeldOutPredictionRecord(
        "prediction_hit_burst", expected_added_support=frozenset({"burst"}), hit=True
    )
    prediction_miss = HeldOutPredictionRecord(
        "prediction_miss_burst", expected_added_support=frozenset({"burst"}), hit=False
    )
    stable = DualStabilityRecord(
        "stable_summary", max_shadow_drift=F(1, 40), summary_ref="summary_ops_lawful.summaryRecord"
    )
    stable_slack_obstructed = DualStabilityRecord(
        "stable_summary_slack", max_shadow_drift=F(1, 40), summary_ref="summary_slack_obstructed.summaryRecord"
    )
    unstable = DualStabilityRecord(
        "unstable_summary", max_shadow_drift=F(1, 8), summary_ref="summary_redescription.summaryRecord"
    )

    summaries = {
        "summary_ops_lawful": CompressedControlSummary(
            "summary_ops_lawful",
            CompressedSummaryRecord("summary_ops_lawful.summaryRecord", fields["field_summary_slack"].field_record.name, F(1, 2), F(0), F(0)),
            "field_summary_slack",
            "obs_low",
            before,
            after_burst,
            prediction_hit,
            stable,
            (F(-1, 10), F(1, 10)),
        ),
        "summary_slack_obstructed": CompressedControlSummary(
            "summary_slack_obstructed",
            CompressedSummaryRecord("summary_slack_obstructed.summaryRecord", fields["field_summary_slack"].field_record.name, F(1, 2), F(1, 8), F(0)),
            "field_summary_slack",
            "obs_low",
            before,
            after_burst,
            prediction_hit,
            stable_slack_obstructed,
            (F(-1, 10), F(1, 10)),
        ),
        "summary_redescription": CompressedControlSummary(
            "summary_redescription",
            CompressedSummaryRecord("summary_redescription.summaryRecord", fields["field_summary_slack"].field_record.name, F(1, 2), F(0), F(0)),
            "field_summary_slack",
            "obs_low",
            before,
            after_same,
            prediction_miss,
            unstable,
            (F(-1, 10), F(1, 10)),
        ),
    }

    control_claims = {
        "claim_component_cpu_lawful": ControlPriceClaimRef(ClaimKind.component, components["cmp_cpu_bind"].component_record.name),
        "claim_field_ops_lawful": ControlPriceClaimRef(ClaimKind.field, fields["field_ops_lawful"].field_record.name),
        "claim_summary_ops_lawful": ControlPriceClaimRef(ClaimKind.summary, summaries["summary_ops_lawful"].summary_record.name),
        "claim_summary_slack_obstructed": ControlPriceClaimRef(ClaimKind.summary, summaries["summary_slack_obstructed"].summary_record.name),
        "claim_component_io_slack": ControlPriceClaimRef(ClaimKind.component, components["cmp_io_slack_violation"].component_record.name),
        "claim_component_proxy": ControlPriceClaimRef(ClaimKind.component, components["cmp_proxy_bind"].component_record.name),
        "claim_summary_redescription": ControlPriceClaimRef(ClaimKind.summary, summaries["summary_redescription"].summary_record.name),
        "claim_field_incomplete": ControlPriceClaimRef(ClaimKind.field, fields["field_incomplete"].field_record.name),
        "ctrl_field_member_slack_obstruction": ControlPriceClaimRef(ClaimKind.field, fields["field_member_slack"].field_record.name),
        "ctrl_unrelated_component_not_obstructing_field": ControlPriceClaimRef(ClaimKind.field, fields["field_unrelated_clean"].field_record.name),
        "ctrl_summary_comparators_nontrivial": ControlPriceClaimRef(ClaimKind.summary, summaries["summary_redescription"].summary_record.name),
    }

    control_status_records = {
        "status_component_cpu_lawful": ControlPriceStatusRecord(
            "status_component_cpu_lawful", ClaimKind.component, components["cmp_cpu_bind"].component_record.name, None, None, ControlPriceStatus.component_lawful
        ),
        "status_field_ops_lawful": ControlPriceStatusRecord(
            "status_field_ops_lawful", ClaimKind.field, None, fields["field_ops_lawful"].field_record.name, None, ControlPriceStatus.field_lawful
        ),
        "status_summary_ops_lawful": ControlPriceStatusRecord(
            "status_summary_ops_lawful", ClaimKind.summary, None, None, summaries["summary_ops_lawful"].summary_record.name, ControlPriceStatus.summary_lawful
        ),
        "status_summary_slack_obstructed": ControlPriceStatusRecord(
            "status_summary_slack_obstructed", ClaimKind.summary, None, None, summaries["summary_slack_obstructed"].summary_record.name, ControlPriceStatus.slack_obstructed
        ),
        "status_component_io_slack": ControlPriceStatusRecord(
            "status_component_io_slack", ClaimKind.component, components["cmp_io_slack_violation"].component_record.name, None, None, ControlPriceStatus.slack_obstructed
        ),
        "status_component_proxy": ControlPriceStatusRecord(
            "status_component_proxy", ClaimKind.component, components["cmp_proxy_bind"].component_record.name, None, None, ControlPriceStatus.proxy_obstructed
        ),
        "status_summary_redescription": ControlPriceStatusRecord(
            "status_summary_redescription", ClaimKind.summary, None, None, summaries["summary_redescription"].summary_record.name, ControlPriceStatus.summary_redescription
        ),
        "status_field_incomplete": ControlPriceStatusRecord(
            "status_field_incomplete", ClaimKind.field, None, fields["field_incomplete"].field_record.name, None, ControlPriceStatus.incomplete_or_unpriced
        ),
        "status_field_member_slack": ControlPriceStatusRecord(
            "status_field_member_slack", ClaimKind.field, None, fields["field_member_slack"].field_record.name, None, ControlPriceStatus.slack_obstructed
        ),
        "status_field_unrelated_clean": ControlPriceStatusRecord(
            "status_field_unrelated_clean", ClaimKind.field, None, fields["field_unrelated_clean"].field_record.name, None, ControlPriceStatus.field_lawful
        ),
    }

    budget_moves = {
        "bm_shared": EndogenousBudgetSettingMove("bm_shared", BudgetSettingMoveRecord("bm_shared"), F(10), F(15)),
        "bm_no_capture": EndogenousBudgetSettingMove("bm_no_capture", BudgetSettingMoveRecord("bm_no_capture"), F(10), F(12)),
        "bm_capacity": EndogenousBudgetSettingMove("bm_capacity", BudgetSettingMoveRecord("bm_capacity"), F(8), F(8)),
        "bm_missing": EndogenousBudgetSettingMove("bm_missing", BudgetSettingMoveRecord("bm_missing"), F(5), F(5)),
        "bm_inflation_no_blind": EndogenousBudgetSettingMove("bm_inflation_no_blind", BudgetSettingMoveRecord("bm_inflation_no_blind"), F(10), F(20)),
        "bm_wrong_lineage": EndogenousBudgetSettingMove("bm_wrong_lineage", BudgetSettingMoveRecord("bm_wrong_lineage"), F(10), F(14)),
        "bm_equal_budget_metadata_inflated": EndogenousBudgetSettingMove(
            "bm_equal_budget_metadata_inflated",
            BudgetSettingMoveRecord("bm_equal_budget_metadata_inflated"),
            F(12),
            F(12),
            reported_inflated=True,
        ),
    }

    lineages = {
        "lineage_shared_A": OmegaLineageRecord("lineage_shared_A", "bm_shared"),
        "lineage_shared_B": OmegaLineageRecord("lineage_shared_B", "bm_shared"),
        "lineage_no_capture": OmegaLineageRecord("lineage_no_capture", "bm_no_capture", no_capture_certificate=True),
        "lineage_no_blind": OmegaLineageRecord("lineage_no_blind", "bm_inflation_no_blind"),
        "lineage_claim_actual": OmegaLineageRecord("lineage_claim_actual", "bm_wrong_lineage"),
        "lineage_wrong_source": OmegaLineageRecord("lineage_wrong_source", "bm_wrong_lineage"),
        "lineage_flag_blind": OmegaLineageRecord("lineage_flag_blind", "bm_equal_budget_metadata_inflated"),
    }
    blind_spot_audits = {
        "blind_shared_B": BlindSpotAuditRecord("blind_shared_B", "lineage_shared_B", 1),
        "blind_no_capture": BlindSpotAuditRecord("blind_no_capture", "lineage_no_capture", 0),
        "blind_wrong_source": BlindSpotAuditRecord("blind_wrong_source", "lineage_wrong_source", 1),
        "blind_flag": BlindSpotAuditRecord("blind_flag", "lineage_flag_blind", 1),
    }
    health_records = {
        "health_shared_B": ReportedLedgerHealthRecord("health_shared_B", "lineage_shared_B", True),
        "health_no_capture": ReportedLedgerHealthRecord("health_no_capture", "lineage_no_capture", True),
        "health_wrong_lineage": ReportedLedgerHealthRecord("health_wrong_lineage", "lineage_claim_actual", True),
        "health_flag_blind": ReportedLedgerHealthRecord("health_flag_blind", "lineage_flag_blind", True),
    }
    meta_audit_records = {
        "meta_shared_discharge": MetaAuditRecord("meta_shared_discharge", "bm_shared", "lineage_shared_A"),
        "meta_shared_capture": MetaAuditRecord("meta_shared_capture", "bm_shared", "lineage_shared_B"),
        "meta_no_capture": MetaAuditRecord("meta_no_capture", "bm_no_capture", "lineage_no_capture"),
        "meta_capacity": MetaAuditRecord("meta_capacity", "bm_capacity", None),
        "meta_inflation_no_blind": MetaAuditRecord("meta_inflation_no_blind", "bm_inflation_no_blind", "lineage_no_blind"),
        "meta_wrong_lineage": MetaAuditRecord("meta_wrong_lineage", "bm_wrong_lineage", "lineage_claim_actual"),
        "meta_flag_blind": MetaAuditRecord("meta_flag_blind", "bm_equal_budget_metadata_inflated", "lineage_flag_blind"),
    }
    residual_audits = {
        "residual_shared": ResidualDischargeAudit("residual_shared", "meta_shared_discharge", "bm_shared", "lineage_shared_A", F(5), F(2)),
        "residual_inflation_no_blind": ResidualDischargeAudit("residual_inflation_no_blind", "meta_inflation_no_blind", "bm_inflation_no_blind", "lineage_no_blind", F(9), F(4)),
    }
    budget_inflation_audits = {
        "inflation_shared_capture": BudgetInflationAudit("inflation_shared_capture", "meta_shared_capture", "bm_shared", "lineage_shared_B", "blind_shared_B", "health_shared_B"),
        "inflation_wrong_lineage": BudgetInflationAudit("inflation_wrong_lineage", "meta_wrong_lineage", "bm_wrong_lineage", "lineage_wrong_source", "blind_wrong_source", "health_wrong_lineage"),
        "inflation_flag_blind": BudgetInflationAudit("inflation_flag_blind", "meta_flag_blind", "bm_equal_budget_metadata_inflated", "lineage_flag_blind", "blind_flag", "health_flag_blind"),
    }
    no_capture_audits = {
        "no_capture": NoCaptureLineageAudit(
            "no_capture",
            "bm_no_capture",
            "lineage_no_capture",
            "health_no_capture",
            "blind_no_capture",
            "meta_no_capture",
        )
    }
    e2_levels = (LEVELS[0], LEVELS[1], LEVELS[2])
    e2_bounds = {
        "capacity_bound": MetaAuditBoundedByE2("capacity_bound", "bm_capacity", None, None, e2_levels, 8)
    }
    budget_claims = {
        "claim_shared_discharge": BudgetAuditClaimRef("bm_shared", "lineage_shared_A", None),
        "claim_shared_capture": BudgetAuditClaimRef("bm_shared", "lineage_shared_B", "health_shared_B"),
        "claim_no_capture_rejected": BudgetAuditClaimRef("bm_no_capture", "lineage_no_capture", "health_no_capture"),
        "claim_capacity_blocked": BudgetAuditClaimRef("bm_capacity", None, None),
        "claim_missing_meta_audit": BudgetAuditClaimRef("bm_missing", None, None),
        "claim_inflation_no_blind": BudgetAuditClaimRef("bm_inflation_no_blind", "lineage_no_blind", None),
        "ctrl_wrong_lineage_capture_claim": BudgetAuditClaimRef("bm_wrong_lineage", "lineage_claim_actual", "health_wrong_lineage"),
        "ctrl_disconnected_budget_inflation_flag": BudgetAuditClaimRef("bm_equal_budget_metadata_inflated", "lineage_flag_blind", "health_flag_blind"),
    }
    budget_status_records = {
        "status_shared_discharge": BudgetAuditStatusRecord("status_shared_discharge", "bm_shared", "lineage_shared_A", None, "meta_shared_discharge", BudgetAuditStatus.residual_discharge_verified),
        "status_shared_capture": BudgetAuditStatusRecord("status_shared_capture", "bm_shared", "lineage_shared_B", "health_shared_B", "meta_shared_capture", BudgetAuditStatus.capture_detected),
        "status_no_capture_rejected": BudgetAuditStatusRecord("status_no_capture_rejected", "bm_no_capture", "lineage_no_capture", "health_no_capture", "meta_no_capture", BudgetAuditStatus.capture_claim_rejected),
        "status_capacity_blocked": BudgetAuditStatusRecord("status_capacity_blocked", "bm_capacity", None, None, "meta_capacity", BudgetAuditStatus.meta_audit_capacity_blocked),
        "status_missing_meta_audit": BudgetAuditStatusRecord("status_missing_meta_audit", "bm_missing", None, None, None, BudgetAuditStatus.meta_audit_missing),
        "status_inflation_no_blind": BudgetAuditStatusRecord("status_inflation_no_blind", "bm_inflation_no_blind", "lineage_no_blind", None, "meta_inflation_no_blind", BudgetAuditStatus.residual_discharge_verified),
        "status_wrong_lineage_capture": BudgetAuditStatusRecord("status_wrong_lineage_capture", "bm_wrong_lineage", "lineage_claim_actual", "health_wrong_lineage", "meta_wrong_lineage", BudgetAuditStatus.meta_audit_missing),
        "status_disconnected_budget_flag": BudgetAuditStatusRecord("status_disconnected_budget_flag", "bm_equal_budget_metadata_inflated", "lineage_flag_blind", "health_flag_blind", "meta_flag_blind", BudgetAuditStatus.meta_audit_missing),
    }

    return Fixture(
        components=components,
        proxy_prediction_records=proxy_prediction_records,
        proxy_stability_records=proxy_stability_records,
        slack_residual_explanations={},
        fields=fields,
        summaries=summaries,
        control_claims=control_claims,
        control_status_records=control_status_records,
        budget_moves=budget_moves,
        lineages=lineages,
        blind_spot_audits=blind_spot_audits,
        health_records=health_records,
        meta_audit_records=meta_audit_records,
        residual_audits=residual_audits,
        budget_inflation_audits=budget_inflation_audits,
        no_capture_audits=no_capture_audits,
        e2_bounds=e2_bounds,
        budget_claims=budget_claims,
        budget_status_records=budget_status_records,
        ledger_entries=frozenset({"ledger"}),
        audit_records=frozenset({"audit"}),
        carried_control_status_records=frozenset(record.name for record in control_status_records.values()),
        carried_budget_status_records=frozenset(record.name for record in budget_status_records.values()),
        ledger_comparator=LedgerAlignmentComparator(),
        prediction_comparator=HeldOutPredictionComparator(),
        stability_comparator=DualStabilityComparator(),
        summary_comparators=SummaryLegitimacyComparators(),
        lineage_agreement_comparator=LedgerLineageAgreementComparator(),
        e6_allocation_weight=allocation.weight,
        e6_allocation_ratios=e6_ratios,
    )


def binding_exposure_budget(component: ControlPriceComponent) -> bool:
    return component.spend == component.budget


def slack_exposure_budget(component: ControlPriceComponent) -> bool:
    return component.spend < component.budget


def genuine_scarcity(component: ControlPriceComponent) -> bool:
    return component.selected_probe != "" and component.marginal_discharge > 0 and component.marginal_cost > 0


def binding_control_component(component: ControlPriceComponent) -> bool:
    return binding_exposure_budget(component) and genuine_scarcity(component)


def slack_control_component(component: ControlPriceComponent) -> bool:
    return slack_exposure_budget(component)


def component_slack_collapse(component: ControlPriceComponent) -> bool:
    return (not slack_control_component(component)) or component.component_record.lambda_value == 0


def shadow_price_component_identified(component: ControlPriceComponent) -> bool:
    return component.component_record.lambda_value == component.kkt.lambda_value and component_slack_collapse(component)


def slack_collapse_violation(fixture: Fixture, component_name: str) -> bool:
    component = fixture.components[component_name]
    residual_explanation_exists = any(
        explanation.signal_ref == component.signal_record.name
        and explanation.component_ref == component.component_record.name
        and carried_source(
            explanation.source_tag,
            explanation.generated_by_s,
            explanation.in_scope,
        )
        for explanation in fixture.slack_residual_explanations.values()
    )
    return (
        slack_control_component(component)
        and (component.signal_record.value != 0 or component.signal_record.active is True)
        and not residual_explanation_exists
        and carried_source(component.source_tag, component.generated_by_s, component.in_scope)
    )


def proxy_failure(fixture: Fixture, component_name: str) -> bool:
    component = fixture.components[component_name]
    prediction = fixture.proxy_prediction_records.get(component_name)
    stability = fixture.proxy_stability_records.get(component_name)
    if prediction is None or stability is None:
        return False
    aligned = fixture.ledger_comparator.aligned(
        component.signal_record,
        component.constraint_record,
        component.spend,
        component.budget,
        component.component_record.lambda_value,
    )
    predicts = fixture.prediction_comparator.predicts(component.signal_record, prediction)
    stable = fixture.stability_comparator.stable(component.signal_record, stability)
    return not aligned and not predicts and not stable


def component_shadow_price_lawful(fixture: Fixture, component_name: str) -> bool:
    return (
        shadow_price_component_identified(fixture.components[component_name])
        and not slack_collapse_violation(fixture, component_name)
        and not proxy_failure(fixture, component_name)
    )


def field_complete_for_declared_constraints(fixture: Fixture, field_name: str) -> bool:
    field = fixture.fields[field_name]
    return all(
        any(fixture.components[name].constraint_record == constraint for name in field.components)
        for constraint in field.declared_constraints
    )


def control_claim_contains_component(
    fixture: Fixture,
    claim_ref: ControlPriceClaimRef,
    component_name: str,
) -> bool:
    component = fixture.components[component_name]
    if claim_ref.kind is ClaimKind.component:
        return claim_ref.record == component.component_record.name
    if claim_ref.kind is ClaimKind.field:
        field = next((field for field in fixture.fields.values() if field.field_record.name == claim_ref.record), None)
        return field is not None and component_name in field.components
    if claim_ref.kind is ClaimKind.summary:
        summary = next((summary for summary in fixture.summaries.values() if summary.summary_record.name == claim_ref.record), None)
        return summary is not None and component_name in fixture.fields[summary.field].components
    return False


def summary_predictive_legitimacy(fixture: Fixture, summary_name: str) -> bool:
    summary = fixture.summaries[summary_name]
    comparators = fixture.summary_comparators
    return (
        carried_source(summary.source_tag, summary.generated_by_s, summary.in_scope)
        and bool(summary.perturbations)
        and comparators.same_external_observation(summary.quotient_key, summary.readout_before, summary.readout_after)
        and comparators.summary_separates(summary.summary_record, summary.readout_before, summary.readout_after)
        and comparators.policy_support_changes(summary.readout_before, summary.readout_after)
        and comparators.held_out_predicts(summary.prediction, summary.readout_before, summary.readout_after)
        and comparators.dual_stable_held_out(summary.stability, summary.summary_record, summary.perturbations)
    )


def summary_slack_collapse(fixture: Fixture, summary_name: str) -> bool:
    summary = fixture.summaries[summary_name]
    field = fixture.fields[summary.field]
    if all(slack_control_component(fixture.components[name]) for name in field.components):
        return summary.summary_record.shadow_component == summary.summary_record.slack_baseline
    return True


def summary_lawful(fixture: Fixture, summary_name: str) -> bool:
    return summary_predictive_legitimacy(fixture, summary_name) and summary_slack_collapse(fixture, summary_name)


def control_status_record_matches_claim(record: ControlPriceStatusRecord, claim_ref: ControlPriceClaimRef) -> bool:
    if claim_ref.kind is ClaimKind.component:
        return (
            record.claim_kind is ClaimKind.component
            and record.component_record == claim_ref.record
            and record.field_record is None
            and record.summary_record is None
        )
    if claim_ref.kind is ClaimKind.field:
        return (
            record.claim_kind is ClaimKind.field
            and record.component_record is None
            and record.field_record == claim_ref.record
            and record.summary_record is None
        )
    return (
        record.claim_kind is ClaimKind.summary
        and record.component_record is None
        and record.field_record is None
        and record.summary_record == claim_ref.record
    )


def control_price_status_occurrence_for(
    fixture: Fixture,
    claim_ref: ControlPriceClaimRef,
    record: ControlPriceStatusRecord,
) -> bool:
    return (
        control_status_record_matches_claim(record, claim_ref)
        and record.name in fixture.carried_control_status_records
        and carried_source(record.source_tag, record.generated_by_s, record.in_scope)
        and all(entry in fixture.ledger_entries for entry in record.supporting_ledger_entries)
        and all(audit in fixture.audit_records for audit in record.supporting_audit_records)
    )


def _summary_for_claim(fixture: Fixture, claim_ref: ControlPriceClaimRef) -> str | None:
    if claim_ref.kind is not ClaimKind.summary:
        return None
    for name, summary in fixture.summaries.items():
        if summary.summary_record.name == claim_ref.record:
            return name
    return None


def _component_for_claim(fixture: Fixture, claim_ref: ControlPriceClaimRef) -> str | None:
    if claim_ref.kind is not ClaimKind.component:
        return None
    return next(
        (name for name, component in fixture.components.items() if component.component_record.name == claim_ref.record),
        None,
    )


def _field_for_claim(fixture: Fixture, claim_ref: ControlPriceClaimRef) -> str | None:
    if claim_ref.kind is not ClaimKind.field:
        return None
    return next((name for name, field in fixture.fields.items() if field.field_record.name == claim_ref.record), None)


def _slack_obstruction_evidence(fixture: Fixture, claim_ref: ControlPriceClaimRef) -> bool:
    component_path = any(
        slack_collapse_violation(fixture, name)
        and control_claim_contains_component(fixture, claim_ref, name)
        for name in fixture.components
    )
    summary_name = _summary_for_claim(fixture, claim_ref)
    summary_path = (
        summary_name is not None
        and summary_predictive_legitimacy(fixture, summary_name)
        and not summary_slack_collapse(fixture, summary_name)
    )
    return component_path or summary_path


def _proxy_obstruction_evidence(fixture: Fixture, claim_ref: ControlPriceClaimRef) -> bool:
    return any(
        proxy_failure(fixture, name)
        and control_claim_contains_component(fixture, claim_ref, name)
        for name in fixture.components
    )


def _summary_redescription_evidence(fixture: Fixture, claim_ref: ControlPriceClaimRef) -> bool:
    summary_name = _summary_for_claim(fixture, claim_ref)
    return summary_name is not None and not summary_predictive_legitimacy(fixture, summary_name)


def _component_lawful_evidence(fixture: Fixture, claim_ref: ControlPriceClaimRef) -> bool:
    component_name = _component_for_claim(fixture, claim_ref)
    return component_name is not None and component_shadow_price_lawful(fixture, component_name)


def _field_lawful_evidence(fixture: Fixture, claim_ref: ControlPriceClaimRef) -> bool:
    field_name = _field_for_claim(fixture, claim_ref)
    return (
        field_name is not None
        and field_complete_for_declared_constraints(fixture, field_name)
        and all(component_shadow_price_lawful(fixture, name) for name in fixture.fields[field_name].components)
    )


def _summary_lawful_evidence(fixture: Fixture, claim_ref: ControlPriceClaimRef) -> bool:
    summary_name = _summary_for_claim(fixture, claim_ref)
    return summary_name is not None and summary_lawful(fixture, summary_name)


def _exists_main_status_record(
    fixture: Fixture,
    claim_ref: ControlPriceClaimRef,
    status: ControlPriceStatus,
    evidence: Callable[[Fixture, ControlPriceClaimRef], bool],
) -> bool:
    return any(
        control_price_status_occurrence_for(fixture, claim_ref, record)
        and record.status is status
        and evidence(fixture, claim_ref)
        for record in fixture.control_status_records.values()
    )


def slack_obstructed_case(fixture: Fixture, claim_ref: ControlPriceClaimRef, record: ControlPriceStatusRecord) -> bool:
    return (
        control_price_status_occurrence_for(fixture, claim_ref, record)
        and _slack_obstruction_evidence(fixture, claim_ref)
        and record.status is ControlPriceStatus.slack_obstructed
    )


def proxy_obstructed_case(fixture: Fixture, claim_ref: ControlPriceClaimRef, record: ControlPriceStatusRecord) -> bool:
    higher = _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.slack_obstructed,
        _slack_obstruction_evidence,
    )
    return (
        not higher
        and control_price_status_occurrence_for(fixture, claim_ref, record)
        and _proxy_obstruction_evidence(fixture, claim_ref)
        and record.status is ControlPriceStatus.proxy_obstructed
    )


def summary_redescription_case(fixture: Fixture, claim_ref: ControlPriceClaimRef, record: ControlPriceStatusRecord) -> bool:
    higher = _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.slack_obstructed,
        _slack_obstruction_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.proxy_obstructed,
        _proxy_obstruction_evidence,
    )
    return (
        not higher
        and control_price_status_occurrence_for(fixture, claim_ref, record)
        and _summary_redescription_evidence(fixture, claim_ref)
        and record.status is ControlPriceStatus.summary_redescription
    )


def component_lawful_case(fixture: Fixture, claim_ref: ControlPriceClaimRef, record: ControlPriceStatusRecord) -> bool:
    higher = _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.slack_obstructed,
        _slack_obstruction_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.proxy_obstructed,
        _proxy_obstruction_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.summary_redescription,
        _summary_redescription_evidence,
    )
    return (
        not higher
        and control_price_status_occurrence_for(fixture, claim_ref, record)
        and claim_ref.kind is ClaimKind.component
        and _component_lawful_evidence(fixture, claim_ref)
        and record.status is ControlPriceStatus.component_lawful
    )


def field_lawful_case(fixture: Fixture, claim_ref: ControlPriceClaimRef, record: ControlPriceStatusRecord) -> bool:
    higher = _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.slack_obstructed,
        _slack_obstruction_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.proxy_obstructed,
        _proxy_obstruction_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.summary_redescription,
        _summary_redescription_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.component_lawful,
        _component_lawful_evidence,
    )
    return (
        not higher
        and control_price_status_occurrence_for(fixture, claim_ref, record)
        and claim_ref.kind is ClaimKind.field
        and _field_lawful_evidence(fixture, claim_ref)
        and record.status is ControlPriceStatus.field_lawful
    )


def summary_lawful_case(fixture: Fixture, claim_ref: ControlPriceClaimRef, record: ControlPriceStatusRecord) -> bool:
    higher = _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.slack_obstructed,
        _slack_obstruction_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.proxy_obstructed,
        _proxy_obstruction_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.summary_redescription,
        _summary_redescription_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.component_lawful,
        _component_lawful_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.field_lawful,
        _field_lawful_evidence,
    )
    return (
        not higher
        and control_price_status_occurrence_for(fixture, claim_ref, record)
        and _summary_lawful_evidence(fixture, claim_ref)
        and record.status is ControlPriceStatus.summary_lawful
    )


def incomplete_or_unpriced_case(fixture: Fixture, claim_ref: ControlPriceClaimRef, record: ControlPriceStatusRecord) -> bool:
    higher = _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.slack_obstructed,
        _slack_obstruction_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.proxy_obstructed,
        _proxy_obstruction_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.summary_redescription,
        _summary_redescription_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.component_lawful,
        _component_lawful_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.field_lawful,
        _field_lawful_evidence,
    ) or _exists_main_status_record(
        fixture,
        claim_ref,
        ControlPriceStatus.summary_lawful,
        _summary_lawful_evidence,
    )
    return (
        not higher
        and control_price_status_occurrence_for(fixture, claim_ref, record)
        and record.status is ControlPriceStatus.incomplete_or_unpriced
    )


MAIN_CASES: tuple[tuple[ControlPriceStatus, Callable[[Fixture, ControlPriceClaimRef, ControlPriceStatusRecord], bool]], ...] = (
    (ControlPriceStatus.slack_obstructed, slack_obstructed_case),
    (ControlPriceStatus.proxy_obstructed, proxy_obstructed_case),
    (ControlPriceStatus.summary_redescription, summary_redescription_case),
    (ControlPriceStatus.component_lawful, component_lawful_case),
    (ControlPriceStatus.field_lawful, field_lawful_case),
    (ControlPriceStatus.summary_lawful, summary_lawful_case),
    (ControlPriceStatus.incomplete_or_unpriced, incomplete_or_unpriced_case),
)


def classify_control_price_status(
    fixture: Fixture,
    claim_name: str,
) -> tuple[ControlPriceStatus, dict[str, bool], ControlPriceStatusRecord | None]:
    claim_ref = fixture.control_claims[claim_name]
    record = next(
        (
            record
            for record in fixture.control_status_records.values()
            if control_price_status_occurrence_for(fixture, claim_ref, record)
        ),
        None,
    )
    if record is None:
        return ControlPriceStatus.unclassified, {}, None
    truths = {
        status.value: case(fixture, claim_ref, record)
        for status, case in MAIN_CASES
    }
    for status, _case in MAIN_CASES:
        if truths[status.value]:
            return status, truths, record
    return ControlPriceStatus.unclassified, truths, record


def budget_inflates(move: EndogenousBudgetSettingMove) -> bool:
    return move.old_budget < move.new_budget


def omega_lineage_blind_spot(hazard: int) -> bool:
    return blind_spot_excess(hazard) > 0


def budget_audit_status_record_matches_claim(record: BudgetAuditStatusRecord, claim_ref: BudgetAuditClaimRef) -> bool:
    return (
        record.budget_move_record == claim_ref.budget_move_record
        and record.lineage_record == claim_ref.lineage_record
        and record.health_record == claim_ref.health_record
    )


def budget_audit_status_occurrence_for(
    fixture: Fixture,
    claim_ref: BudgetAuditClaimRef,
    record: BudgetAuditStatusRecord,
) -> bool:
    return (
        budget_audit_status_record_matches_claim(record, claim_ref)
        and record.name in fixture.carried_budget_status_records
        and carried_source(record.source_tag, record.generated_by_s, record.in_scope)
        and all(entry in fixture.ledger_entries for entry in record.supporting_ledger_entries)
        and all(audit in fixture.audit_records for audit in record.supporting_audit_records)
    )


def capture_claim_rejected(fixture: Fixture, audit_name: str) -> bool:
    audit = fixture.no_capture_audits[audit_name]
    move = fixture.budget_moves[audit.budget_move]
    lineage = fixture.lineages[audit.lineage_record]
    health = fixture.health_records[audit.reported_health]
    blind = fixture.blind_spot_audits[audit.blind_spot_record]
    return (
        carried_source(move.source_tag, move.generated_by_s, move.in_scope)
        and blind.lineage_ref == lineage.name
        and not omega_lineage_blind_spot(blind.hazard)
        and fixture.lineage_agreement_comparator.agrees(health, lineage)
        and lineage.budget_move_ref == move.move_record.name
        and health.lineage_ref == lineage.name
    )


def capture_claim_rejected_case(fixture: Fixture, claim_ref: BudgetAuditClaimRef, record: BudgetAuditStatusRecord) -> bool:
    return (
        budget_audit_status_occurrence_for(fixture, claim_ref, record)
        and any(
            (
                capture_claim_rejected(fixture, audit.name)
                and (claimed := fixture.meta_audit_records[audit.claimed_capture_record])
                and (move := fixture.budget_moves[audit.budget_move])
                and claim_ref.budget_move_record == move.move_record.name
                and claim_ref.lineage_record == audit.lineage_record
                and claim_ref.health_record == audit.reported_health
                and claimed.budget_move_ref == move.move_record.name
                and claimed.lineage_ref == audit.lineage_record
                and record.meta_audit_record == claimed.name
            )
            for audit in fixture.no_capture_audits.values()
        )
        and record.status is BudgetAuditStatus.capture_claim_rejected
    )


def budget_inflation_audit(fixture: Fixture, audit_name: str, claim_ref: BudgetAuditClaimRef | None = None) -> bool:
    audit = fixture.budget_inflation_audits[audit_name]
    move = fixture.budget_moves[audit.budget_move]
    lineage = fixture.lineages[audit.lineage_record]
    blind = fixture.blind_spot_audits[audit.blind_spot_record]
    health = fixture.health_records[audit.reported_health]
    meta = fixture.meta_audit_records[audit.meta_audit_record]
    claim_lineage_ok = True if claim_ref is None else claim_ref.lineage_record == lineage.name
    claim_health_ok = True if claim_ref is None else claim_ref.health_record == health.name
    return (
        health.reports_healthy is True
        and budget_inflates(move)
        and omega_lineage_blind_spot(blind.hazard)
        and blind.lineage_ref == lineage.name
        and health.lineage_ref == lineage.name
        and meta.budget_move_ref == move.move_record.name
        and meta.lineage_ref == lineage.name
        and lineage.budget_move_ref == move.move_record.name
        and claim_lineage_ok
        and claim_health_ok
    )


def capture_detected_case(fixture: Fixture, claim_ref: BudgetAuditClaimRef, record: BudgetAuditStatusRecord) -> bool:
    higher = any(capture_claim_rejected_case(fixture, claim_ref, candidate) for candidate in fixture.budget_status_records.values())
    return (
        not higher
        and budget_audit_status_occurrence_for(fixture, claim_ref, record)
        and any(
            budget_inflation_audit(fixture, audit.name, claim_ref)
            and claim_ref.budget_move_record == fixture.budget_moves[audit.budget_move].move_record.name
            and record.meta_audit_record == audit.meta_audit_record
            for audit in fixture.budget_inflation_audits.values()
        )
        and record.status is BudgetAuditStatus.capture_detected
    )


def residual_discharge_audit(fixture: Fixture, audit_name: str, claim_ref: BudgetAuditClaimRef | None = None) -> bool:
    audit = fixture.residual_audits[audit_name]
    meta = fixture.meta_audit_records[audit.meta_audit_record]
    move = fixture.budget_moves[audit.budget_move]
    lineage = fixture.lineages[audit.lineage_record]
    claim_ok = True
    if claim_ref is not None:
        claim_ok = (
            claim_ref.budget_move_record == move.move_record.name
            and claim_ref.lineage_record == lineage.name
            and claim_ref.health_record is None
        )
    return (
        audit.residual_after < audit.residual_before
        and meta.budget_move_ref == move.move_record.name
        and meta.lineage_ref == lineage.name
        and lineage.budget_move_ref == move.move_record.name
        and claim_ok
    )


def residual_discharge_verified_case(fixture: Fixture, claim_ref: BudgetAuditClaimRef, record: BudgetAuditStatusRecord) -> bool:
    higher = any(
        capture_claim_rejected_case(fixture, claim_ref, candidate)
        or capture_detected_case(fixture, claim_ref, candidate)
        for candidate in fixture.budget_status_records.values()
    )
    return (
        not higher
        and budget_audit_status_occurrence_for(fixture, claim_ref, record)
        and any(
            residual_discharge_audit(fixture, audit.name, claim_ref)
            and record.meta_audit_record == audit.meta_audit_record
            for audit in fixture.residual_audits.values()
        )
        and record.status is BudgetAuditStatus.residual_discharge_verified
    )


def meta_audit_bounded_by_e2(fixture: Fixture, bound_name: str) -> bool:
    bound = fixture.e2_bounds[bound_name]
    return (
        capacity_realizable_tower(bound.levels)
        and capacity_admissible(bound.levels, bound.cap)
        and capacity_bound_holds(bound.levels, bound.cap)
    )


def meta_audit_capacity_blocked_case(fixture: Fixture, claim_ref: BudgetAuditClaimRef, record: BudgetAuditStatusRecord) -> bool:
    higher = any(
        capture_claim_rejected_case(fixture, claim_ref, candidate)
        or capture_detected_case(fixture, claim_ref, candidate)
        or residual_discharge_verified_case(fixture, claim_ref, candidate)
        for candidate in fixture.budget_status_records.values()
    )
    return (
        not higher
        and budget_audit_status_occurrence_for(fixture, claim_ref, record)
        and any(
            meta_audit_bounded_by_e2(fixture, bound.name)
            and capacity_saturated(bound.levels, bound.cap)
            and claim_ref.budget_move_record == fixture.budget_moves[bound.budget_move].move_record.name
            and claim_ref.lineage_record == bound.lineage_record
            and claim_ref.health_record == bound.health_record
            for bound in fixture.e2_bounds.values()
        )
        and record.status is BudgetAuditStatus.meta_audit_capacity_blocked
    )


def meta_audit_missing_case(fixture: Fixture, claim_ref: BudgetAuditClaimRef, record: BudgetAuditStatusRecord) -> bool:
    higher = any(
        capture_claim_rejected_case(fixture, claim_ref, candidate)
        or capture_detected_case(fixture, claim_ref, candidate)
        or residual_discharge_verified_case(fixture, claim_ref, candidate)
        or meta_audit_capacity_blocked_case(fixture, claim_ref, candidate)
        for candidate in fixture.budget_status_records.values()
    )
    return (
        not higher
        and budget_audit_status_occurrence_for(fixture, claim_ref, record)
        and record.status is BudgetAuditStatus.meta_audit_missing
    )


BUDGET_CASES: tuple[tuple[BudgetAuditStatus, Callable[[Fixture, BudgetAuditClaimRef, BudgetAuditStatusRecord], bool]], ...] = (
    (BudgetAuditStatus.capture_claim_rejected, capture_claim_rejected_case),
    (BudgetAuditStatus.capture_detected, capture_detected_case),
    (BudgetAuditStatus.residual_discharge_verified, residual_discharge_verified_case),
    (BudgetAuditStatus.meta_audit_capacity_blocked, meta_audit_capacity_blocked_case),
    (BudgetAuditStatus.meta_audit_missing, meta_audit_missing_case),
)


def classify_budget_audit_status(
    fixture: Fixture,
    claim_name: str,
) -> tuple[BudgetAuditStatus, dict[str, bool], BudgetAuditStatusRecord | None]:
    claim_ref = fixture.budget_claims[claim_name]
    record = next(
        (
            record
            for record in fixture.budget_status_records.values()
            if budget_audit_status_occurrence_for(fixture, claim_ref, record)
        ),
        None,
    )
    if record is None:
        return BudgetAuditStatus.unclassified, {}, None
    truths = {status.value: case(fixture, claim_ref, record) for status, case in BUDGET_CASES}
    for status, _case in BUDGET_CASES:
        if truths[status.value]:
            return status, truths, record
    return BudgetAuditStatus.unclassified, truths, record


def _main_row(fixture: Fixture, claim_name: str) -> MainStatusRow:
    status, truths, record = classify_control_price_status(fixture, claim_name)
    claim_ref = fixture.control_claims[claim_name]
    return MainStatusRow(
        claim=claim_name,
        claim_ref=claim_ref,
        record=record.name if record else "",
        slack_obstructed=truths.get("slack_obstructed", False),
        proxy_obstructed=truths.get("proxy_obstructed", False),
        summary_redescription=truths.get("summary_redescription", False),
        component_lawful=truths.get("component_lawful", False),
        field_lawful=truths.get("field_lawful", False),
        summary_lawful=truths.get("summary_lawful", False),
        incomplete_or_unpriced=truths.get("incomplete_or_unpriced", False),
        status=status.value,
    )


def _budget_row(fixture: Fixture, claim_name: str) -> BudgetStatusRow:
    status, truths, record = classify_budget_audit_status(fixture, claim_name)
    claim_ref = fixture.budget_claims[claim_name]
    return BudgetStatusRow(
        claim=claim_name,
        claim_ref=claim_ref,
        record=record.name if record else "",
        capture_claim_rejected=truths.get("capture_claim_rejected", False),
        capture_detected=truths.get("capture_detected", False),
        residual_discharge_verified=truths.get("residual_discharge_verified", False),
        meta_audit_capacity_blocked=truths.get("meta_audit_capacity_blocked", False),
        meta_audit_missing=truths.get("meta_audit_missing", False),
        status=status.value,
    )


def _main_summary(row: MainStatusRow) -> str:
    return f"status={row.status}; claim={row.claim_ref.kind.value}:{row.claim_ref.record}"


def _budget_summary(row: BudgetStatusRow) -> str:
    return (
        f"status={row.status}; key=({row.claim_ref.budget_move_record},"
        f"{row.claim_ref.lineage_record},{row.claim_ref.health_record})"
    )


def _control_rows(fixture: Fixture) -> tuple[ControlRow, ...]:
    rows: list[ControlRow] = []

    discharge_status = classify_budget_audit_status(fixture, "claim_shared_discharge")[0]
    capture_status = classify_budget_audit_status(fixture, "claim_shared_capture")[0]
    rows.append(
        ControlRow(
            "ctrl_budget_audit_claim_scoping",
            discharge_status is BudgetAuditStatus.residual_discharge_verified
            and capture_status is BudgetAuditStatus.capture_detected,
            f"bm_shared: discharge={discharge_status.value}; capture={capture_status.value}",
            "bm_shared supports two independent claim statuses",
        )
    )

    member_status = classify_control_price_status(fixture, "ctrl_field_member_slack_obstruction")[0]
    member_contains = control_claim_contains_component(
        fixture,
        fixture.control_claims["ctrl_field_member_slack_obstruction"],
        "cmp_io_slack_violation",
    )
    rows.append(
        ControlRow(
            "ctrl_field_member_slack_obstruction.status",
            member_status is ControlPriceStatus.slack_obstructed and member_contains is True,
            f"status={member_status.value}; contains={member_contains}",
            "slack_obstructed",
        )
    )

    unrelated_status = classify_control_price_status(fixture, "ctrl_unrelated_component_not_obstructing_field")[0]
    unrelated_contains = control_claim_contains_component(
        fixture,
        fixture.control_claims["ctrl_unrelated_component_not_obstructing_field"],
        "cmp_unrelated_slack_violation",
    )
    rows.append(
        ControlRow(
            "ctrl_unrelated_component_not_obstructing_field.status",
            unrelated_status is ControlPriceStatus.field_lawful and unrelated_contains is False,
            f"status={unrelated_status.value}; contains={unrelated_contains}",
            "field_lawful",
        )
    )

    summary_status = classify_control_price_status(fixture, "ctrl_summary_comparators_nontrivial")[0]
    summary_legit = summary_predictive_legitimacy(fixture, "summary_redescription")
    rows.append(
        ControlRow(
            "ctrl_summary_comparators_nontrivial.status",
            summary_status is ControlPriceStatus.summary_redescription and summary_legit is False,
            f"status={summary_status.value}; SummaryPredictiveLegitimacy={summary_legit}",
            "summary_redescription",
        )
    )

    bound = fixture.e2_bounds["capacity_bound"]
    footprint = tower_footprint(bound.levels)
    cap_ok = capacity_bound_holds(bound.levels, bound.cap)
    saturated = capacity_saturated(bound.levels, bound.cap)
    rows.append(
        ControlRow(
            "ctrl_e2_capacity_bound_computed",
            footprint == 8 and bound.cap == 8 and cap_ok is True and saturated is True,
            f"footprint={footprint}; cap={bound.cap}; bound={cap_ok}; saturated={saturated}",
            "footprint=8; cap=8; bound=True; saturated=True",
        )
    )

    inflation_no_blind_status = classify_budget_audit_status(fixture, "claim_inflation_no_blind")[0]
    rows.append(
        ControlRow(
            "ctrl_inflation_without_blindspot.status",
            inflation_no_blind_status is BudgetAuditStatus.residual_discharge_verified
            and not omega_lineage_blind_spot(0),
            f"status={inflation_no_blind_status.value}; capture_detected={capture_detected_case(fixture, fixture.budget_claims['claim_inflation_no_blind'], fixture.budget_status_records['status_inflation_no_blind'])}",
            "residual_discharge_verified; capture_detected=False",
        )
    )

    wrong_claim = fixture.budget_claims["ctrl_wrong_lineage_capture_claim"]
    wrong_record = fixture.budget_status_records["status_wrong_lineage_capture"]
    wrong_capture = capture_detected_case(fixture, wrong_claim, wrong_record)
    rows.append(
        ControlRow(
            "ctrl_wrong_lineage_capture_claim",
            wrong_capture is False
            and budget_inflation_audit(fixture, "inflation_wrong_lineage", wrong_claim) is False
            and omega_lineage_blind_spot(1) is True,
            f"capture_detected={wrong_capture}; audit_lineage=lineage_wrong_source; claim_lineage=lineage_claim_actual",
            "capture_detected=False",
        )
    )

    flag_claim = fixture.budget_claims["ctrl_disconnected_budget_inflation_flag"]
    flag_record = fixture.budget_status_records["status_disconnected_budget_flag"]
    flag_move = fixture.budget_moves["bm_equal_budget_metadata_inflated"]
    flag_capture = capture_detected_case(fixture, flag_claim, flag_record)
    flag_audit = budget_inflation_audit(fixture, "inflation_flag_blind", flag_claim)
    rows.append(
        ControlRow(
            "ctrl_disconnected_budget_inflation_flag",
            flag_move.reported_inflated is True
            and budget_inflates(flag_move) is False
            and flag_audit is False
            and flag_capture is False,
            (
                f"reportedInflated={flag_move.reported_inflated}; "
                f"budgetInflates={budget_inflates(flag_move)}; "
                f"BudgetInflationAudit={flag_audit}; capture_detected={flag_capture}"
            ),
            "budgetInflates=False; BudgetInflationAudit=False; capture_detected=False",
        )
    )

    return tuple(rows)


def _comparisons(results: SweepResults) -> tuple[Comparison, ...]:
    main = {row.claim: row for row in results.main_rows}
    budget = {row.claim: row for row in results.budget_rows}
    expected_main = {
        "claim_component_cpu_lawful": "component_lawful",
        "claim_field_ops_lawful": "field_lawful",
        "claim_summary_ops_lawful": "summary_lawful",
        "claim_summary_slack_obstructed": "slack_obstructed",
        "claim_component_io_slack": "slack_obstructed",
        "claim_component_proxy": "proxy_obstructed",
        "claim_summary_redescription": "summary_redescription",
        "claim_field_incomplete": "incomplete_or_unpriced",
    }
    expected_budget = {
        "claim_shared_discharge": "residual_discharge_verified",
        "claim_shared_capture": "capture_detected",
        "claim_no_capture_rejected": "capture_claim_rejected",
        "claim_capacity_blocked": "meta_audit_capacity_blocked",
        "claim_missing_meta_audit": "meta_audit_missing",
    }
    comparisons: list[Comparison] = []
    for name, expected in expected_main.items():
        row = main[name]
        comparisons.append(
            Comparison(
                f"{name}.status",
                row.status == expected
                and sum(
                    (
                        row.slack_obstructed,
                        row.proxy_obstructed,
                        row.summary_redescription,
                        row.component_lawful,
                        row.field_lawful,
                        row.summary_lawful,
                        row.incomplete_or_unpriced,
                    )
                )
                == 1,
                _main_summary(row),
                expected,
            )
        )
    for name, expected in expected_budget.items():
        row = budget[name]
        comparisons.append(
            Comparison(
                f"{name}.status",
                row.status == expected
                and sum(
                    (
                        row.capture_claim_rejected,
                        row.capture_detected,
                        row.residual_discharge_verified,
                        row.meta_audit_capacity_blocked,
                        row.meta_audit_missing,
                    )
                )
                == 1,
                _budget_summary(row),
                expected,
            )
        )
    comparisons.extend(
        Comparison(control.name, control.passed_control, control.observed, control.expected)
        for control in results.controls
    )
    return tuple(comparisons)


def _actual_scope_discipline(fixture: Fixture) -> bool:
    return all(
        control_price_status_occurrence_for(fixture, fixture.control_claims[row.claim], fixture.control_status_records[row.record])
        for row in (_main_row(fixture, name) for name in MAIN_COMPARISON_ORDER)
    ) and all(
        budget_audit_status_occurrence_for(fixture, fixture.budget_claims[row.claim], fixture.budget_status_records[row.record])
        for row in (_budget_row(fixture, name) for name in BUDGET_COMPARISON_ORDER)
    )


def _no_hardcoded_status_discipline(results: SweepResults) -> bool:
    return all(
        sum(
            (
                row.slack_obstructed,
                row.proxy_obstructed,
                row.summary_redescription,
                row.component_lawful,
                row.field_lawful,
                row.summary_lawful,
                row.incomplete_or_unpriced,
            )
        )
        == 1
        for row in results.main_rows
    ) and all(
        sum(
            (
                row.capture_claim_rejected,
                row.capture_detected,
                row.residual_discharge_verified,
                row.meta_audit_capacity_blocked,
                row.meta_audit_missing,
            )
        )
        == 1
        for row in results.budget_rows
    )


def run_e8_control_price_sweep() -> SweepResults:
    fixture = build_fixture()
    main_rows = tuple(_main_row(fixture, name) for name in MAIN_COMPARISON_ORDER)
    budget_rows = tuple(_budget_row(fixture, name) for name in BUDGET_COMPARISON_ORDER)
    results = SweepResults(
        main_rows=main_rows,
        budget_rows=budget_rows,
        controls=_control_rows(fixture),
        actual_scope_discipline=_actual_scope_discipline(fixture),
        no_hardcoded_status_discipline=False,
        comparisons=(),
    )
    results = SweepResults(
        **{
            **results.__dict__,
            "no_hardcoded_status_discipline": _no_hardcoded_status_discipline(results),
        }
    )
    return SweepResults(**{**results.__dict__, "comparisons": _comparisons(results)})


def results_markdown(results: SweepResults) -> str:
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    lines = [
        "# E8 Control Price Sweep Results",
        "",
        "Generated by `sixbirds_foundations_v.sweeps.e8_control_price_sweep` against "
        "`formalization/notes/sweeps/E8_control_price_predictions.md`.",
        "",
        f"Overall verdict: {'PASS' if not failures else 'FAIL'}",
        "",
        "## Registered Prediction Comparisons",
        "",
        "| check | verdict | observed | registered prediction |",
        "| --- | --- | --- | --- |",
    ]
    for comparison in results.comparisons:
        lines.append(
            f"| {comparison.name} | {'PASS' if comparison.passed else 'FAIL'} | "
            f"{comparison.observed} | {comparison.expected} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- All arithmetic is exact `fractions.Fraction`; no stochastic branch is used.",
            "- Main status rows are scoped by `ControlPriceClaimRef` and budget-audit rows "
            "by the full `(budgetMove,lineage,health)` `BudgetAuditClaimRef`.",
            "- Summary legitimacy and proxy checks use shared comparator objects.",
            "- E2 capacity and Xi/Omega blind-spot checks call the existing E2/E7 sweep helpers.",
            "",
        ]
    )
    return "\n".join(lines)


def write_results_report(path: Path = DEFAULT_RESULTS_PATH) -> SweepResults:
    results = run_e8_control_price_sweep()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(results_markdown(results), encoding="utf-8")
    return results


def main() -> None:
    results = write_results_report()
    total = len(results.comparisons)
    passed = sum(1 for comparison in results.comparisons if comparison.passed)
    print(f"E8 control price sweep: {passed}/{total} comparisons PASS")
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    if failures:
        for failure in failures:
            print(f"FAIL {failure.name}: observed {failure.observed}; expected {failure.expected}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
