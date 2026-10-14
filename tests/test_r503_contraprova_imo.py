# -*- coding: utf-8 -*-
"""Testes da contra-prova R503: corpus IMO expandido (9 problemas) e
validação cruzada com verificação determinística."""

from __future__ import annotations

import pytest

from integrations.deepmind.imobench_harness import IMOBenchmarkHarness
from integrations.deepmind.imo_real_solver import RealIMOSolver


EXPECTED_BY_ID = {
    "imo-bench-algebra-001": "3",
    "imo-bench-algebra-004": "2^{u-2}",
    "imo-bench-number-theory-001": "(7, 3)",
    "imo-bench-combinatorics-001": "2^{n-1}",
    "imo-bench-algebra-002": "5",
    "imo-bench-number-theory-002": "{3}",
    "imo-bench-number-theory-003": "1006",
    "imo-bench-combinatorics-002": "88",
    "imo-bench-geometry-001": "2043230",
}


class TestCorpusExpandido:
    def test_corpus_tem_9_problemas(self):
        h = IMOBenchmarkHarness()
        ids = [p.problem_id for p in h.sample_dataset]
        assert len(ids) == 9
        assert "imo-bench-geometry-001" in ids

    def test_solver_resolve_novos_problemas(self):
        s = RealIMOSolver()
        assert s.solve_alg002()[0] == 5          # menor n: 2^n > n^2
        assert s.solve_nt002() == [3]            # p^2 | 2^p+1
        assert s.solve_nt003() == 1006           # v_3(2023!) por Legendre
        assert s.solve_comb002()["count_two_peaks"] == 88
        assert s.solve_geo001() == 2043230       # diagonais 2023-ágono


class TestContraProvaAntiLeak:
    """Nenhum solver ecoa short_answer: extrai o valor calculado do texto."""

    def test_solver_nao_ecoa_resposta(self):
        s = RealIMOSolver()
        h = IMOBenchmarkHarness()
        for p in h.sample_dataset:
            texto = s.solve(p)
            assert p.short_answer not in texto.split("Metodo:")[0], p.problem_id
            # o valor esperado nunca aparece antes do "Metodo:"
        assert True  # checagem de presença acima é a asserção central


class TestHarnessCompleto:
    def test_run_benchmark_9_problemas(self):
        h = IMOBenchmarkHarness()
        s = RealIMOSolver()
        res = h.run_benchmark(solver_fn=s.submit, limit=9)
        assert len(res["results"]) == 9
        assert res.get("total_problems", 0) == 9
        # Respostas explícitas calculadas; a justificativa não fornece acerto
        # por substring. O mapa esperado pertence somente ao teste.
        expected = {key: value.replace(" ", "") for key, value in EXPECTED_BY_ID.items()}
        submitted = {row["problem_id"]: row["predicted_answer"].replace(" ", "")
                     for row in res["results"]}
        assert submitted == expected
        assert all(row["is_correct"] is True for row in res["results"])
        assert all(row["formal_verified"] is False for row in res["results"])
        assert res["correct_problems"] == 9
        assert res["accuracy"] == 1.0
        assert res["dataset_scope"] == "internal_sample_with_derived_problems"
