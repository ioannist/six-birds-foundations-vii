from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .framework import CompletionFamilyId, CompletionSourceKind
from .strategies import (
    CompletionStrategy,
    completion_preserving_strategy,
    control_matched_strategy,
    identity_reference_strategy,
    max_weight_representative_strategy,
    predictive_signature_canonical_strategy,
)


@dataclass(frozen=True)
class CompletionStrategySpec:
    strategy_id: str
    description: str
    supported_source_kinds: tuple[CompletionSourceKind, ...]
    deterministic: bool
    parameter_note: str
    enabled_by_default: bool
    default_tie_break_rule: str
    weight_source: str | None
    feature_basis: str | None
    strategy: CompletionStrategy

    def export_payload(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "description": self.description,
            "supported_source_kinds": [kind.value for kind in self.supported_source_kinds],
            "deterministic": self.deterministic,
            "parameter_note": self.parameter_note,
            "enabled_by_default": self.enabled_by_default,
        }


@dataclass(frozen=True)
class CompletionFamilySpec:
    family_id: CompletionFamilyId
    description: str
    parameter_note: str
    enabled_by_default: bool

    def export_payload(self) -> dict[str, Any]:
        return {
            "family_id": self.family_id.value,
            "description": self.description,
            "parameter_note": self.parameter_note,
            "enabled_by_default": self.enabled_by_default,
        }


DEFAULT_STRATEGY_REGISTRY_PATH = (
    Path(__file__).resolve().parents[3]
    / "configs"
    / "recombination"
    / "completion"
    / "default_strategy_registry.json"
)
DEFAULT_FAMILY_REGISTRY_PATH = (
    Path(__file__).resolve().parents[3]
    / "configs"
    / "recombination"
    / "completion"
    / "default_family_registry.json"
)

ALL_SOURCE_KINDS = tuple(CompletionSourceKind)
ASSEMBLAGE_SOURCE_KINDS = (
    CompletionSourceKind.BRANCHWISE_QUOTIENT,
    CompletionSourceKind.RECOMBINATION_QUOTIENT,
)

COMPLETION_STRATEGIES: dict[str, CompletionStrategySpec] = {
    "identity_reference": CompletionStrategySpec(
        strategy_id="identity_reference",
        description="Use the canonical representative already exposed by the source quotient/carrier result.",
        supported_source_kinds=ALL_SOURCE_KINDS,
        deterministic=True,
        parameter_note="No parameters.",
        enabled_by_default=True,
        default_tie_break_rule="source result representative",
        weight_source=None,
        feature_basis="source representative labels",
        strategy=identity_reference_strategy,
    ),
    "max_weight_representative": CompletionStrategySpec(
        strategy_id="max_weight_representative",
        description="Choose the candidate with the largest available branch-member weight; break ties deterministically.",
        supported_source_kinds=ASSEMBLAGE_SOURCE_KINDS,
        deterministic=True,
        parameter_note="Requires assemblage-backed source kinds with per-member branch weights.",
        enabled_by_default=True,
        default_tie_break_rule="maximize max_member_weight, then total_weight, then candidate_id",
        weight_source="branch assemblage member weights",
        feature_basis="max branch weight within each candidate assemblage",
        strategy=max_weight_representative_strategy,
    ),
    "predictive_signature_canonical": CompletionStrategySpec(
        strategy_id="predictive_signature_canonical",
        description="Choose a canonical representative from the richest lower-state predictive decomposition, then lexical signature order.",
        supported_source_kinds=ALL_SOURCE_KINDS,
        deterministic=True,
        parameter_note="No parameters in Ticket 8; canonicalization uses predictive-signature-derived candidate features.",
        enabled_by_default=True,
        default_tie_break_rule="prefer richer predictive decomposition, then canonical signature, then candidate_id",
        weight_source=None,
        feature_basis="predictive lower-state signature keys",
        strategy=predictive_signature_canonical_strategy,
    ),
    "completion_preserving": CompletionStrategySpec(
        strategy_id="completion_preserving",
        description="Prefer representatives that preserve paired completion/flattening structure when an explicit partner reference is available; fallback stays explicit.",
        supported_source_kinds=ASSEMBLAGE_SOURCE_KINDS,
        deterministic=True,
        parameter_note="Ticket27 smoke prepares paired flattening/completion partner references explicitly; fallback is machine-readable when the signal is absent.",
        enabled_by_default=True,
        default_tie_break_rule="prefer exact normalized paired-partner signature match, then richer predictive decomposition, then max_member_weight, then canonical signature, then candidate_id",
        weight_source="paired completion/flattening partner reference plus candidate branch-member weights",
        feature_basis="normalized paired observable signature and predictive decomposition richness",
        strategy=completion_preserving_strategy,
    ),
    "control_matched": CompletionStrategySpec(
        strategy_id="control_matched",
        description="Prefer representatives that best align with an explicit matched-control reference surface on deterministic candidate features; fallback stays explicit.",
        supported_source_kinds=ASSEMBLAGE_SOURCE_KINDS,
        deterministic=True,
        parameter_note="Ticket27 smoke prepares matched-control class references explicitly; fallback is machine-readable when the signal is absent.",
        enabled_by_default=True,
        default_tie_break_rule="minimize branch_member_count distance to matched control, then max_member_weight distance, then canonical predictive signature, then candidate_id",
        weight_source="matched-control reference branch counts and candidate branch-member weights",
        feature_basis="matched-control branch profile alignment",
        strategy=control_matched_strategy,
    ),
}

COMPLETION_FAMILIES: dict[CompletionFamilyId, CompletionFamilySpec] = {
    CompletionFamilyId.DECLARED_COMPLETION_FAMILY: CompletionFamilySpec(
        family_id=CompletionFamilyId.DECLARED_COMPLETION_FAMILY,
        description="Use the benchmark's declared continuation and observable families unchanged.",
        parameter_note="No parameters.",
        enabled_by_default=True,
    ),
    CompletionFamilyId.REACHABLE_CONTINUATION_EXPANSION: CompletionFamilySpec(
        family_id=CompletionFamilyId.REACHABLE_CONTINUATION_EXPANSION,
        description="Expand the lawful continuation surface by exact finite continuation compositions induced by the declared generator family.",
        parameter_note="No parameters in Ticket 9.1; exact continuation closure is used when it stabilizes within the current finite bound.",
        enabled_by_default=True,
    ),
    CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT: CompletionFamilySpec(
        family_id=CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT,
        description="Use the declared observable family enriched by the lawful paired flattening/completion partner observable family.",
        parameter_note="Supported only on benchmarks with paired flattening/control metadata.",
        enabled_by_default=True,
    ),
}


def get_strategy_spec(strategy_id: str) -> CompletionStrategySpec:
    return COMPLETION_STRATEGIES[strategy_id]


def list_strategy_specs() -> list[CompletionStrategySpec]:
    return [COMPLETION_STRATEGIES[strategy_id] for strategy_id in sorted(COMPLETION_STRATEGIES)]


def get_family_spec(family_id: CompletionFamilyId | str) -> CompletionFamilySpec:
    normalized = CompletionFamilyId(family_id)
    return COMPLETION_FAMILIES[normalized]


def list_family_specs() -> list[CompletionFamilySpec]:
    return [COMPLETION_FAMILIES[family_id] for family_id in CompletionFamilyId]


def completion_strategy_registry_payload() -> dict[str, Any]:
    return {
        "schema_version": "recombination-default-completion-strategy-registry.v1",
        "ticket_scope": "live_completion_registry",
        "note": "This registry file is a project config artifact, not a Ticket 2 canonical schema kind.",
        "strategies": [
            spec.export_payload()
            for spec in list_strategy_specs()
        ],
    }


def completion_family_registry_payload() -> dict[str, Any]:
    return {
        "schema_version": "recombination-default-completion-family-registry.v1",
        "ticket_scope": "ticket9.1",
        "note": "This registry file is a project config artifact, not a Ticket 2 canonical schema kind.",
        "families": [
            spec.export_payload()
            for spec in list_family_specs()
        ],
    }


__all__ = [
    "COMPLETION_FAMILIES",
    "COMPLETION_STRATEGIES",
    "DEFAULT_FAMILY_REGISTRY_PATH",
    "DEFAULT_STRATEGY_REGISTRY_PATH",
    "CompletionFamilySpec",
    "CompletionStrategySpec",
    "completion_family_registry_payload",
    "completion_strategy_registry_payload",
    "get_family_spec",
    "get_strategy_spec",
    "list_family_specs",
    "list_strategy_specs",
]
