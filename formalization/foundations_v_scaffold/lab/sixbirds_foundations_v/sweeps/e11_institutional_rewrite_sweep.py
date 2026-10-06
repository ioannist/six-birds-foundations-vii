"""E11 institutional-rewrite sweep against the pre-registration.

The configuration is fixed by
``formalization/notes/sweeps/E11_institutional_rewrite_predictions.md``.
This module evaluates that deterministic fixture with exact ``Fraction``
arithmetic.  Support/closure differences, FIII top-down gate outcomes,
``Delta_stack`` controls, status classification, and Lucas-style descent
residuals are computed from concrete carried records and comparator functions
rather than copied from the prediction table.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Any

from sixbirds_foundations_v.carried_records import FineSourceTag


F = Fraction

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESULTS_PATH = (
    REPO_ROOT
    / "formalization"
    / "notes"
    / "sweeps"
    / "E11_institutional_rewrite_results.md"
)

STATES = ("a", "b", "c", "d")
SUPPORT_EPSILON = F(1, 100)


class ClaimStatus(str, Enum):
    accepted = "accepted"
    blocked = "blocked"


class InstitutionalRewriteStatus(str, Enum):
    inert = "inert"
    conditioning = "conditioning"
    stack_active = "stack_active"
    constitutive = "constitutive"
    unclassified = "unclassified"


@dataclass(frozen=True)
class TopDownChannelRecord:
    name: str
    host: str
    profile: str
    macro_record_present: bool
    substrate_record_present: bool
    structural_path_present: bool
    intervention_gate: bool
    matched_controls_gate: bool
    feasibility_gate: bool
    source_gate: bool
    visibility_gate: bool
    audit_gate: bool
    no_smuggling_gate: bool
    effect_gate: bool
    comparator_finite: bool
    threshold_finite: bool
    nonclaim_recorded: bool


@dataclass(frozen=True)
class InstitutionalIntervention:
    name: str
    label: str
    label_record: str
    intervention_record: str
    support: frozenset[tuple[str, str]]
    closure_signature: str
    parameter_value: Fraction
    transition_weights: dict[tuple[str, str], Fraction]
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True
    used_ledger_entries: tuple[str, ...] = ()
    used_audit_records: tuple[str, ...] = ()


@dataclass(frozen=True)
class MatchedInstitutionalComparison:
    name: str
    comparison_record: str
    theta_i: str
    theta_j: str
    channel_record: str
    matched_controls_record: str
    controlled_lower_context: str
    uncontrolled_difference_witness: str | None


@dataclass(frozen=True)
class InstitutionalStructuralEffect:
    name: str
    effect_record: str
    comparison_record: str
    channel_record: str
    observed_outcome: str
    support_witness: tuple[str, str] | None = None
    closure_witness: str | None = None


@dataclass(frozen=True)
class InstitutionalParameterEffect:
    name: str
    parameter_record: str
    comparison_record: str
    observed_outcome: str


@dataclass(frozen=True)
class InstitutionalRewriteStatusRecord:
    name: str
    comparison_record: str
    status: InstitutionalRewriteStatus
    channel_record: str | None
    effect_record: str | None
    parameter_record: str | None
    compiled_record: str | None
    supporting_ledger_entries: tuple[str, ...]
    supporting_audit_records: tuple[str, ...]
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class E4CompiledInstitutionalRewrite:
    compiled_records: dict[tuple[str, str, str], str]

    def holds(
        self,
        comparison: MatchedInstitutionalComparison,
        channel_name: str,
        effect: InstitutionalStructuralEffect,
    ) -> bool:
        return (comparison.name, channel_name, effect.name) in self.compiled_records

    def compiled_record_for(
        self,
        comparison: MatchedInstitutionalComparison,
        channel_name: str,
        effect: InstitutionalStructuralEffect,
    ) -> str | None:
        return self.compiled_records.get((comparison.name, channel_name, effect.name))


@dataclass(frozen=True)
class StatusRow:
    name: str
    comparison: str
    carried_status_record: str | None
    status: str
    inert: bool
    conditioning: bool
    stack_active: bool
    constitutive: bool


@dataclass(frozen=True)
class LucasRow:
    regime: str
    comparison: str
    predicted_support_bd: int
    actual_support_bd: int
    residual: int
    descent_failure: bool


@dataclass(frozen=True)
class Comparison:
    name: str
    passed: bool
    observed: str
    expected: str


@dataclass(frozen=True)
class SweepResults:
    top_down_outcomes: dict[str, dict[str, Any]]
    theorem_rows: dict[str, dict[str, bool]]
    status_rows: tuple[StatusRow, ...]
    lucas_rows: tuple[LucasRow, ...]
    delta_controls: dict[str, bool]
    matched_controls_failure: dict[str, bool]
    boundary_controls: dict[str, dict[str, bool | str]]
    unlinked_control: dict[str, bool]
    closure_only_control: dict[str, bool | str]
    macro_inert_control: dict[str, bool | str]
    near_zero_control: dict[str, bool | str]
    constitutive_overclaim_control: dict[str, bool]
    blocked_channel_control: dict[str, bool | str]
    actual_scope_discipline: bool
    no_hardcoded_status_discipline: bool
    comparisons: tuple[Comparison, ...]


@dataclass(frozen=True)
class Fixture:
    interventions: dict[str, InstitutionalIntervention]
    comparisons: dict[str, MatchedInstitutionalComparison]
    channels: dict[str, TopDownChannelRecord]
    structural_effects: dict[str, InstitutionalStructuralEffect]
    parameter_effects: dict[str, InstitutionalParameterEffect]
    status_records: dict[str, InstitutionalRewriteStatusRecord]
    e4_compiled: E4CompiledInstitutionalRewrite
    carried_label_records: frozenset[str]
    carried_intervention_records: frozenset[str]
    carried_comparison_records: frozenset[str]
    carried_effect_records: frozenset[str]
    carried_parameter_records: frozenset[str]
    carried_compiled_records: frozenset[str]
    carried_channel_records: frozenset[str]
    carried_status_records: frozenset[str]
    ledger_entries: frozenset[str]
    audit_records: frozenset[str]
    static_label_comparisons: frozenset[str]
    base_independent_comparisons: frozenset[str]
    strict_refinement_comparisons: frozenset[str]


def accepted_top_down_record(name: str) -> TopDownChannelRecord:
    return TopDownChannelRecord(
        name=name,
        host="Host.fin",
        profile="baseProfile",
        macro_record_present=True,
        substrate_record_present=True,
        structural_path_present=True,
        intervention_gate=True,
        matched_controls_gate=True,
        feasibility_gate=True,
        source_gate=True,
        visibility_gate=True,
        audit_gate=True,
        no_smuggling_gate=True,
        effect_gate=True,
        comparator_finite=True,
        threshold_finite=True,
        nonclaim_recorded=True,
    )


def structural_only_top_down_record() -> TopDownChannelRecord:
    accepted = accepted_top_down_record("td_structural_only")
    return TopDownChannelRecord(
        **{
            **accepted.__dict__,
            "intervention_gate": False,
            "effect_gate": False,
        }
    )


def wf_top_down_channel_record_bool(record: TopDownChannelRecord) -> bool:
    return (
        record.macro_record_present
        and record.substrate_record_present
        and record.comparator_finite
        and record.threshold_finite
        and record.nonclaim_recorded
    )


def td_gates_pass_bool(record: TopDownChannelRecord) -> bool:
    return (
        record.macro_record_present
        and record.intervention_gate
        and record.matched_controls_gate
        and record.feasibility_gate
        and record.source_gate
        and record.visibility_gate
        and record.audit_gate
        and record.no_smuggling_gate
        and record.effect_gate
    )


def top_down_channel_accepted_bool(record: TopDownChannelRecord) -> bool:
    return (
        record.structural_path_present
        and wf_top_down_channel_record_bool(record)
        and td_gates_pass_bool(record)
    )


def struct_down(record: TopDownChannelRecord) -> bool:
    return record.structural_path_present


def top_down_channel_claim_status(record: TopDownChannelRecord) -> ClaimStatus:
    return (
        ClaimStatus.accepted
        if top_down_channel_accepted_bool(record)
        else ClaimStatus.blocked
    )


def _base_support() -> frozenset[tuple[str, str]]:
    return frozenset(
        {
            ("a", "a"),
            ("a", "b"),
            ("b", "b"),
            ("b", "c"),
            ("c", "c"),
            ("c", "d"),
            ("d", "d"),
        }
    )


def _support_with(*extra: tuple[str, str], remove: tuple[str, str] | None = None) -> frozenset[tuple[str, str]]:
    support = set(_base_support())
    if remove is not None:
        support.remove(remove)
    support.update(extra)
    return frozenset(support)


def _weights(*, bd: Fraction | None = None) -> dict[tuple[str, str], Fraction]:
    weights = {edge: F(1, 1) for edge in _base_support()}
    if bd is not None:
        weights[("b", "d")] = bd
    return weights


def _intervention(
    name: str,
    label: str,
    record_suffix: str,
    support: frozenset[tuple[str, str]],
    closure: str,
    parameter_value: Fraction,
    *,
    transition_weights: dict[tuple[str, str], Fraction] | None = None,
) -> InstitutionalIntervention:
    return InstitutionalIntervention(
        name=name,
        label=label,
        label_record=f"lrec_{record_suffix}",
        intervention_record=f"irec_{record_suffix}",
        support=support,
        closure_signature=closure,
        parameter_value=parameter_value,
        transition_weights=transition_weights or _weights(),
        used_ledger_entries=(f"led_{record_suffix}",),
        used_audit_records=(f"aud_{record_suffix}",),
    )


def build_fixture() -> Fixture:
    base = _base_support()
    license_support = _support_with(("b", "d"), remove=("b", "c"))
    constitution_support = _support_with(("a", "d"))
    interventions = {
        "theta_open": _intervention("theta_open", "open_market", "open", base, "closure_base", F(1, 2)),
        "theta_license": _intervention(
            "theta_license",
            "license_regime",
            "license",
            license_support,
            "closure_license",
            F(1, 2),
        ),
        "theta_low_fee": _intervention("theta_low_fee", "fee_low", "low_fee", base, "closure_base", F(1, 3)),
        "theta_high_fee": _intervention("theta_high_fee", "fee_high", "high_fee", base, "closure_base", F(2, 3)),
        "theta_static_blue": _intervention(
            "theta_static_blue", "static_blue", "static_blue", base, "closure_base", F(1, 2)
        ),
        "theta_static_red": _intervention(
            "theta_static_red", "static_red", "static_red", base, "closure_base", F(1, 2)
        ),
        "theta_macro_left": _intervention(
            "theta_macro_left", "macro_left", "macro_left", base, "closure_base", F(1, 2)
        ),
        "theta_macro_right": _intervention(
            "theta_macro_right", "macro_right", "macro_right", base, "closure_base", F(1, 2)
        ),
        "theta_near_low": _intervention(
            "theta_near_low",
            "near_low",
            "near_low",
            base,
            "closure_base",
            F(0, 1),
            transition_weights=_weights(bd=F(0, 1)),
        ),
        "theta_near_high": _intervention(
            "theta_near_high",
            "near_high",
            "near_high",
            base,
            "closure_base",
            F(1, 1000),
            transition_weights=_weights(bd=F(1, 1000)),
        ),
        "theta_constitution_old": _intervention(
            "theta_constitution_old",
            "charter_old",
            "charter_old",
            base,
            "closure_base",
            F(1, 2),
        ),
        "theta_constitution_new": _intervention(
            "theta_constitution_new",
            "charter_new",
            "charter_new",
            constitution_support,
            "closure_constitution",
            F(1, 2),
        ),
        "theta_closure_old": _intervention(
            "theta_closure_old",
            "closure_old",
            "closure_old",
            base,
            "closure_base",
            F(1, 2),
        ),
        "theta_closure_new": _intervention(
            "theta_closure_new",
            "closure_new",
            "closure_new",
            base,
            "closure_cycle_rank_2",
            F(1, 2),
        ),
    }
    channels = {
        "td_accepted_stack": accepted_top_down_record("td_accepted_stack"),
        "td_accepted_conditioning": accepted_top_down_record("td_accepted_conditioning"),
        "td_accepted_washout": accepted_top_down_record("td_accepted_washout"),
        "td_accepted_constitutive": accepted_top_down_record("td_accepted_constitutive"),
        "td_accepted_closure": accepted_top_down_record("td_accepted_closure"),
        "td_accepted_delta_claimed": accepted_top_down_record("td_accepted_delta_claimed"),
        "td_accepted_delta_placebo": accepted_top_down_record("td_accepted_delta_placebo"),
        "td_structural_only": structural_only_top_down_record(),
    }
    comparisons = {
        "comp_stack_license": MatchedInstitutionalComparison(
            "comp_stack_license",
            "mcr_stack_license",
            "theta_open",
            "theta_license",
            "td_accepted_stack",
            "aud_matched_stack",
            "ctx_game",
            None,
        ),
        "comp_conditioning_fee": MatchedInstitutionalComparison(
            "comp_conditioning_fee",
            "mcr_conditioning_fee",
            "theta_low_fee",
            "theta_high_fee",
            "td_accepted_conditioning",
            "aud_matched_fee",
            "ctx_game",
            None,
        ),
        "comp_washout_static": MatchedInstitutionalComparison(
            "comp_washout_static",
            "mcr_washout_static",
            "theta_static_blue",
            "theta_static_red",
            "td_accepted_washout",
            "aud_matched_washout",
            "ctx_game",
            None,
        ),
        "comp_constitutive_rule": MatchedInstitutionalComparison(
            "comp_constitutive_rule",
            "mcr_constitutive_rule",
            "theta_constitution_old",
            "theta_constitution_new",
            "td_accepted_constitutive",
            "aud_matched_constitutive",
            "ctx_game",
            None,
        ),
        "comp_stack_closure": MatchedInstitutionalComparison(
            "comp_stack_closure",
            "mcr_stack_closure",
            "theta_closure_old",
            "theta_closure_new",
            "td_accepted_closure",
            "aud_matched_closure",
            "ctx_game",
            None,
        ),
        "comp_macro_label": MatchedInstitutionalComparison(
            "comp_macro_label",
            "mcr_macro_label",
            "theta_macro_left",
            "theta_macro_right",
            "td_structural_only",
            "aud_matched_macro",
            "ctx_game",
            None,
        ),
        "comp_near_zero": MatchedInstitutionalComparison(
            "comp_near_zero",
            "mcr_near_zero",
            "theta_near_low",
            "theta_near_high",
            "td_accepted_conditioning",
            "aud_matched_near",
            "ctx_game",
            None,
        ),
        "comp_stack_blocked_channel": MatchedInstitutionalComparison(
            "comp_stack_blocked_channel",
            "mcr_stack_blocked_channel",
            "theta_open",
            "theta_license",
            "td_structural_only",
            "aud_matched_blocked_channel",
            "ctx_game",
            None,
        ),
        "comp_delta_claimed": MatchedInstitutionalComparison(
            "comp_delta_claimed",
            "mcr_delta_claimed",
            "theta_open",
            "theta_license",
            "td_accepted_delta_claimed",
            "aud_matched_delta_claimed",
            "ctx_game",
            None,
        ),
        "comp_delta_placebo": MatchedInstitutionalComparison(
            "comp_delta_placebo",
            "mcr_delta_placebo",
            "theta_low_fee",
            "theta_high_fee",
            "td_accepted_delta_placebo",
            "aud_matched_delta_placebo",
            "ctx_game",
            None,
        ),
        "comp_unmatched": MatchedInstitutionalComparison(
            "comp_unmatched",
            "mcr_unmatched",
            "theta_open",
            "theta_license",
            "td_accepted_stack",
            "aud_matched_unmatched",
            "ctx_game",
            "uncontrolled_context_shift",
        ),
        "comp_unlinked_other": MatchedInstitutionalComparison(
            "comp_unlinked_other",
            "mcr_unlinked_other",
            "theta_static_blue",
            "theta_static_red",
            "td_accepted_washout",
            "aud_matched_unlinked",
            "ctx_game",
            None,
        ),
    }
    structural_effects = {
        "effect_stack_exit": InstitutionalStructuralEffect(
            "effect_stack_exit",
            "ierc_stack_exit",
            "mcr_stack_license",
            "td_accepted_stack",
            "out_direct_exit_available",
            support_witness=("b", "d"),
        ),
        "effect_constitutive_charter": InstitutionalStructuralEffect(
            "effect_constitutive_charter",
            "ierc_constitutive_charter",
            "mcr_constitutive_rule",
            "td_accepted_constitutive",
            "out_constitutional_exit_available",
            support_witness=("a", "d"),
            closure_witness="closure_diff_constitution",
        ),
        "effect_stack_closure": InstitutionalStructuralEffect(
            "effect_stack_closure",
            "ierc_stack_closure",
            "mcr_stack_closure",
            "td_accepted_closure",
            "out_cycle_rank_changed",
            closure_witness="closure_diff_cycle_rank",
        ),
        "effect_blocked_channel": InstitutionalStructuralEffect(
            "effect_blocked_channel",
            "ierc_blocked_channel",
            "mcr_stack_blocked_channel",
            "td_structural_only",
            "out_blocked_channel_support_difference",
            support_witness=("b", "d"),
        ),
        "effect_delta_claimed": InstitutionalStructuralEffect(
            "effect_delta_claimed",
            "ierc_delta_claimed",
            "mcr_delta_claimed",
            "td_accepted_delta_claimed",
            "out_defection_pressure_shift",
            support_witness=("b", "d"),
        ),
        "effect_unlinked": InstitutionalStructuralEffect(
            "effect_unlinked",
            "ierc_unlinked",
            "mcr_unlinked_other",
            "td_accepted_stack",
            "out_direct_exit_available",
            support_witness=("b", "d"),
        ),
    }
    parameter_effects = {
        "param_effect_fee": InstitutionalParameterEffect(
            "param_effect_fee",
            "prec_fee",
            "mcr_conditioning_fee",
            "out_fee_shift_only",
        ),
        "param_effect_delta_placebo": InstitutionalParameterEffect(
            "param_effect_delta_placebo",
            "prec_delta_placebo",
            "mcr_delta_placebo",
            "out_defection_pressure_shift",
        ),
        "param_effect_near_zero": InstitutionalParameterEffect(
            "param_effect_near_zero",
            "prec_near_zero",
            "mcr_near_zero",
            "out_tiny_weight_shift",
        ),
    }
    status_records = {
        "isr_stack": InstitutionalRewriteStatusRecord(
            "isr_stack",
            "mcr_stack_license",
            InstitutionalRewriteStatus.stack_active,
            "td_accepted_stack",
            "ierc_stack_exit",
            None,
            None,
            ("led_status_stack",),
            ("aud_status_stack",),
        ),
        "isr_constitutive": InstitutionalRewriteStatusRecord(
            "isr_constitutive",
            "mcr_constitutive_rule",
            InstitutionalRewriteStatus.constitutive,
            "td_accepted_constitutive",
            "ierc_constitutive_charter",
            None,
            "comp_rec_constitutive",
            ("led_status_constitutive",),
            ("aud_status_constitutive",),
        ),
        "isr_stack_closure": InstitutionalRewriteStatusRecord(
            "isr_stack_closure",
            "mcr_stack_closure",
            InstitutionalRewriteStatus.stack_active,
            "td_accepted_closure",
            "ierc_stack_closure",
            None,
            None,
            ("led_status_closure",),
            ("aud_status_closure",),
        ),
        "isr_conditioning": InstitutionalRewriteStatusRecord(
            "isr_conditioning",
            "mcr_conditioning_fee",
            InstitutionalRewriteStatus.conditioning,
            None,
            None,
            "prec_fee",
            None,
            ("led_status_conditioning",),
            ("aud_status_conditioning",),
        ),
        "isr_inert": InstitutionalRewriteStatusRecord(
            "isr_inert",
            "mcr_washout_static",
            InstitutionalRewriteStatus.inert,
            None,
            None,
            None,
            None,
            ("led_status_inert",),
            ("aud_status_inert",),
        ),
        "isr_macro_inert": InstitutionalRewriteStatusRecord(
            "isr_macro_inert",
            "mcr_macro_label",
            InstitutionalRewriteStatus.inert,
            None,
            None,
            None,
            None,
            ("led_status_macro",),
            ("aud_status_macro",),
        ),
        "isr_near_zero": InstitutionalRewriteStatusRecord(
            "isr_near_zero",
            "mcr_near_zero",
            InstitutionalRewriteStatus.conditioning,
            None,
            None,
            "prec_near_zero",
            None,
            ("led_status_near",),
            ("aud_status_near",),
        ),
        "isr_blocked_channel": InstitutionalRewriteStatusRecord(
            "isr_blocked_channel",
            "mcr_stack_blocked_channel",
            InstitutionalRewriteStatus.inert,
            None,
            None,
            None,
            None,
            ("led_status_blocked_channel",),
            ("aud_status_blocked_channel",),
        ),
    }
    ledger_entries = {
        entry
        for intervention in interventions.values()
        for entry in intervention.used_ledger_entries
    } | {
        entry
        for status in status_records.values()
        for entry in status.supporting_ledger_entries
    }
    audit_records = {
        audit
        for intervention in interventions.values()
        for audit in intervention.used_audit_records
    } | {
        audit
        for status in status_records.values()
        for audit in status.supporting_audit_records
    } | {comparison.matched_controls_record for comparison in comparisons.values()}
    return Fixture(
        interventions=interventions,
        comparisons=comparisons,
        channels=channels,
        structural_effects=structural_effects,
        parameter_effects=parameter_effects,
        status_records=status_records,
        e4_compiled=E4CompiledInstitutionalRewrite(
            {
                (
                    "comp_constitutive_rule",
                    "td_accepted_constitutive",
                    "effect_constitutive_charter",
                ): "comp_rec_constitutive"
            }
        ),
        carried_label_records=frozenset(
            intervention.label_record for intervention in interventions.values()
        ),
        carried_intervention_records=frozenset(
            intervention.intervention_record for intervention in interventions.values()
        ),
        carried_comparison_records=frozenset(
            comparison.comparison_record for comparison in comparisons.values()
        ),
        carried_effect_records=frozenset(
            effect.effect_record for effect in structural_effects.values()
        ),
        carried_parameter_records=frozenset(
            effect.parameter_record for effect in parameter_effects.values()
        ),
        carried_compiled_records=frozenset({"comp_rec_constitutive"}),
        carried_channel_records=frozenset(channels),
        carried_status_records=frozenset(status_records),
        ledger_entries=frozenset(ledger_entries),
        audit_records=frozenset(audit_records),
        static_label_comparisons=frozenset({"comp_washout_static"}),
        base_independent_comparisons=frozenset({"comp_washout_static"}),
        strict_refinement_comparisons=frozenset(),
    )


def institutional_intervention_occurrence_for(
    fixture: Fixture,
    intervention: InstitutionalIntervention,
) -> bool:
    return (
        intervention.label_record in fixture.carried_label_records
        and intervention.intervention_record in fixture.carried_intervention_records
        and intervention.source_tag
        in {FineSourceTag.committed_state, FineSourceTag.audited_cell_records}
        and intervention.generated_by_s is True
        and intervention.in_scope is True
        and all(entry in fixture.ledger_entries for entry in intervention.used_ledger_entries)
        and all(audit in fixture.audit_records for audit in intervention.used_audit_records)
    )


def distinct_institutional_interventions(
    theta_i: InstitutionalIntervention,
    theta_j: InstitutionalIntervention,
) -> bool:
    return (
        theta_i.label != theta_j.label
        and theta_i.intervention_record != theta_j.intervention_record
    )


def matched_controls_comparison(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
) -> bool:
    theta_i = fixture.interventions[comparison.theta_i]
    theta_j = fixture.interventions[comparison.theta_j]
    channel = fixture.channels[comparison.channel_record]
    return (
        institutional_intervention_occurrence_for(fixture, theta_i)
        and institutional_intervention_occurrence_for(fixture, theta_j)
        and distinct_institutional_interventions(theta_i, theta_j)
        and comparison.comparison_record in fixture.carried_comparison_records
        and comparison.matched_controls_record in fixture.audit_records
        and comparison.uncontrolled_difference_witness is None
        and channel.matched_controls_gate is True
    )


def support_under(
    intervention: InstitutionalIntervention,
    z: str,
    z_next: str,
) -> bool:
    if (z, z_next) in {("b", "d")}:
        return (
            (z, z_next) in intervention.support
            and intervention.transition_weights.get((z, z_next), F(1)) >= SUPPORT_EPSILON
        )
    return (z, z_next) in intervention.support


def kernel_support_differs(
    fixture: Fixture,
    theta_i_name: str,
    theta_j_name: str,
) -> bool:
    theta_i = fixture.interventions[theta_i_name]
    theta_j = fixture.interventions[theta_j_name]
    return any(
        support_under(theta_i, z, z_next) != support_under(theta_j, z, z_next)
        for z in STATES
        for z_next in STATES
    )


def closure_differs(
    fixture: Fixture,
    theta_i_name: str,
    theta_j_name: str,
) -> bool:
    return (
        fixture.interventions[theta_i_name].closure_signature
        != fixture.interventions[theta_j_name].closure_signature
    )


def parameters_differ(
    fixture: Fixture,
    theta_i_name: str,
    theta_j_name: str,
) -> bool:
    return (
        fixture.interventions[theta_i_name].parameter_value
        != fixture.interventions[theta_j_name].parameter_value
    )


def parameter_conditioning_only(
    fixture: Fixture,
    theta_i_name: str,
    theta_j_name: str,
) -> bool:
    return (
        parameters_differ(fixture, theta_i_name, theta_j_name)
        and not kernel_support_differs(fixture, theta_i_name, theta_j_name)
        and not closure_differs(fixture, theta_i_name, theta_j_name)
    )


def structural_effect_for(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
    channel_name: str,
    effect: InstitutionalStructuralEffect,
) -> bool:
    if channel_name not in fixture.channels:
        return False
    channel = fixture.channels[channel_name]
    support_witness_ok = False
    if effect.support_witness is not None:
        z, z_next = effect.support_witness
        support_witness_ok = support_under(
            fixture.interventions[comparison.theta_i], z, z_next
        ) != support_under(fixture.interventions[comparison.theta_j], z, z_next)
    closure_witness_ok = (
        effect.closure_witness is not None
        and closure_differs(fixture, comparison.theta_i, comparison.theta_j)
    )
    return (
        matched_controls_comparison(fixture, comparison)
        and comparison.channel_record == channel_name
        and effect.comparison_record == comparison.comparison_record
        and effect.channel_record == channel_name
        and effect.effect_record in fixture.carried_effect_records
        and channel_name in fixture.carried_channel_records
        and top_down_channel_accepted_bool(channel) is True
        and channel.effect_gate is True
        and (support_witness_ok or closure_witness_ok)
    )


def structural_effects_for(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
) -> tuple[tuple[str, InstitutionalStructuralEffect], ...]:
    return tuple(
        (channel_name, effect)
        for channel_name in fixture.channels
        for effect in fixture.structural_effects.values()
        if structural_effect_for(fixture, comparison, channel_name, effect)
    )


def reproduces_claimed_effect(
    parameter_effect: InstitutionalParameterEffect,
    structural_effect: InstitutionalStructuralEffect,
) -> bool:
    return parameter_effect.observed_outcome == structural_effect.observed_outcome


def delta_stack(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
    effect: InstitutionalStructuralEffect,
    parameter_comparison: MatchedInstitutionalComparison,
    parameter_effect: InstitutionalParameterEffect,
) -> bool:
    return (
        matched_controls_comparison(fixture, comparison)
        and effect.comparison_record == comparison.comparison_record
        and matched_controls_comparison(fixture, parameter_comparison)
        and parameter_effect.comparison_record == parameter_comparison.comparison_record
        and parameter_effect.parameter_record in fixture.carried_parameter_records
        and parameter_conditioning_only(
            fixture, parameter_comparison.theta_i, parameter_comparison.theta_j
        )
        and reproduces_claimed_effect(parameter_effect, effect)
    )


def delta_stack_witnesses(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
    effect: InstitutionalStructuralEffect,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        (parameter_comparison.name, parameter_effect.name)
        for parameter_comparison in fixture.comparisons.values()
        for parameter_effect in fixture.parameter_effects.values()
        if delta_stack(
            fixture,
            comparison,
            effect,
            parameter_comparison,
            parameter_effect,
        )
    )


def delta_stack_empty_for(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
    effect: InstitutionalStructuralEffect,
) -> bool:
    return len(delta_stack_witnesses(fixture, comparison, effect)) == 0


def institutional_rewrite_status_occurrence_for(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
    record: InstitutionalRewriteStatusRecord,
) -> bool:
    return (
        matched_controls_comparison(fixture, comparison)
        and record.comparison_record == comparison.comparison_record
        and record.name in fixture.carried_status_records
        and record.source_tag
        in {FineSourceTag.committed_state, FineSourceTag.audited_cell_records}
        and record.generated_by_s is True
        and record.in_scope is True
        and all(entry in fixture.ledger_entries for entry in record.supporting_ledger_entries)
        and all(audit in fixture.audit_records for audit in record.supporting_audit_records)
    )


def static_institutional_labels(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
) -> bool:
    return comparison.name in fixture.static_label_comparisons


def base_independent_behavior(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
) -> bool:
    return comparison.name in fixture.base_independent_comparisons


def strict_institutional_refinement(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
) -> bool:
    return comparison.name in fixture.strict_refinement_comparisons


def washout_null(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
) -> bool:
    return (
        static_institutional_labels(fixture, comparison)
        and base_independent_behavior(fixture, comparison)
        and not strict_institutional_refinement(fixture, comparison)
        and not parameter_conditioning_only(fixture, comparison.theta_i, comparison.theta_j)
        and len(structural_effects_for(fixture, comparison)) == 0
    )


def nctd_control(record: TopDownChannelRecord) -> bool:
    return struct_down(record) and top_down_channel_claim_status(record) is ClaimStatus.blocked


def constitutive_evidence(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
    channel_name: str,
    effect: InstitutionalStructuralEffect,
    compiled_record: str,
) -> bool:
    return (
        structural_effect_for(fixture, comparison, channel_name, effect)
        and delta_stack_empty_for(fixture, comparison, effect)
        and fixture.e4_compiled.holds(comparison, channel_name, effect)
        and compiled_record in fixture.carried_compiled_records
        and compiled_record
        == fixture.e4_compiled.compiled_record_for(comparison, channel_name, effect)
    )


def constitutive_evidence_exists_for(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
) -> bool:
    return any(
        constitutive_evidence(fixture, comparison, channel_name, effect, compiled_record)
        for channel_name in fixture.channels
        for effect in fixture.structural_effects.values()
        for compiled_record in fixture.carried_compiled_records
    )


def stack_active_evidence(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
    channel_name: str,
    effect: InstitutionalStructuralEffect,
) -> bool:
    return (
        structural_effect_for(fixture, comparison, channel_name, effect)
        and delta_stack_empty_for(fixture, comparison, effect)
        and not constitutive_evidence_exists_for(fixture, comparison)
    )


def conditioning_evidence(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
    parameter_effect: InstitutionalParameterEffect,
) -> bool:
    return (
        matched_controls_comparison(fixture, comparison)
        and parameter_effect.comparison_record == comparison.comparison_record
        and parameter_effect.parameter_record in fixture.carried_parameter_records
        and parameter_conditioning_only(fixture, comparison.theta_i, comparison.theta_j)
        and len(structural_effects_for(fixture, comparison)) == 0
    )


def inert_evidence(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
) -> bool:
    return matched_controls_comparison(fixture, comparison) and (
        washout_null(fixture, comparison)
        or (
            not parameter_conditioning_only(
                fixture, comparison.theta_i, comparison.theta_j
            )
            and len(structural_effects_for(fixture, comparison)) == 0
        )
    )


def inert_case(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
    record: InstitutionalRewriteStatusRecord,
) -> bool:
    return (
        institutional_rewrite_status_occurrence_for(fixture, comparison, record)
        and record.status is InstitutionalRewriteStatus.inert
        and record.channel_record is None
        and record.effect_record is None
        and record.parameter_record is None
        and record.compiled_record is None
        and inert_evidence(fixture, comparison)
    )


def conditioning_case(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
    record: InstitutionalRewriteStatusRecord,
) -> bool:
    return any(
        institutional_rewrite_status_occurrence_for(fixture, comparison, record)
        and record.status is InstitutionalRewriteStatus.conditioning
        and record.channel_record is None
        and record.parameter_record == parameter_effect.parameter_record
        and record.effect_record is None
        and record.compiled_record is None
        and conditioning_evidence(fixture, comparison, parameter_effect)
        for parameter_effect in fixture.parameter_effects.values()
    )


def stack_active_case(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
    record: InstitutionalRewriteStatusRecord,
) -> bool:
    return any(
        institutional_rewrite_status_occurrence_for(fixture, comparison, record)
        and record.status is InstitutionalRewriteStatus.stack_active
        and record.channel_record == channel_name
        and record.effect_record == effect.effect_record
        and record.parameter_record is None
        and record.compiled_record is None
        and stack_active_evidence(fixture, comparison, channel_name, effect)
        for channel_name in fixture.channels
        for effect in fixture.structural_effects.values()
    )


def constitutive_case(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
    record: InstitutionalRewriteStatusRecord,
) -> bool:
    return any(
        institutional_rewrite_status_occurrence_for(fixture, comparison, record)
        and record.status is InstitutionalRewriteStatus.constitutive
        and record.channel_record == channel_name
        and record.effect_record == effect.effect_record
        and record.parameter_record is None
        and record.compiled_record == compiled_record
        and constitutive_evidence(
            fixture, comparison, channel_name, effect, compiled_record
        )
        for channel_name in fixture.channels
        for effect in fixture.structural_effects.values()
        for compiled_record in fixture.carried_compiled_records
    )


def classify_institutional_rewrite_status(
    fixture: Fixture,
    comparison: MatchedInstitutionalComparison,
) -> tuple[InstitutionalRewriteStatus, dict[str, bool], str | None]:
    records = [
        record
        for record in fixture.status_records.values()
        if record.comparison_record == comparison.comparison_record
    ]
    truths = {
        "inert": any(inert_case(fixture, comparison, record) for record in records),
        "conditioning": any(
            conditioning_case(fixture, comparison, record) for record in records
        ),
        "stack_active": any(
            stack_active_case(fixture, comparison, record) for record in records
        ),
        "constitutive": any(
            constitutive_case(fixture, comparison, record) for record in records
        ),
    }
    record_name = records[0].name if records else None
    for status in (
        InstitutionalRewriteStatus.inert,
        InstitutionalRewriteStatus.conditioning,
        InstitutionalRewriteStatus.stack_active,
        InstitutionalRewriteStatus.constitutive,
    ):
        if truths[status.value]:
            return status, truths, record_name
    return InstitutionalRewriteStatus.unclassified, truths, record_name


def _status_rows(fixture: Fixture) -> tuple[StatusRow, ...]:
    rows = []
    for row_name, comparison_name in (
        ("stack_support_rewrite", "comp_stack_license"),
        ("stack_closure_rewrite", "comp_stack_closure"),
        ("constitutive_compiled", "comp_constitutive_rule"),
        ("conditioning_fee", "comp_conditioning_fee"),
        ("washout_static", "comp_washout_static"),
    ):
        comparison = fixture.comparisons[comparison_name]
        status, truths, record_name = classify_institutional_rewrite_status(
            fixture, comparison
        )
        rows.append(
            StatusRow(
                name=row_name,
                comparison=comparison_name,
                carried_status_record=record_name,
                status=status.value,
                inert=truths["inert"],
                conditioning=truths["conditioning"],
                stack_active=truths["stack_active"],
                constitutive=truths["constitutive"],
            )
        )
    return tuple(rows)


def _theorem_rows(fixture: Fixture) -> dict[str, dict[str, bool]]:
    stack = fixture.comparisons["comp_stack_license"]
    stack_effect = fixture.structural_effects["effect_stack_exit"]
    stack_record = fixture.status_records["isr_stack"]
    constitutive = fixture.comparisons["comp_constitutive_rule"]
    constitutive_effect = fixture.structural_effects["effect_constitutive_charter"]
    constitutive_record = fixture.status_records["isr_constitutive"]
    conditioning = fixture.comparisons["comp_conditioning_fee"]
    parameter_effect = fixture.parameter_effects["param_effect_fee"]
    conditioning_record = fixture.status_records["isr_conditioning"]
    washout = fixture.comparisons["comp_washout_static"]
    inert_record = fixture.status_records["isr_inert"]
    return {
        "E11_StackActivity": {
            "matched": matched_controls_comparison(fixture, stack),
            "structural_effect_for": structural_effect_for(
                fixture, stack, "td_accepted_stack", stack_effect
            ),
            "delta_stack_empty_for": delta_stack_empty_for(fixture, stack, stack_effect),
            "not_constitutive_exists": not constitutive_evidence_exists_for(
                fixture, stack
            ),
            "status_occurrence": institutional_rewrite_status_occurrence_for(
                fixture, stack, stack_record
            ),
            "status_tag": stack_record.status is InstitutionalRewriteStatus.stack_active,
            "channel_field": stack_record.channel_record == "td_accepted_stack",
            "effect_field": stack_record.effect_record == stack_effect.effect_record,
            "parameter_field": stack_record.parameter_record is None,
            "compiled_field": stack_record.compiled_record is None,
            "holds": stack_active_case(fixture, stack, stack_record),
        },
        "E11_Constitutive": {
            "matched": matched_controls_comparison(fixture, constitutive),
            "structural_effect_for": structural_effect_for(
                fixture,
                constitutive,
                "td_accepted_constitutive",
                constitutive_effect,
            ),
            "delta_stack_empty_for": delta_stack_empty_for(
                fixture, constitutive, constitutive_effect
            ),
            "e4_holds": fixture.e4_compiled.holds(
                constitutive, "td_accepted_constitutive", constitutive_effect
            ),
            "compiled_record_carried": "comp_rec_constitutive"
            in fixture.carried_compiled_records,
            "compiled_record_eq": fixture.e4_compiled.compiled_record_for(
                constitutive, "td_accepted_constitutive", constitutive_effect
            )
            == "comp_rec_constitutive",
            "status_occurrence": institutional_rewrite_status_occurrence_for(
                fixture, constitutive, constitutive_record
            ),
            "status_tag": constitutive_record.status
            is InstitutionalRewriteStatus.constitutive,
            "compiled_field": constitutive_record.compiled_record
            == "comp_rec_constitutive",
            "holds": constitutive_case(fixture, constitutive, constitutive_record),
        },
        "E11_ConditioningOnly": {
            "matched": matched_controls_comparison(fixture, conditioning),
            "parameter_conditioning_only": parameter_conditioning_only(
                fixture, conditioning.theta_i, conditioning.theta_j
            ),
            "no_structural_effect": len(structural_effects_for(fixture, conditioning))
            == 0,
            "parameter_effect_record": parameter_effect.comparison_record
            == conditioning.comparison_record,
            "parameter_record_carried": parameter_effect.parameter_record
            in fixture.carried_parameter_records,
            "status_occurrence": institutional_rewrite_status_occurrence_for(
                fixture, conditioning, conditioning_record
            ),
            "status_tag": conditioning_record.status
            is InstitutionalRewriteStatus.conditioning,
            "parameter_field": conditioning_record.parameter_record
            == parameter_effect.parameter_record,
            "holds": conditioning_case(fixture, conditioning, conditioning_record),
        },
        "E11_WashoutInert": {
            "static_labels": static_institutional_labels(fixture, washout),
            "base_independent": base_independent_behavior(fixture, washout),
            "not_strict_refinement": not strict_institutional_refinement(
                fixture, washout
            ),
            "not_parameter_conditioning": not parameter_conditioning_only(
                fixture, washout.theta_i, washout.theta_j
            ),
            "no_structural_effect": len(structural_effects_for(fixture, washout))
            == 0,
            "washout_null": washout_null(fixture, washout),
            "status_occurrence": institutional_rewrite_status_occurrence_for(
                fixture, washout, inert_record
            ),
            "status_tag": inert_record.status is InstitutionalRewriteStatus.inert,
            "option_fields_none": inert_record.channel_record is None
            and inert_record.effect_record is None
            and inert_record.parameter_record is None
            and inert_record.compiled_record is None,
            "holds": inert_case(fixture, washout, inert_record),
        },
        "E11_NCTDObstruction": {
            "struct_down": struct_down(fixture.channels["td_structural_only"]),
            "accepted": top_down_channel_accepted_bool(
                fixture.channels["td_structural_only"]
            ),
            "blocked": top_down_channel_claim_status(
                fixture.channels["td_structural_only"]
            )
            is ClaimStatus.blocked,
            "obstruction": nctd_control(fixture.channels["td_structural_only"]),
        },
    }


def _lucas_rows(fixture: Fixture) -> tuple[LucasRow, ...]:
    rows = []
    for regime, comparison_name in (
        ("washout/static", "comp_washout_static"),
        ("conditioning-only", "comp_conditioning_fee"),
        ("stack-active license", "comp_stack_license"),
    ):
        comparison = fixture.comparisons[comparison_name]
        predicted = int(
            support_under(fixture.interventions[comparison.theta_i], "b", "d")
        )
        actual = int(support_under(fixture.interventions[comparison.theta_j], "b", "d"))
        residual = abs(actual - predicted)
        rows.append(
            LucasRow(
                regime=regime,
                comparison=comparison_name,
                predicted_support_bd=predicted,
                actual_support_bd=actual,
                residual=residual,
                descent_failure=residual != 0,
            )
        )
    return tuple(rows)


def _top_down_outcomes(fixture: Fixture) -> dict[str, dict[str, Any]]:
    return {
        name: {
            "StructDown": struct_down(record),
            "TopDownChannelAcceptedBool": top_down_channel_accepted_bool(record),
            "TopDownChannelClaimStatus": top_down_channel_claim_status(record).value,
        }
        for name, record in fixture.channels.items()
    }


def _delta_controls(fixture: Fixture) -> dict[str, bool]:
    claimed = fixture.comparisons["comp_delta_claimed"]
    claimed_effect = fixture.structural_effects["effect_delta_claimed"]
    placebo = fixture.comparisons["comp_delta_placebo"]
    placebo_effect = fixture.parameter_effects["param_effect_delta_placebo"]
    stack = fixture.comparisons["comp_stack_license"]
    stack_effect = fixture.structural_effects["effect_stack_exit"]
    return {
        "stack_delta_empty": delta_stack_empty_for(fixture, stack, stack_effect),
        "placebo_parameter_conditioning": parameter_conditioning_only(
            fixture, placebo.theta_i, placebo.theta_j
        ),
        "placebo_reproduces_claim": reproduces_claimed_effect(
            placebo_effect, claimed_effect
        ),
        "delta_stack_nonempty": delta_stack(
            fixture, claimed, claimed_effect, placebo, placebo_effect
        ),
        "claimed_delta_empty": delta_stack_empty_for(fixture, claimed, claimed_effect),
        "claimed_credited_stack_active": any(
            row.comparison == "comp_delta_claimed" and row.stack_active
            for row in _status_rows(fixture)
        ),
    }


def _matched_controls_failure(fixture: Fixture) -> dict[str, bool]:
    unmatched = fixture.comparisons["comp_unmatched"]
    return {
        "has_uncontrolled_witness": unmatched.uncontrolled_difference_witness is not None,
        "matched_controls": matched_controls_comparison(fixture, unmatched),
        "structural_effect_for_any": len(structural_effects_for(fixture, unmatched)) > 0,
        "status_theorem_applies": any(
            record.comparison_record == unmatched.comparison_record
            for record in fixture.status_records.values()
        ),
    }


def _boundary_controls(fixture: Fixture) -> dict[str, dict[str, bool | str]]:
    controls: dict[str, dict[str, bool | str]] = {}
    for comparison_name in ("comp_washout_static", "comp_conditioning_fee"):
        comparison = fixture.comparisons[comparison_name]
        status, _, _ = classify_institutional_rewrite_status(fixture, comparison)
        controls[comparison_name] = {
            "static_labels": static_institutional_labels(fixture, comparison),
            "base_independent": base_independent_behavior(fixture, comparison),
            "parameters_differ": parameters_differ(
                fixture, comparison.theta_i, comparison.theta_j
            ),
            "parameter_conditioning_only": parameter_conditioning_only(
                fixture, comparison.theta_i, comparison.theta_j
            ),
            "status": status.value,
        }
    return controls


def _unlinked_control(fixture: Fixture) -> dict[str, bool]:
    stack = fixture.comparisons["comp_stack_license"]
    effect = fixture.structural_effects["effect_unlinked"]
    return {
        "accepted_channel": top_down_channel_accepted_bool(
            fixture.channels["td_accepted_stack"]
        ),
        "support_inequality": support_under(
            fixture.interventions[stack.theta_i], "b", "d"
        )
        != support_under(fixture.interventions[stack.theta_j], "b", "d"),
        "effect_comparison_matches": effect.comparison_record == stack.comparison_record,
        "structural_effect_for": structural_effect_for(
            fixture, stack, "td_accepted_stack", effect
        ),
        "stack_active_from_unlinked": structural_effect_for(
            fixture, stack, "td_accepted_stack", effect
        )
        and delta_stack_empty_for(fixture, stack, effect),
    }


def _closure_only_control(fixture: Fixture) -> dict[str, bool | str]:
    comparison = fixture.comparisons["comp_stack_closure"]
    effect = fixture.structural_effects["effect_stack_closure"]
    status, _, _ = classify_institutional_rewrite_status(fixture, comparison)
    return {
        "comparison": comparison.name,
        "kernel_support_differs": kernel_support_differs(
            fixture, comparison.theta_i, comparison.theta_j
        ),
        "closure_differs": closure_differs(fixture, comparison.theta_i, comparison.theta_j),
        "structural_effect_for": structural_effect_for(
            fixture, comparison, "td_accepted_closure", effect
        ),
        "delta_stack_empty": delta_stack_empty_for(fixture, comparison, effect),
        "constitutive_exists": constitutive_evidence_exists_for(fixture, comparison),
        "status": status.value,
    }


def _macro_inert_control(fixture: Fixture) -> dict[str, bool | str]:
    comparison = fixture.comparisons["comp_macro_label"]
    status, _, _ = classify_institutional_rewrite_status(fixture, comparison)
    theta_i = fixture.interventions[comparison.theta_i]
    theta_j = fixture.interventions[comparison.theta_j]
    return {
        "accepted": top_down_channel_accepted_bool(
            fixture.channels["td_structural_only"]
        ),
        "support_equal": all(
            support_under(theta_i, z, z_next) == support_under(theta_j, z, z_next)
            for z in STATES
            for z_next in STATES
        ),
        "closure_differs": closure_differs(fixture, comparison.theta_i, comparison.theta_j),
        "parameter_values_equal": theta_i.parameter_value == theta_j.parameter_value,
        "parameter_conditioning_only": parameter_conditioning_only(
            fixture, comparison.theta_i, comparison.theta_j
        ),
        "structural_effect_for_any": len(structural_effects_for(fixture, comparison))
        > 0,
        "status": status.value,
    }


def _near_zero_control(fixture: Fixture) -> dict[str, bool | str]:
    comparison = fixture.comparisons["comp_near_zero"]
    status, _, _ = classify_institutional_rewrite_status(fixture, comparison)
    return {
        "support_low_bd": support_under(fixture.interventions[comparison.theta_i], "b", "d"),
        "support_high_bd": support_under(
            fixture.interventions[comparison.theta_j], "b", "d"
        ),
        "kernel_support_differs": kernel_support_differs(
            fixture, comparison.theta_i, comparison.theta_j
        ),
        "closure_differs": closure_differs(fixture, comparison.theta_i, comparison.theta_j),
        "parameter_conditioning_only": parameter_conditioning_only(
            fixture, comparison.theta_i, comparison.theta_j
        ),
        "status": status.value,
    }


def _constitutive_overclaim_control(fixture: Fixture) -> dict[str, bool]:
    comparison = fixture.comparisons["comp_stack_license"]
    effect = fixture.structural_effects["effect_stack_exit"]
    status, truths, _ = classify_institutional_rewrite_status(fixture, comparison)
    return {
        "structural_effect_for": structural_effect_for(
            fixture, comparison, "td_accepted_stack", effect
        ),
        "e4_holds": fixture.e4_compiled.holds(
            comparison, "td_accepted_stack", effect
        ),
        "constitutive_exists": constitutive_evidence_exists_for(fixture, comparison),
        "constitutive_holds": truths["constitutive"],
        "stack_active_holds": truths["stack_active"],
        "status_is_stack_active": status is InstitutionalRewriteStatus.stack_active,
    }


def _blocked_channel_control(fixture: Fixture) -> dict[str, bool | str]:
    comparison = fixture.comparisons["comp_stack_blocked_channel"]
    effect = fixture.structural_effects["effect_blocked_channel"]
    status, truths, _ = classify_institutional_rewrite_status(fixture, comparison)
    return {
        "theta_pair_is_open_license": comparison.theta_i == "theta_open"
        and comparison.theta_j == "theta_license",
        "channel_is_structural_only": comparison.channel_record == "td_structural_only",
        "support_difference": kernel_support_differs(
            fixture, comparison.theta_i, comparison.theta_j
        ),
        "support_witness_genuine": support_under(
            fixture.interventions[comparison.theta_i], "b", "d"
        )
        is False
        and support_under(fixture.interventions[comparison.theta_j], "b", "d")
        is True,
        "top_down_accepted": top_down_channel_accepted_bool(
            fixture.channels[comparison.channel_record]
        ),
        "top_down_status": top_down_channel_claim_status(
            fixture.channels[comparison.channel_record]
        ).value,
        "effect_comparison_matches": effect.comparison_record
        == comparison.comparison_record,
        "effect_channel_matches": effect.channel_record == comparison.channel_record,
        "structural_effect_for": structural_effect_for(
            fixture, comparison, comparison.channel_record, effect
        ),
        "stack_active_holds": truths["stack_active"],
        "status": status.value,
    }


def _actual_scope_discipline(fixture: Fixture, status_rows: tuple[StatusRow, ...]) -> bool:
    return all(
        row.carried_status_record in fixture.carried_status_records
        and fixture.status_records[row.carried_status_record].comparison_record
        == fixture.comparisons[row.comparison].comparison_record
        for row in status_rows
        if row.carried_status_record is not None
    )


def _no_hardcoded_status_discipline(status_rows: tuple[StatusRow, ...]) -> bool:
    return all(
        sum((row.inert, row.conditioning, row.stack_active, row.constitutive)) == 1
        and row.status
        in {
            InstitutionalRewriteStatus.inert.value,
            InstitutionalRewriteStatus.conditioning.value,
            InstitutionalRewriteStatus.stack_active.value,
            InstitutionalRewriteStatus.constitutive.value,
        }
        for row in status_rows
    )


def _theorem_row_ok(row: dict[str, bool]) -> bool:
    return all(row.values())


def _status_table_ok(rows: tuple[StatusRow, ...]) -> bool:
    expected = {
        "stack_support_rewrite": "stack_active",
        "stack_closure_rewrite": "stack_active",
        "constitutive_compiled": "constitutive",
        "conditioning_fee": "conditioning",
        "washout_static": "inert",
    }
    return all(
        row.status == expected[row.name]
        and sum((row.inert, row.conditioning, row.stack_active, row.constitutive)) == 1
        for row in rows
    )


def _lucas_rows_ok(rows: tuple[LucasRow, ...]) -> bool:
    expected = {
        "washout/static": (0, 0, 0, False),
        "conditioning-only": (0, 0, 0, False),
        "stack-active license": (0, 1, 1, True),
    }
    return all(
        (
            row.predicted_support_bd,
            row.actual_support_bd,
            row.residual,
            row.descent_failure,
        )
        == expected[row.regime]
        for row in rows
    )


def _comparisons(results: SweepResults) -> tuple[Comparison, ...]:
    theorem = results.theorem_rows
    top_down = results.top_down_outcomes
    delta = results.delta_controls
    matched = results.matched_controls_failure
    boundary = results.boundary_controls
    unlinked = results.unlinked_control
    closure = results.closure_only_control
    macro = results.macro_inert_control
    near = results.near_zero_control
    overclaim = results.constitutive_overclaim_control
    blocked = results.blocked_channel_control
    return (
        Comparison(
            "fixture and carried objects",
            all(
                row["status_occurrence"]
                for key, row in theorem.items()
                if key
                in {
                    "E11_StackActivity",
                    "E11_Constitutive",
                    "E11_ConditioningOnly",
                    "E11_WashoutInert",
                }
            ),
            "carried intervention/comparison/effect/parameter/status records are present for theorem rows",
            "actual carried institutional records listed in pre-registration",
        ),
        Comparison(
            "FIII top-down fixture",
            top_down["td_accepted_stack"]["TopDownChannelAcceptedBool"] is True
            and top_down["td_accepted_stack"]["TopDownChannelClaimStatus"] == "accepted"
            and top_down["td_structural_only"]["StructDown"] is True
            and top_down["td_structural_only"]["TopDownChannelAcceptedBool"] is False
            and top_down["td_structural_only"]["TopDownChannelClaimStatus"] == "blocked",
            f"accepted_stack={top_down['td_accepted_stack']}; structural_only={top_down['td_structural_only']}",
            "acceptedTopDownRecord accepted; structuralOnlyTopDownRecord blocked",
        ),
        Comparison(
            "E11_StackActivity",
            _theorem_row_ok(theorem["E11_StackActivity"]),
            _mapping_summary(theorem["E11_StackActivity"]),
            "support witness (b,d), empty Delta_stack, no constitutive evidence, carried isr_stack",
        ),
        Comparison(
            "E11_Constitutive",
            _theorem_row_ok(theorem["E11_Constitutive"]),
            _mapping_summary(theorem["E11_Constitutive"]),
            "certified E4 table, carried compiled record, and constitutive status witness",
        ),
        Comparison(
            "E11_ConditioningOnly",
            _theorem_row_ok(theorem["E11_ConditioningOnly"]),
            _mapping_summary(theorem["E11_ConditioningOnly"]),
            "parameter-only fee comparison with no structural effect",
        ),
        Comparison(
            "E11_WashoutInert",
            _theorem_row_ok(theorem["E11_WashoutInert"]),
            _mapping_summary(theorem["E11_WashoutInert"]),
            "washout null with not ParameterConditioningOnly and no structural effect",
        ),
        Comparison(
            "E11_NCTDObstruction",
            theorem["E11_NCTDObstruction"]["struct_down"]
            and theorem["E11_NCTDObstruction"]["accepted"] is False
            and theorem["E11_NCTDObstruction"]["blocked"]
            and theorem["E11_NCTDObstruction"]["obstruction"],
            _mapping_summary(theorem["E11_NCTDObstruction"]),
            "structural path present but FIII claim status blocked",
        ),
        Comparison(
            "E11_StatusPartition",
            _status_table_ok(results.status_rows),
            _status_summary(results.status_rows),
            "each exercised comparison has exactly one computed status",
        ),
        Comparison(
            "closure-only stack-active control",
            closure["kernel_support_differs"] is False
            and closure["closure_differs"] is True
            and closure["structural_effect_for"] is True
            and closure["delta_stack_empty"] is True
            and closure["constitutive_exists"] is False
            and closure["status"] == "stack_active",
            _mapping_summary(closure),
            "same support, changed closure, stack_active",
        ),
        Comparison(
            "macro-inert control",
            macro["accepted"] is False
            and macro["support_equal"] is True
            and macro["closure_differs"] is False
            and macro["parameter_values_equal"] is True
            and macro["parameter_conditioning_only"] is False
            and macro["structural_effect_for_any"] is False
            and macro["status"] == "inert",
            _mapping_summary(macro),
            "macro label row has no accepted channel, no parameter channel, no structural effect",
        ),
        Comparison(
            "near-zero tolerance control",
            near["support_low_bd"] is False
            and near["support_high_bd"] is False
            and near["kernel_support_differs"] is False
            and near["closure_differs"] is False
            and near["parameter_conditioning_only"] is True
            and near["status"] == "conditioning",
            _mapping_summary(near),
            "1/1000 weight remains below 1/100 support threshold; conditioning, not stack_active",
        ),
        Comparison(
            "constitutive overclaim before E4",
            overclaim["structural_effect_for"] is True
            and overclaim["e4_holds"] is False
            and overclaim["constitutive_exists"] is False
            and overclaim["constitutive_holds"] is False
            and overclaim["stack_active_holds"] is True
            and overclaim["status_is_stack_active"] is True,
            _mapping_summary(overclaim),
            "accepted structural channel without E4 compiled evidence remains stack_active",
        ),
        Comparison(
            "blocked channel with genuine structural difference",
            blocked["theta_pair_is_open_license"] is True
            and blocked["channel_is_structural_only"] is True
            and blocked["support_difference"] is True
            and blocked["support_witness_genuine"] is True
            and blocked["top_down_accepted"] is False
            and blocked["top_down_status"] == "blocked"
            and blocked["effect_comparison_matches"] is True
            and blocked["effect_channel_matches"] is True
            and blocked["structural_effect_for"] is False
            and blocked["stack_active_holds"] is False
            and blocked["status"] == "inert",
            _mapping_summary(blocked),
            "real support difference refused stack_active because the FIII channel is blocked",
        ),
        Comparison(
            "Lucas-style descent failure",
            _lucas_rows_ok(results.lucas_rows),
            _lucas_summary(results.lucas_rows),
            "washout/conditioning residual 0; stack-active license residual 1",
        ),
        Comparison(
            "Delta_stack nonempty control",
            delta["stack_delta_empty"] is True
            and delta["placebo_parameter_conditioning"] is True
            and delta["placebo_reproduces_claim"] is True
            and delta["delta_stack_nonempty"] is True
            and delta["claimed_delta_empty"] is False
            and delta["claimed_credited_stack_active"] is False,
            _mapping_summary(delta),
            "stack effect has empty Delta; separate claimed effect is reproduced by placebo",
        ),
        Comparison(
            "matched-controls failure control",
            matched["has_uncontrolled_witness"] is True
            and matched["matched_controls"] is False
            and matched["structural_effect_for_any"] is False
            and matched["status_theorem_applies"] is False,
            _mapping_summary(matched),
            "uncontrolledDifferenceWitness blocks comparison from theorem scope",
        ),
        Comparison(
            "inert/conditioning boundary control",
            boundary["comp_washout_static"]["parameter_conditioning_only"] is False
            and boundary["comp_washout_static"]["status"] == "inert"
            and boundary["comp_conditioning_fee"]["parameter_conditioning_only"] is True
            and boundary["comp_conditioning_fee"]["status"] == "conditioning",
            f"washout={_mapping_summary(boundary['comp_washout_static'])}; "
            f"conditioning={_mapping_summary(boundary['comp_conditioning_fee'])}",
            "opposite ParameterConditioningOnly values produce inert vs conditioning",
        ),
        Comparison(
            "unlinked evidence control",
            unlinked["accepted_channel"] is True
            and unlinked["support_inequality"] is True
            and unlinked["effect_comparison_matches"] is False
            and unlinked["structural_effect_for"] is False
            and unlinked["stack_active_from_unlinked"] is False,
            _mapping_summary(unlinked),
            "effect comparison record mismatch blocks StructuralEffectFor",
        ),
        Comparison(
            "actual carried comparison scope",
            results.actual_scope_discipline,
            "status rows use carried status records tied to their actual comparison records",
            "no existential feasible intervention or unrelated status record used",
        ),
        Comparison(
            "future sweep anti-hardcoding guard",
            results.no_hardcoded_status_discipline,
            "all status rows have exactly one computed branch truth",
            "support/closure/status/Delta/Lucas rows derived from fixture predicates",
        ),
    )


def run_institutional_rewrite_sweep() -> SweepResults:
    fixture = build_fixture()
    status_rows = _status_rows(fixture)
    results = SweepResults(
        top_down_outcomes=_top_down_outcomes(fixture),
        theorem_rows=_theorem_rows(fixture),
        status_rows=status_rows,
        lucas_rows=_lucas_rows(fixture),
        delta_controls=_delta_controls(fixture),
        matched_controls_failure=_matched_controls_failure(fixture),
        boundary_controls=_boundary_controls(fixture),
        unlinked_control=_unlinked_control(fixture),
        closure_only_control=_closure_only_control(fixture),
        macro_inert_control=_macro_inert_control(fixture),
        near_zero_control=_near_zero_control(fixture),
        constitutive_overclaim_control=_constitutive_overclaim_control(fixture),
        blocked_channel_control=_blocked_channel_control(fixture),
        actual_scope_discipline=_actual_scope_discipline(fixture, status_rows),
        no_hardcoded_status_discipline=_no_hardcoded_status_discipline(status_rows),
        comparisons=(),
    )
    return SweepResults(**{**results.__dict__, "comparisons": _comparisons(results)})


def _fmt_bool(value: Any) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def _mapping_summary(mapping: dict[str, Any]) -> str:
    return "; ".join(f"{key}={_fmt_bool(value)}" for key, value in sorted(mapping.items()))


def _status_summary(rows: tuple[StatusRow, ...]) -> str:
    return "; ".join(
        f"{row.name}: status={row.status}, branches="
        f"({row.inert},{row.conditioning},{row.stack_active},{row.constitutive})"
        for row in rows
    )


def _lucas_summary(rows: tuple[LucasRow, ...]) -> str:
    return "; ".join(
        f"{row.regime}: predicted={row.predicted_support_bd}, actual={row.actual_support_bd}, "
        f"residual={row.residual}, failure={row.descent_failure}"
        for row in rows
    )


def results_markdown(results: SweepResults) -> str:
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    lines = [
        "# E11 Institutional Rewrite Sweep Results",
        "",
        "Generated by `sixbirds_foundations_v.sweeps.e11_institutional_rewrite_sweep` "
        "against `formalization/notes/sweeps/E11_institutional_rewrite_predictions.md`.",
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
            "- Arithmetic is exact `fractions.Fraction`; no stochastic or floating-point branch is used.",
            "- The FIII top-down channel mirror uses the vendored Lean field names and boolean gate logic: "
            "`TopDownChannelAcceptedBool = structuralPathPresent && WF && TDGatesPass`.",
            "- Support and closure differences are computed from the concrete intervention records' support "
            "sets and closure signatures, including the near-zero threshold check for `(b,d)`.",
            "- `StructuralEffectFor` checks the same comparison/channel/effect equalities as Lean, so the "
            "unlinked-effect control fails through the comparison-record mismatch.",
            "- `Delta_stack` searches independent parameter-only comparisons and compares observed outcomes; "
            "the opposite `DeltaStackEmptyFor` results for `comp_stack_license` and `comp_delta_claimed` are "
            "not special-cased.",
            "- Statuses are derived from branch evidence and carried status records; no status row is copied "
            "directly from the pre-registration table.",
            "",
        ]
    )
    return "\n".join(lines)


def write_results_report(path: Path = DEFAULT_RESULTS_PATH) -> SweepResults:
    results = run_institutional_rewrite_sweep()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(results_markdown(results), encoding="utf-8")
    return results


def main() -> None:
    results = write_results_report()
    print(results_markdown(results))
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
