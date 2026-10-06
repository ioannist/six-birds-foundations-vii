from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from sixbirds_foundations_v._holonomy_support.schemas.manifests import BenchmarkManifest
from sixbirds_foundations_v._holonomy_support.schemas.transport import RouteTransportPackageConfig
from pydantic import BaseModel

from .configs import BenchmarkRunConfig, FrozenSliceConfig, SearchRunConfig
from .ledgers import (
    ResultLedger,
    RouteClassificationLedger,
)
from .results import RecombinationResultManifest


REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_SCHEMA_ROOT = REPO_ROOT / "schemas" / "recombination"
COMPATIBILITY_RESULT_SCHEMA_PATH = (
    REPO_ROOT / "src" / "sixbirds_foundations_v._recombination_support" / "schemas" / "recombination_result.schema.json"
)


@dataclass(frozen=True)
class SchemaSpec:
    kind: str
    model: type[BaseModel]
    canonical_path: Path
    origin: str
    compatibility_paths: tuple[Path, ...] = ()


SCHEMA_SPECS: tuple[SchemaSpec, ...] = (
    SchemaSpec(
        kind="benchmark-manifest",
        model=BenchmarkManifest,
        canonical_path=CANONICAL_SCHEMA_ROOT / "inherited" / "benchmark_manifest.schema.json",
        origin="inherited",
    ),
    SchemaSpec(
        kind="route-transport-package",
        model=RouteTransportPackageConfig,
        canonical_path=CANONICAL_SCHEMA_ROOT / "inherited" / "route_transport_package.schema.json",
        origin="inherited",
    ),
    SchemaSpec(
        kind="benchmark-run-config",
        model=BenchmarkRunConfig,
        canonical_path=CANONICAL_SCHEMA_ROOT / "benchmark_run_config.schema.json",
        origin="local",
    ),
    SchemaSpec(
        kind="search-run-config",
        model=SearchRunConfig,
        canonical_path=CANONICAL_SCHEMA_ROOT / "search_run_config.schema.json",
        origin="local",
    ),
    SchemaSpec(
        kind="frozen-slice",
        model=FrozenSliceConfig,
        canonical_path=CANONICAL_SCHEMA_ROOT / "frozen_slice_config.schema.json",
        origin="local",
    ),
    SchemaSpec(
        kind="result-manifest",
        model=RecombinationResultManifest,
        canonical_path=CANONICAL_SCHEMA_ROOT / "result_manifest.schema.json",
        origin="local",
        compatibility_paths=(COMPATIBILITY_RESULT_SCHEMA_PATH,),
    ),
    SchemaSpec(
        kind="result-ledger",
        model=ResultLedger,
        canonical_path=CANONICAL_SCHEMA_ROOT / "result_ledger.schema.json",
        origin="local",
    ),
    SchemaSpec(
        kind="route-classification-ledger",
        model=RouteClassificationLedger,
        canonical_path=CANONICAL_SCHEMA_ROOT / "route_classification_ledger.schema.json",
        origin="local",
    ),
)

SCHEMA_SPEC_BY_KIND = {spec.kind: spec for spec in SCHEMA_SPECS}
LOCAL_SCHEMA_KINDS = tuple(
    spec.kind for spec in SCHEMA_SPECS if spec.origin == "local"
)
INHERITED_SCHEMA_KINDS = tuple(
    spec.kind for spec in SCHEMA_SPECS if spec.origin == "inherited"
)


def _repo_relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def schema_inventory() -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for spec in SCHEMA_SPECS:
        inventory.append(
            {
                "kind": spec.kind,
                "origin": spec.origin,
                "model": spec.model.__name__,
                "canonical_schema_path": _repo_relative(spec.canonical_path),
                "compatibility_paths": [
                    _repo_relative(path) for path in spec.compatibility_paths
                ],
            }
        )
    return inventory


def export_schema(kind: str, *, include_compatibility_copies: bool = True) -> Path:
    spec = SCHEMA_SPEC_BY_KIND[kind]
    payload = spec.model.model_json_schema(mode="validation")
    _write_json(spec.canonical_path, payload)
    if include_compatibility_copies:
        for compat_path in spec.compatibility_paths:
            _write_json(compat_path, payload)
    return spec.canonical_path


def export_all_schemas(*, include_compatibility_copies: bool = True) -> list[Path]:
    return [
        export_schema(spec.kind, include_compatibility_copies=include_compatibility_copies)
        for spec in SCHEMA_SPECS
    ]


def validate_artifact(kind: str, path: str | Path) -> BaseModel:
    spec = SCHEMA_SPEC_BY_KIND[kind]
    if kind in {"benchmark-run-config", "search-run-config"}:
        from sixbirds_foundations_v._recombination_support.runner import load_run_config, validate_run_config

        return validate_run_config(load_run_config(path))
    if kind == "frozen-slice":
        from sixbirds_foundations_v._recombination_support.frontier import validate_frozen_slice_metric_names

        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        validated = spec.model.model_validate(payload)
        validate_frozen_slice_metric_names(validated)
        return validated
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return spec.model.model_validate(payload)


def validate_artifact_summary(kind: str, path: str | Path) -> dict[str, Any]:
    validated = validate_artifact(kind, path)
    schema_version = getattr(validated, "schema_version", None)
    if hasattr(schema_version, "value"):
        schema_version = schema_version.value
    return {
        "kind": kind,
        "path": _repo_relative(Path(path).resolve()),
        "schema_version": schema_version,
        "validated": True,
    }


def main_export(argv: Iterable[str] | None = None) -> int:
    for path in export_all_schemas():
        print(_repo_relative(path))
    return 0


def main_validate(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sixbirds-validate")
    parser.add_argument("--kind", required=True, choices=sorted(SCHEMA_SPEC_BY_KIND))
    parser.add_argument("--path", required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)
    summary = validate_artifact_summary(args.kind, args.path)
    print(json.dumps(summary, sort_keys=True))
    return 0


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


__all__ = [
    "CANONICAL_SCHEMA_ROOT",
    "COMPATIBILITY_RESULT_SCHEMA_PATH",
    "INHERITED_SCHEMA_KINDS",
    "LOCAL_SCHEMA_KINDS",
    "SCHEMA_SPEC_BY_KIND",
    "SCHEMA_SPECS",
    "SchemaSpec",
    "export_all_schemas",
    "export_schema",
    "main_export",
    "main_validate",
    "schema_inventory",
    "validate_artifact",
    "validate_artifact_summary",
]
