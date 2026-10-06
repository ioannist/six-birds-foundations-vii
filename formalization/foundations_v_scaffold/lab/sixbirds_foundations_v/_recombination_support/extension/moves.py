from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import ExtensionAuditZone, ExtensionMoveSpec


REWRITE_EFFECTIVE_OPERATOR = "rewrite_effective_operator"
ENLARGE_OBSERVABLE_FAMILY = "enlarge_observable_family"
NEW_OBJECT_MAP = "new_object_map"

DEFAULT_EXTENSION_MOVES_PATH = (
    Path(__file__).resolve().parents[3]
    / "configs"
    / "recombination"
    / "extensions"
    / "default_extension_moves.json"
)

EXTENSION_MOVE_REGISTRY: dict[str, ExtensionMoveSpec] = {
    REWRITE_EFFECTIVE_OPERATOR: ExtensionMoveSpec(
        move_id=REWRITE_EFFECTIVE_OPERATOR,
        description="Replace the coarse effective update law with an explicit rewritten update on the same support.",
        assumption_note="Current scope treats this as a finite exact override of the successor law on the selected zone.",
    ),
    ENLARGE_OBSERVABLE_FAMILY: ExtensionMoveSpec(
        move_id=ENLARGE_OBSERVABLE_FAMILY,
        description="Add extra observable coordinates so previously hidden distinctions become explicit.",
        assumption_note="Current scope treats this as a finite exact replacement of the observable-signature map on the selected zone.",
    ),
    NEW_OBJECT_MAP: ExtensionMoveSpec(
        move_id=NEW_OBJECT_MAP,
        description="Replace the baseline coarse object map with a deeper map on the same support.",
        assumption_note="Current scope treats this as an exact finite repartition of the selected support atoms.",
    ),
}


def list_extension_move_ids() -> list[str]:
    return list(EXTENSION_MOVE_REGISTRY)


def get_extension_move_spec(move_id: str) -> ExtensionMoveSpec:
    return EXTENSION_MOVE_REGISTRY[move_id]


def extension_move_registry_payload() -> dict[str, Any]:
    return {
        "schema_version": "recombination-default-extension-moves.v1",
        "note": "This registry file is a project config artifact, not a Ticket 2 canonical schema kind.",
        "moves": [
            EXTENSION_MOVE_REGISTRY[move_id].model_dump(mode="json")
            for move_id in sorted(EXTENSION_MOVE_REGISTRY)
        ],
    }


def apply_extension_move(zone: ExtensionAuditZone, move_id: str) -> tuple[dict[str, Any] | None, list[str]]:
    if move_id not in zone.move_payloads:
        return None, [f"zone does not declare payload for extension move {move_id!r}"]
    baseline = dict(zone.baseline_semantics)
    payload = zone.move_payloads[move_id]
    merged = dict(baseline)
    merged.update(payload)
    return merged, []


__all__ = [
    "DEFAULT_EXTENSION_MOVES_PATH",
    "ENLARGE_OBSERVABLE_FAMILY",
    "EXTENSION_MOVE_REGISTRY",
    "NEW_OBJECT_MAP",
    "REWRITE_EFFECTIVE_OPERATOR",
    "apply_extension_move",
    "extension_move_registry_payload",
    "get_extension_move_spec",
    "list_extension_move_ids",
]
