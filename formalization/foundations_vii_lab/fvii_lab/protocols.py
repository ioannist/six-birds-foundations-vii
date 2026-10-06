from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

BRIDGE_DISPOSITIONS = {"PROPOSED", "ACCEPTED", "FAILED", "WITHDRAWN"}
CLAIM_GRADES = {"THEOREM", "COROLLARY", "SCHEMA", "CALIBRATION", "CONJECTURE", "PHILOSOPHY", "NONCLAIM"}
EVIDENCE_GRADES = {
    "NONE", "EXECUTABLE_EXAMPLE", "BOUNDED_SEARCH", "EXHAUSTIVE_FINITE_LEAN",
    "EXHAUSTIVE_FINITE_EXTERNAL", "CALIBRATION_DATA", "THEOREM_BACKED",
}
NEGATIVE_GRADES = {"POINT_NULL", "BOUNDED_SEARCH", "EXHAUSTIVE_CLOSED_FINITE", "THEOREM_IMPOSSIBILITY"}
NEGATIVE_SCOPES = {"ONE_INSTANCE", "BOUNDED_FAMILY", "CLOSED_FINITE_FAMILY", "UNRESTRICTED_UNDER_HYPOTHESES"}
_SCOPE_RANK = {
    "ONE_INSTANCE": 0,
    "BOUNDED_FAMILY": 1,
    "CLOSED_FINITE_FAMILY": 2,
    "UNRESTRICTED_UNDER_HYPOTHESES": 3,
}
_MAX_SCOPE = {
    "POINT_NULL": "ONE_INSTANCE",
    "BOUNDED_SEARCH": "BOUNDED_FAMILY",
    "EXHAUSTIVE_CLOSED_FINITE": "CLOSED_FINITE_FAMILY",
    "THEOREM_IMPOSSIBILITY": "UNRESTRICTED_UNDER_HYPOTHESES",
}


def append_only_extends(old: Sequence[Mapping[str, Any]], new: Sequence[Mapping[str, Any]]) -> bool:
    """True exactly when `old` is a prefix of `new`.

    Prefix extension, rather than set inclusion, preserves order and duplicate
    records.  This is the finite-lab counterpart of the Lean ledger relation.
    """
    return len(new) >= len(old) and list(new[: len(old)]) == list(old)


def bridge_well_formed(record: Mapping[str, Any]) -> bool:
    required_text = (
        "source_declaration", "target_declaration", "source_type", "target_type",
        "source_map", "target_map",
    )
    explicit_list_fields = (
        "preserved_hypotheses", "added_hypotheses", "lost_hypotheses",
        "trust_dependencies",
    )
    return (
        all(isinstance(record.get(key), str) and bool(record[key]) for key in required_text)
        and all(isinstance(record.get(key), list) for key in explicit_list_fields)
        and isinstance(record.get("nonclaims"), list)
        and bool(record["nonclaims"])
        and record.get("disposition") in BRIDGE_DISPOSITIONS
        and isinstance(record.get("audit"), list)
        and bool(record["audit"])
    )


def transport_licensed(kind: str, record: Mapping[str, Any] | None = None) -> bool:
    if kind == "CITATION_ONLY":
        return False
    if kind != "CERTIFIED_BRIDGE" or record is None:
        return False
    return bridge_well_formed(record) and record.get("disposition") == "ACCEPTED"


def negative_licenses(
    grade: str,
    declared_scope: str,
    requested_scope: str,
    *,
    family_closed: bool,
) -> bool:
    if grade not in NEGATIVE_GRADES or declared_scope not in NEGATIVE_SCOPES or requested_scope not in NEGATIVE_SCOPES:
        return False
    if grade == "EXHAUSTIVE_CLOSED_FINITE" and not family_closed:
        return False
    return (
        _SCOPE_RANK[requested_scope] <= _SCOPE_RANK[declared_scope]
        and _SCOPE_RANK[requested_scope] <= _SCOPE_RANK[_MAX_SCOPE[grade]]
    )


def science_asset_grade_faithful(record: Mapping[str, Any]) -> bool:
    claim_grade = record.get("claim_grade")
    evidence_grade = record.get("evidence_grade")
    specification_kind = record.get("specification_kind")
    if claim_grade not in CLAIM_GRADES or evidence_grade not in EVIDENCE_GRADES:
        return False
    if claim_grade in {"THEOREM", "COROLLARY"} and not record.get("formal_declaration"):
        return False
    if evidence_grade == "EXHAUSTIVE_FINITE_EXTERNAL" and claim_grade in {"THEOREM", "COROLLARY"}:
        return False
    if specification_kind == "NORMATIVE" and not record.get("normative_specification"):
        return False
    return bool(record.get("nonclaims")) and bool(record.get("audit"))


@dataclass(frozen=True, slots=True)
class DetectorContract:
    signal_case_ids: tuple[str, ...]
    null_case_ids: tuple[str, ...]
    falsifier_case_ids: tuple[str, ...]
    same_source_controls: tuple[str, ...]
    no_contact_controls: tuple[str, ...]
    scheduling_controls: tuple[str, ...]
    relabeling_controls: tuple[str, ...]
    frozen_scenario_ids: tuple[str, ...]
    frozen_countermodel_ids: tuple[str, ...]
    false_positive_cost: int
    false_negative_cost: int

    def well_formed(self) -> bool:
        nonempty = (
            self.signal_case_ids, self.null_case_ids, self.falsifier_case_ids,
            self.same_source_controls, self.no_contact_controls,
            self.scheduling_controls, self.relabeling_controls,
            self.frozen_scenario_ids, self.frozen_countermodel_ids,
        )
        frozen = set(self.frozen_scenario_ids) | set(self.frozen_countermodel_ids)
        controlled = (
            self.signal_case_ids, self.null_case_ids, self.falsifier_case_ids,
            self.same_source_controls, self.no_contact_controls,
            self.scheduling_controls, self.relabeling_controls,
        )
        return (
            all(nonempty)
            and len(set(self.frozen_scenario_ids)) == len(self.frozen_scenario_ids)
            and len(set(self.frozen_countermodel_ids)) == len(self.frozen_countermodel_ids)
            and self.false_positive_cost > self.false_negative_cost >= 0
            and all(set(case_ids) <= frozen for case_ids in controlled)
            and set(self.signal_case_ids) <= set(self.frozen_scenario_ids)
            and set(self.null_case_ids) <= set(self.frozen_scenario_ids)
            and set(self.falsifier_case_ids) <= set(self.frozen_countermodel_ids)
        )


def phase1_detector_contract(scenario_ids: Sequence[str], countermodel_ids: Sequence[str]) -> DetectorContract:
    return DetectorContract(
        signal_case_ids=("TTW-S01", "TTW-S08", "TTW-S21"),
        null_case_ids=("TTW-S02", "TTW-S06", "TTW-S12", "TTW-S19", "TTW-S20"),
        falsifier_case_ids=tuple(countermodel_ids),
        same_source_controls=("TTW-S05", "CM-01", "CM-26"),
        no_contact_controls=("TTW-S12", "TTW-S13", "CM-02", "CM-27"),
        scheduling_controls=("TTW-S14", "CM-04"),
        relabeling_controls=("TTW-S15", "CM-16"),
        frozen_scenario_ids=tuple(scenario_ids),
        frozen_countermodel_ids=tuple(countermodel_ids),
        false_positive_cost=10,
        false_negative_cost=1,
    )
