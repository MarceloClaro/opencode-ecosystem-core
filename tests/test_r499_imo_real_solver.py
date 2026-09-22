# -*- coding: utf-8 -*-
"""Testes do solver determinístico real para problemas da IMO (R499).

O solver NUNCA recebe short_answer (anti-leak). Resultados esperados vêm da
dedução exata (enumeração/simbólica), não de eco da resposta.
Hermético, anti-overclaim: nenhum "superhuman"/"melhor que DeepMind".
"""

from __future__ import annotations

import re

import pytest

from integrations.deepmind.imo_real_solver import RealIMOSolver
from integrations.deepmind.imobench_harness import IMOBenchmarkHarness


@pytest.fixture(scope="module")
def solver() -> RealIMOSolver:
    return RealIMOSolver()


@pytest.fixture(scope="module")
def harness() -> IMOBenchmarkHarness:
    return IMOBenchmarkHarness()


BANNED = [r"\bsuperhuman\b", r"\bmelhor que [a-z]*(deepmind|alphageometry)\b",
          r"\bverificad[oa]s?\b"]


# ── P1: resolução exata dos problemas canônicos ─────────────────────────

def test_nt001_enumera_primodial(solver):
    sol = solver.solve_nt001()
    assert (7, 3) in sol, "enumeração exata de primos deve encontrar (7,3)"
    assert len(sol) >= 1


def test_alg001_floor_encontra_3(solver):
    sol = solver.solve_alg001()
    assert 3 in sol, "divisão inteira (quotient floor) deve dar N=3"
    assert 1 not in sol, "interpretação fracionária NÃO é a semântica alvo"


def test_comb001_confirma_2n1(solver):
    res = solver.solve_comb001()
    assert res["confirmed"] is True
    assert res["max_n"] >= 6
    assert all(res["counts"][n] == 2 ** (n - 1) for n in res["counts"])


def test_alg004_parcial_sem_prova(solver):
    res = solver.solve_alg004()
    assert res["status"] == "parcial"
    assert res["candidate"] == "2**(u-2)"
    assert res["formal_proof"] is False, "sem prova formal => nunca score 7"


# ── Anti-leak ───────────────────────────────────────────────────────────

def test_solver_sem_short_answer(solver, harness):
    for p in harness.sample_dataset:
        text = solver.solve(p)
        assert isinstance(text, str) and len(text) > 30, p.problem_id
        # a solução é DEDUZIDA: contém passos de método, não só resposta
        assert re.search(r"(valores|verifica|enumera|soma|permuta|desigualdade|pares|N=|n=|u=|C=|diagonais|formula)", text), p.problem_id


def test_harness_sem_leak(solver, harness):
    report = harness.run_benchmark(solver_fn=solver.solve, limit=4)
    assert report["total_problems"] == 4
    # o solver padrão (leak) daria 4/4 a 7; com solver real os números são
    # determinados pela dedução — garantimos que pelo menos 2 problemas são
    # resolvidos por enumeração exata e que média < 7
    assert report["correct_problems"] >= 2
    assert report["average_grade_0_to_7"] < 7


# ── Anti-overclaim ──────────────────────────────────────────────────────

def test_saida_sem_overclaim(solver, harness):
    report = harness.run_benchmark(solver_fn=solver.solve, limit=4)
    blob = str(report)
    for pattern in BANNED:
        assert not re.search(pattern, blob, re.IGNORECASE), pattern