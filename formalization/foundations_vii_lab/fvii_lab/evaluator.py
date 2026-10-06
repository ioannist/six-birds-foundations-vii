from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class DerivedFacts:
    contact: bool
    strict_join: bool
    directionality: bool
    reachable: bool
    occurred: bool
    first_extension: bool
    prospective_credit: bool
    certified_noninteraction: bool
    bridge_valid: bool
    endogenous: bool
    new_residual: bool
    holonomy: bool

    def as_mapping(self) -> dict[str, bool]:
        return asdict(self)


def _flag(flags: Mapping[str, bool], name: str) -> bool:
    return bool(flags.get(name, False))


def derive(flags: Mapping[str, bool]) -> DerivedFacts:
    """Compute typed observable facts from one finite world description.

    This evaluator is independent source code from the Lean evaluator.  They
    share only the frozen fixture contract and the mathematical specification.
    """
    contact = _flag(flags, "contact")
    strict_join = all(
        (
            contact,
            _flag(flags, "source_independent"),
            _flag(flags, "composite"),
            _flag(flags, "retention"),
            _flag(flags, "anti_product"),
            _flag(flags, "budget_ok"),
            not _flag(flags, "scheduling_only"),
            not _flag(flags, "relabel_only"),
        )
    )
    occurred = _flag(flags, "fired")
    return DerivedFacts(
        contact=contact,
        strict_join=strict_join,
        directionality=_flag(flags, "drive"),
        reachable=_flag(flags, "reachable"),
        occurred=occurred,
        first_extension=all(
            (
                _flag(flags, "seed"),
                _flag(flags, "generator_reachable"),
                occurred,
            )
        ),
        prospective_credit=(
            _flag(flags, "prospective") and not _flag(flags, "retrospective")
        ),
        certified_noninteraction=(
            not contact
            and _flag(flags, "closed_family")
            and _flag(flags, "detector_power")
        ),
        bridge_valid=not (
            _flag(flags, "total_lens_only") and _flag(flags, "partial_domain")
        ),
        endogenous=(
            _flag(flags, "generator_reachable")
            and occurred
            and not _flag(flags, "observer_used")
            and not _flag(flags, "seed")
        ),
        new_residual=_flag(flags, "new_residual"),
        holonomy=_flag(flags, "holonomy"),
    )


def classify(flags: Mapping[str, bool], facts: DerivedFacts) -> str:
    context_markers = (
        facts.contact,
        _flag(flags, "compatible"),
        _flag(flags, "closed_family"),
        _flag(flags, "sound"),
        _flag(flags, "prospective"),
        _flag(flags, "retrospective"),
        _flag(flags, "observer_used"),
        _flag(flags, "total_lens_only"),
        _flag(flags, "parent_refined"),
    )
    ordered_rules: tuple[tuple[bool, str], ...] = (
        (
            not _flag(flags, "seed")
            and not _flag(flags, "generator_reachable")
            and not any(context_markers),
            "BOOTSTRAP_BLOCKED",
        ),
        (_flag(flags, "retrospective"), "RETROSPECTIVE_SELF_CERTIFICATION_REJECTED"),
        (
            _flag(flags, "observer_used") and not _flag(flags, "observer_priced"),
            "UNPRICED_OBSERVER",
        ),
        (
            _flag(flags, "total_lens_only") and _flag(flags, "partial_domain"),
            "UNLICENSED_TOTALITY_TRANSFER",
        ),
        (
            _flag(flags, "holonomy")
            and not _flag(flags, "drive")
            and not _flag(flags, "order_residue"),
            "HOLONOMY_ZERO_ARROW",
        ),
        (_flag(flags, "drive"), "DRIVEN_ARROW"),
        (_flag(flags, "order_residue"), "ORDER_RESIDUE"),
        (
            _flag(flags, "sound") and not _flag(flags, "reachable"),
            "SOUND_UNREACHABLE",
        ),
        (
            _flag(flags, "reachable") and not _flag(flags, "fired"),
            "REACHABLE_NONOCCURRENT",
        ),
        (
            _flag(flags, "sound")
            and _flag(flags, "reachable")
            and _flag(flags, "fired"),
            "OCCURRENT_EVENT",
        ),
        (
            _flag(flags, "parent_refined") and _flag(flags, "join_destroyed"),
            "REFINEMENT_DESTROYS_JOIN",
        ),
        (facts.certified_noninteraction, "CERTIFIED_NONINTERACTION"),
        (
            not facts.contact and _flag(flags, "compatible"),
            "NO_EVIDENCED_CONTACT",
        ),
        (_flag(flags, "scheduling_only"), "FAKE_JOIN_SCHEDULING"),
        (_flag(flags, "relabel_only"), "FAKE_JOIN_RELABELING"),
        (
            facts.contact
            and _flag(flags, "same_source")
            and _flag(flags, "resemblance_only"),
            "INDEPENDENCE_GATE_FAILED",
        ),
        (
            facts.contact and not _flag(flags, "composite"),
            "CONTACT_WITHOUT_JOIN",
        ),
        (
            facts.contact
            and _flag(flags, "common_refinement")
            and not _flag(flags, "anti_product"),
            "COMMON_REFINEMENT_NONSTRICT",
        ),
        (
            facts.contact
            and _flag(flags, "composite")
            and not _flag(flags, "retention"),
            "RETENTION_OBSTRUCTION",
        ),
        (
            facts.contact
            and _flag(flags, "composite")
            and _flag(flags, "anti_product")
            and not _flag(flags, "budget_ok"),
            "BUDGET_OBSTRUCTION",
        ),
        (
            facts.contact
            and _flag(flags, "composite")
            and _flag(flags, "anti_product")
            and not _flag(flags, "source_independent"),
            "SOURCE_OBSTRUCTION",
        ),
        (facts.strict_join, "STRICT_JOIN"),
        (facts.prospective_credit, "PROSPECTIVE_ADMISSION"),
        (facts.first_extension, "LAWFUL_FIRST_EXTENSION"),
    )
    for condition, status in ordered_rules:
        if condition:
            return status
    return "UNCLASSIFIED"


def evaluate(flags: Mapping[str, bool]) -> tuple[str, DerivedFacts]:
    facts = derive(flags)
    return classify(flags, facts), facts
