# -*- coding: utf-8 -*-
"""
Pacote SDD/TDD — Specification-Driven & Test-Driven Development
===============================================================
Motor de especificações executáveis e ciclo Red-Green-Refactor
para todos os componentes e agentes do OpenCode Ecosystem Core.
"""

from sdd.spec_engine import (
    AcceptanceCriterion,
    Specification,
    SpecRegistry,
    SpecVerifier,
    spec_registry,
    spec_verifier,
)
from sdd.tdd_runner import TDDRunner, tdd_runner, run_pytest

__all__ = [
    "AcceptanceCriterion",
    "Specification",
    "SpecRegistry",
    "SpecVerifier",
    "spec_registry",
    "spec_verifier",
    "TDDRunner",
    "tdd_runner",
    "run_pytest",
]
