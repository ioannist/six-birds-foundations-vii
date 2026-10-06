"""Foundations VII finite reference world.

The package is deliberately standard-library-only.  Its results are finite
reference assays and regression certificates, never universal mathematical
proofs.
"""

from .evaluator import DerivedFacts, evaluate
from .fixtures import load_countermodels, load_scenarios
from .model import Scenario, ScenarioResult

__all__ = [
    "DerivedFacts",
    "Scenario",
    "ScenarioResult",
    "evaluate",
    "load_countermodels",
    "load_scenarios",
]
