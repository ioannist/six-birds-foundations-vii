"""Reflexive SBT package copied from six-birds-meta/experiments/src/reflexive_sbt.

This package is a scaffold for upcoming Reflexive SBT experiments and reports.
"""

from .audits import audit_dictionary, audit_routes, audit_subspace
from .closure import (
    closure_AL,
    closure_feasibility,
    closure_routes,
    closure_symmetry,
    evaluate_all_closures,
)
from .meta_moves import (
    canonicalize_dictionary,
    gate_coherent_pairs,
    merge_routes_into_artifact,
    split_near_duplicate_pairs,
    symmetrize_subspace_via_projector,
)
from .addressability_score import (
    compute_addressability_scores,
    compute_cancel_score,
    compute_sym_score,
)
from .diagnostics import (
    column_space_basis_svd,
    eig_gap_stats,
    near_duplicate_pairs,
    principal_angles,
)

__all__ = [
    "audit_subspace",
    "audit_dictionary",
    "audit_routes",
    "closure_symmetry",
    "closure_feasibility",
    "closure_routes",
    "closure_AL",
    "evaluate_all_closures",
    "symmetrize_subspace_via_projector",
    "canonicalize_dictionary",
    "gate_coherent_pairs",
    "merge_routes_into_artifact",
    "split_near_duplicate_pairs",
    "compute_sym_score",
    "compute_cancel_score",
    "compute_addressability_scores",
    "column_space_basis_svd",
    "near_duplicate_pairs",
    "principal_angles",
    "eig_gap_stats",
]
