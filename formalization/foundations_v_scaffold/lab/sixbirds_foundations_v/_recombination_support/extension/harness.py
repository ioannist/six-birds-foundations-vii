from __future__ import annotations

from .checks import evaluate_obstruction_check, list_obstruction_check_ids
from .models import ExtensionAuditBundle, ExtensionAuditZone
from .moves import list_extension_move_ids


def run_extension_harness(
    zone: ExtensionAuditZone,
    *,
    extension_move_ids: list[str] | None = None,
    obstruction_check_ids: list[str] | None = None,
) -> ExtensionAuditBundle:
    move_ids = extension_move_ids or list_extension_move_ids()
    check_ids = obstruction_check_ids or list_obstruction_check_ids()
    rows = [
        evaluate_obstruction_check(
            zone,
            extension_move_id=move_id,
            obstruction_check_id=check_id,
        )
        for move_id in move_ids
        for check_id in check_ids
    ]
    return ExtensionAuditBundle(
        zone_id=zone.zone_id,
        source_kind=zone.source_kind,
        row_count=len(rows),
        extension_move_ids=list(move_ids),
        obstruction_check_ids=list(check_ids),
        rows=rows,
        provenance={
            "zone_category": zone.zone_category.value,
            "budget_context_status": zone.budget_context_status.value,
            "extension_surface_id": zone.extension_surface_id,
        },
        warnings=list(zone.warnings),
    )


__all__ = ["run_extension_harness"]
