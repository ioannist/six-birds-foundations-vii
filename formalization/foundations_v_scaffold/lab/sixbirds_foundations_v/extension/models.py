from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from sixbirds_foundations_v._recombination_support.schemas import SixBirdsRecombinationModel


class ExtensionAuditStatus(str, Enum):
    OK = "ok"
    UNSUPPORTED = "unsupported"
    ARTIFACT_CONTEXT_EXCLUDED = "artifact_context_excluded"
    INSUFFICIENT_SUPPORT = "insufficient_support"
    ERROR = "error"


class ExtensionZoneCategory(str, Enum):
    TOY_FACTORABLE = "toy_factorable"
    TOY_OBSTRUCTED_NONFACTORIZABLE = "toy_obstructed_nonfactorizable"
    TOY_MACRO_OBSTRUCTION = "toy_macro_obstruction"
    BENCHMARK_CONTEXT = "benchmark_context"


class BudgetContextStatus(str, Enum):
    AVAILABLE_TICKET14 = "available_ticket14"
    MISSING_TICKET14 = "missing_ticket14"
    NOT_APPLICABLE = "not_applicable"


class ExtensionMoveSpec(SixBirdsRecombinationModel):
    move_id: str
    description: str
    assumption_note: str
    enabled_by_default: bool = True


class ExtensionAuditZone(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-extension-zone.v1"
    zone_id: str
    input_kind: str = "extension_zone"
    zone_category: ExtensionZoneCategory
    source_kind: str
    benchmark_id: str | None = None
    slice_id: str | None = None
    comparison_group: str | None = None
    phase_mode: str | None = None
    strategy_id: str | None = None
    extension_surface_id: str | None = None
    artifact_excluded: bool = False
    artifact_exclusion_reason: str | None = None
    budget_context_status: BudgetContextStatus = BudgetContextStatus.NOT_APPLICABLE
    support_cone_id: str | None = None
    support_refs: dict[str, str] = Field(default_factory=dict)
    upstream_evidence: dict[str, Any] = Field(default_factory=dict)
    baseline_semantics: dict[str, Any] = Field(default_factory=dict)
    move_payloads: dict[str, dict[str, Any]] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ExtensionAuditRow(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-extension-audit-row.v1"
    zone_id: str
    source_kind: str
    extension_move_id: str
    obstruction_check_id: str
    status: ExtensionAuditStatus
    baseline_status: str
    extended_status: str
    obstruction_flag: bool | None = None
    resolution_flag: bool | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class ExtensionAuditBundle(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-extension-audit-bundle.v1"
    zone_id: str
    source_kind: str
    row_count: int
    extension_move_ids: list[str]
    obstruction_check_ids: list[str]
    rows: list[ExtensionAuditRow]
    warnings: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "BudgetContextStatus",
    "ExtensionAuditBundle",
    "ExtensionAuditRow",
    "ExtensionAuditStatus",
    "ExtensionAuditZone",
    "ExtensionMoveSpec",
    "ExtensionZoneCategory",
]
