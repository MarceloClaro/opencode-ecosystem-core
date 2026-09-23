"""Testes da instrumentação de eficiência por operação (SPEC-975, R582)."""

from __future__ import annotations

import json

import pytest

from integrations.op_timing import record, report


@pytest.fixture()
def timing_path(tmp_path, monkeypatch):
    p = tmp_path / "op_times.jsonl"
    monkeypatch.setenv("OP_TIMES_PATH", str(p))
    monkeypatch.setenv("OP_ROUND_ID", "R582")
    return p


def test_record_append_only_e_report_medianas(timing_path):
    record("smoke", 0.097, True)
    record("smoke", 0.082, True)
    record("smoke", 0.300, False)
    record("budget", 0.050, True)

    out = report()
    assert "4 medições, 1 falhas" in out
    assert "smoke" in out
    assert "budget" in out
    assert "97.0 ms" in out  # mediana do smoke = 0.097 (sorted: 0.082,0.097,0.300)
    assert "50.0 ms" in out

    # append-only: segunda gravação não apaga a primeira
    record("smoke", 0.111, True)
    assert "5 medições" in report()


def test_report_sem_arquivo(timing_path):
    assert "nenhuma medição" in report()


def test_report_filtra_linhas_corrompidas(timing_path):
    timing_path.write_text("{\"op\": \"a\", \"seconds\": 0.1, \"ok\": true}\nlinha-quebrada\n", encoding="utf-8")
    out = report()
    assert "1 medições" in out


if __name__ == "__main__":
    pytest.main([__file__, "-q"])