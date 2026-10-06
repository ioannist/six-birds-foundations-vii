"""Exact unit-distance verification for the G12 finite witness."""

from __future__ import annotations

import random
from dataclasses import dataclass

import sympy as sp

from foundations_vi_lab.g12_finite_witness.parsing import Edge, Vertex


@dataclass(frozen=True)
class UnitDistanceSummary:
    """Summary of symbolic/numeric unit-distance checks."""

    edges_checked: int
    symbolic_failures: tuple[tuple[int, int, str], ...]
    numeric_failures: tuple[tuple[int, int, str], ...]
    non_edges_sampled: int
    non_edge_unit_hits: int
    non_edge_unit_examples: tuple[Edge, ...]


def squared_distance(vertices: tuple[Vertex, ...], edge: Edge) -> sp.Expr:
    """Compute exact squared Euclidean distance for a 1-indexed edge."""

    i, j = edge
    xi, yi = vertices[i - 1]
    xj, yj = vertices[j - 1]
    dx = sp.expand(xi - xj)
    dy = sp.expand(yi - yj)
    return sp.simplify(sp.radsimp(sp.expand(dx * dx + dy * dy)))


def verify_edge_unit_distances(
    vertices: tuple[Vertex, ...],
    edges: tuple[Edge, ...],
    numeric_precision: int = 60,
    numeric_tolerance: str = "1e-50",
) -> tuple[tuple[tuple[int, int, str], ...], tuple[tuple[int, int, str], ...]]:
    """Verify all declared edges have exact and numeric squared distance `1`."""

    symbolic_failures: list[tuple[int, int, str]] = []
    numeric_failures: list[tuple[int, int, str]] = []
    tolerance = sp.Float(numeric_tolerance, numeric_precision)
    for edge in edges:
        d2 = squared_distance(vertices, edge)
        if d2 != 1:
            symbolic_failures.append((edge[0], edge[1], str(d2)))
        numeric_error = abs(sp.N(d2 - 1, numeric_precision))
        if numeric_error >= tolerance:
            numeric_failures.append((edge[0], edge[1], str(numeric_error)))
    return tuple(symbolic_failures), tuple(numeric_failures)


def sample_non_edges(
    vertex_count: int,
    edges: tuple[Edge, ...],
    sample_size: int,
    seed: int,
) -> tuple[Edge, ...]:
    """Sample distinct non-edge pairs from the complete graph."""

    rng = random.Random(seed)
    edge_set = set(edges)
    samples: set[Edge] = set()
    while len(samples) < sample_size:
        i = rng.randint(1, vertex_count)
        j = rng.randint(1, vertex_count)
        if i == j:
            continue
        edge = (i, j) if i < j else (j, i)
        if edge in edge_set or edge in samples:
            continue
        samples.add(edge)
    return tuple(sorted(samples))


def verify_non_edges_not_unit(
    vertices: tuple[Vertex, ...],
    edges: tuple[Edge, ...],
    sample_size: int = 1_000,
    seed: int = 12,
) -> tuple[int, tuple[Edge, ...]]:
    """Sample non-edges and count exact accidental unit distances."""

    samples = sample_non_edges(len(vertices), edges, sample_size, seed)
    unit_hits: list[Edge] = []
    for edge in samples:
        if squared_distance(vertices, edge) == 1:
            unit_hits.append(edge)
    return len(samples), tuple(unit_hits)


def verify_unit_distance_certificate(
    vertices: tuple[Vertex, ...],
    edges: tuple[Edge, ...],
    non_edge_samples: int = 1_000,
    seed: int = 12,
) -> UnitDistanceSummary:
    """Run the full fast unit-distance certificate checks."""

    symbolic_failures, numeric_failures = verify_edge_unit_distances(vertices, edges)
    sampled, unit_hits = verify_non_edges_not_unit(
        vertices=vertices,
        edges=edges,
        sample_size=non_edge_samples,
        seed=seed,
    )
    return UnitDistanceSummary(
        edges_checked=len(edges),
        symbolic_failures=symbolic_failures,
        numeric_failures=numeric_failures,
        non_edges_sampled=sampled,
        non_edge_unit_hits=len(unit_hits),
        non_edge_unit_examples=unit_hits[:20],
    )
