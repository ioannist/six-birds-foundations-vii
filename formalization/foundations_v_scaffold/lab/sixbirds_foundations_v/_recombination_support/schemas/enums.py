from __future__ import annotations

from enum import Enum


class RecombinationResultManifestVersion(str, Enum):
    V1 = "recombination-result-manifest.v1"


class FrozenSliceConfigVersion(str, Enum):
    V1 = "recombination-frozen-slice-config.v1"
    V2 = "recombination-frozen-slice-config.v2"


class ResultLedgerVersion(str, Enum):
    V1 = "recombination-run-ledger.v1"


class RouteClassificationLedgerVersion(str, Enum):
    V1 = "recombination-route-classification-ledger.v1"


class AuditStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"
    SKIPPED = "skipped"


class RobustnessStatus(str, Enum):
    UNTESTED = "untested"
    PASSED = "passed"
    FAILED = "failed"
    MIXED = "mixed"


class RecombinationGapMetricName(str, Enum):
    EXACT_RECOMBINATION_GAP = "exact_recombination_gap"
    EXACT_BRANCHWISE_L1_GAP = "exact_branchwise_l1_gap"
    EXACT_TERMINAL_TOTAL_VARIATION = "exact_terminal_total_variation"
    EXACT_CONDITIONAL_VISIBILITY_GAP = "exact_conditional_visibility_gap"


class RecombinationClassLabel(str, Enum):
    CLASSICAL_MIXTURE = "classical_mixture"
    MEMORY_ONLY = "memory_only"
    MARKED_SUPPRESSION = "marked_suppression"
    ERASURE_RECOVERY = "erasure_recovery"
    DISSIPATIVE = "dissipative"
    COHERENT_BRANCH_CANDIDATE = "coherent_branch_candidate"
    ARTIFACT = "artifact"
    UNCLASSIFIED = "unclassified"


__all__ = [
    "AuditStatus",
    "FrozenSliceConfigVersion",
    "RecombinationClassLabel",
    "RecombinationGapMetricName",
    "RecombinationResultManifestVersion",
    "ResultLedgerVersion",
    "RobustnessStatus",
    "RouteClassificationLedgerVersion",
]
