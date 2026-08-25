"""Predicados mínimos que decidem caminhos positivos da verificação formal."""

from __future__ import annotations


def solver_result_proves_implication(result: object, unsat_marker: object) -> bool:
    """Só uma inconsistência formal entre premissas e negação conclui a prova."""
    return result == unsat_marker
