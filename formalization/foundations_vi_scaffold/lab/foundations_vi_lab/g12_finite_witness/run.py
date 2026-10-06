"""Command-line runner for the G12 finite-witness lab."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path

from foundations_vi_lab.g12_finite_witness.coloring_sat import (
    SolveSummary,
    build_coloring_cnf,
    solve_cnf,
    write_dimacs,
)
from foundations_vi_lab.g12_finite_witness.parsing import load_heule_826
from foundations_vi_lab.g12_finite_witness.unit_distance import (
    UnitDistanceSummary,
    verify_unit_distance_certificate,
)


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_verdict(path: Path, summary: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    unit: dict[str, object] = summary["unit_distance"]  # type: ignore[assignment]
    solve: dict[str, object] | None = summary["solve"]  # type: ignore[assignment]
    solve_status = "SKIPPED" if solve is None else str(solve["status"])
    status = (
        "PASS"
        if len(unit["symbolic_failures"]) == 0  # type: ignore[arg-type]
        and len(unit["numeric_failures"]) == 0  # type: ignore[arg-type]
        and unit["non_edge_unit_hits"] == 0
        and solve_status in {"UNSAT", "SKIPPED"}
        else "FAIL"
    )

    sat_lines = (
        [
            (
                f"SAT solve: `{solve['status']}` using `{solve['solver_name']}` "
                f"in `{solve['elapsed_seconds']:.6f}` seconds."
            )
        ]
        if solve is not None
        else [
            "SAT solve: skipped by `--skip-sat`; this is a fast structural/distance run only."
        ]
    )

    path.write_text(
        "\n".join(
            [
                "# G12-L1 Verdict - Heule 826 Finite Witness",
                "",
                "## Hypothesis",
                (
                    "The vendored Heule/Polymath16 826-vertex graph should be a "
                    "real unit-distance graph and should be non-4-colorable."
                ),
                "",
                "## Outcome",
                f"{status}.",
                (
                    f"Parsed `{summary['vertices']}` vertices and `{summary['edges']}` "
                    "undirected edges from the vendored data."
                ),
                (
                    f"Exact symbolic unit-distance failures: "
                    f"`{len(unit['symbolic_failures'])}`. "
                    f"60-digit numeric failures: `{len(unit['numeric_failures'])}`."
                ),
                (
                    f"Random non-edge sanity check: sampled `{unit['non_edges_sampled']}` "
                    f"non-edges with `{unit['non_edge_unit_hits']}` exact unit-distance hits."
                ),
                (
                    f"4-coloring CNF: `{summary['cnf_variables']}` variables, "
                    f"`{summary['cnf_clauses']}` clauses, written to "
                    f"`{summary['cnf_path']}`."
                ),
                *sat_lines,
                "",
                "## Certificate Scope",
                (
                    "The coordinate and edge portions of `cert_4(W)` are checked here "
                    "in exact algebraic arithmetic. The non-4-colorability portion is "
                    "solver-verified by SAT, not independently proof-checked: this "
                    "826-vertex instance has no public DRAT/resolution certificate in "
                    "Heule's `CNP-SAT` repository, and this lab does not produce or "
                    "verify one. (Smaller graphs in the same repository, e.g. 517/529/"
                    "553/610/633/803 vertices, do have public DRAT certificates; this "
                    "lab does not consume or proof-check those either. See "
                    "`data/PROVENANCE.md` for the corrected provenance record.)"
                ),
                (
                    "This reproduces a known finite-witness lower-bound stream for the "
                    "Hadwiger-Nelson problem. It is not a new chromatic-number result and "
                    "does not claim to use the smallest known 509-vertex Parts graph, whose "
                    "raw coordinates were not found publicly archived."
                ),
                "",
                "## Scope Note",
                (
                    "The full SAT solve is intentionally not part of `pytest tests`; tests "
                    "cover parsing, structural sanity, and exact unit-distance checks. Run "
                    "this CLI without `--skip-sat` to reproduce the solver-verified UNSAT "
                    "determination."
                ),
                "",
                (
                    "Traceability: this lab instantiates "
                    "`SixBirdsFoundationsVI.Laws.G12FiniteWitnessRadiation.FiniteWitnessObstruction` "
                    "for the concrete 826-vertex unit-distance graph at `k=4`. Combined with "
                    "`SixBirdsFoundationsVI.Laws.G12FiniteWitnessRadiation.no_global_k_coloring`, "
                    "the finite witness rules out a proper 4-coloring of the plane, modulo the "
                    "solver-verified UNSAT caveat above."
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_g12_l1(args: argparse.Namespace) -> dict[str, object]:
    """Run G12-L1 and optionally write result artifacts."""

    start = time.perf_counter()
    vertices, edge_data = load_heule_826()
    unit_summary: UnitDistanceSummary = verify_unit_distance_certificate(
        vertices=vertices,
        edges=edge_data.edges,
        non_edge_samples=args.non_edge_samples,
        seed=args.seed,
    )
    cnf = build_coloring_cnf(edge_data.vertex_count, edge_data.edges, colors=4)

    out_dir = args.results_dir / "G12-L1"
    cnf_path = out_dir / "heule_826_4color.cnf"
    if args.write_results:
        write_dimacs(cnf_path, cnf)

    solve_summary: SolveSummary | None = None
    if not args.skip_sat:
        solve_summary = solve_cnf(cnf, solver_name=args.solver)

    elapsed = time.perf_counter() - start
    summary: dict[str, object] = {
        "vertices": len(vertices),
        "edges": len(edge_data.edges),
        "declared_vertices": edge_data.vertex_count,
        "declared_edges": edge_data.declared_edge_count,
        "touched_vertices": len(edge_data.touched_vertices),
        "seed": args.seed,
        "non_edge_samples": args.non_edge_samples,
        "unit_distance": asdict(unit_summary),
        "cnf_variables": cnf.variables,
        "cnf_clauses": len(cnf.clauses),
        "cnf_path": str(cnf_path),
        "solve": None if solve_summary is None else asdict(solve_summary),
        "elapsed_seconds": elapsed,
    }
    if args.write_results:
        _write_json(out_dir / "run.json", summary)
        _write_verdict(out_dir / "verdict.md", summary)

    solve_status = "SKIPPED" if solve_summary is None else solve_summary.status
    solve_seconds = 0.0 if solve_summary is None else solve_summary.elapsed_seconds
    print(
        "G12-L1 "
        f"{solve_status}: vertices={len(vertices)} edges={len(edge_data.edges)} "
        f"symbolic_failures={len(unit_summary.symbolic_failures)} "
        f"numeric_failures={len(unit_summary.numeric_failures)} "
        f"nonedge_unit_hits={unit_summary.non_edge_unit_hits} "
        f"cnf_vars={cnf.variables} cnf_clauses={len(cnf.clauses)} "
        f"solver={args.solver if not args.skip_sat else 'none'} "
        f"solve_seconds={solve_seconds:.6f} total_seconds={elapsed:.6f}"
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """Build the G12-L1 CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=12)
    parser.add_argument("--non-edge-samples", type=int, default=2_000)
    parser.add_argument("--solver", default="g3")
    parser.add_argument("--skip-sat", action="store_true")
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--write-results", action="store_true")
    parser.set_defaults(func=run_g12_l1)
    return parser


def main() -> None:
    """Run G12-L1."""

    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
