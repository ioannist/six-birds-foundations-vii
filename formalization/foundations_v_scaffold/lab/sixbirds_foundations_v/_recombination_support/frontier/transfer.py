from __future__ import annotations

from collections import defaultdict

from .models import ConeEquivalenceClass, FrontierEvaluationResult, FrontierResultRow


def assign_cone_equivalence_classes(
    result: FrontierEvaluationResult,
    *,
    tolerance: float,
) -> FrontierEvaluationResult:
    signature_buckets: dict[tuple, list[FrontierResultRow]] = defaultdict(list)
    for row in result.rows:
        signature_buckets[_cone_signature(row, tolerance=tolerance)].append(row)

    class_rows: list[FrontierResultRow] = []
    classes: list[ConeEquivalenceClass] = []
    for index, signature in enumerate(sorted(signature_buckets, key=str)):
        members = sorted(signature_buckets[signature], key=lambda item: item.candidate_id)
        class_id = f"{result.support_cone_id}.eq{index}"
        transfer_replacement = [member.candidate_id for member in members]
        frontier_transferable = any(member.frontier_member for member in members)
        classes.append(
            ConeEquivalenceClass(
                slice_id=result.slice_id,
                support_cone_id=result.support_cone_id,
                class_id=class_id,
                candidate_ids=transfer_replacement,
                frontier_status_transferable=frontier_transferable,
            )
        )
        for member in members:
            class_rows.append(
                member.model_copy(
                    update={
                        "cone_equivalence_class_id": class_id,
                        "transfer_summary": member.transfer_summary.model_copy(
                            update={
                                "eligible": len(members) > 1,
                                "replacement_candidates": [
                                    candidate_id
                                    for candidate_id in transfer_replacement
                                    if candidate_id != member.candidate_id
                                ],
                                "transfer_reason": (
                                    "cone-equivalent candidate may inherit frontier status on this slice"
                                    if len(members) > 1
                                    else "no cone-equivalent replacement candidates"
                                ),
                            }
                        ),
                    }
                )
            )
    return result.model_copy(update={"rows": class_rows, "cone_equivalence_classes": classes})


def _cone_signature(row: FrontierResultRow, *, tolerance: float) -> tuple:
    yield_signature = tuple(
        (metric_name, _rounded(value, tolerance))
        for metric_name, value in sorted(row.aggregated_yield_vector.items())
    )
    cost_signature = tuple(
        (metric_name, _rounded(value, tolerance))
        for metric_name, value in sorted(row.aggregated_cost_vector.items())
    )
    return (
        row.comparison_status.value,
        yield_signature,
        cost_signature,
    )


def _rounded(value: float, tolerance: float) -> float:
    if tolerance <= 0:
        return float(value)
    return round(float(value) / tolerance) * tolerance


__all__ = ["assign_cone_equivalence_classes"]
