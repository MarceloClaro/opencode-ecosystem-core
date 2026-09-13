# -*- coding: utf-8 -*-
"""Testes do comando CLI reverse-scan (R484) — Scanner Reverso via terminal.

Hermético: subprocess local, sem rede, sem credenciais. Usa o mesmo padrão
de tests/test_r481_core_check.py.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
CLI = [sys.executable, "-m", "marceloclaro.cli"]

BANNED = [r"\bsuperhuman\b", r"\bverificad[oa]s?\b", r"\bqualis a1\b", r"\bsuperação\b"]


def _run(*args: str, cwd: pathlib.Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [*CLI, *args],
        capture_output=True,
        text=True,
        cwd=str(cwd or ROOT),
        timeout=120,
    )


class TestUsage:
    def test_missing_target_exits_nonzero(self):
        proc = _run("reverse-scan")
        assert proc.returncode != 0
        assert "target" in proc.stdout.lower() or "target" in proc.stderr.lower()

    def test_unknown_target_still_runs(self):
        # target inexistente no grafo vira aviso, mas com --file deve executar
        probe = ROOT / "specs" / "SPEC-935-R483-reverse-scanner.md"
        proc = _run("reverse-scan", "--target", "nao.existe", "--file", str(probe))
        assert proc.returncode == 0


class TestJsonOutput:
    def test_json_fields(self, tmp_path):
        art = tmp_path / "art.md"
        art.write_text(
            "# Artefato\nMeta-análise requer raciocínio probabilístico e dados longitudinal.\n",
            encoding="utf-8",
        )
        proc = _run(
            "reverse-scan",
            "--target", "metodos.Meta-análise",
            "--file", str(art),
            "--json",
        )
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert "target_state" in data
        assert "reverse_closure" in data
        assert "evolution_gap" in data
        assert "opportunities" in data
        assert "params" in data
        assert data["target_state"] == ["metodos.Meta-análise"]

    def test_json_no_anti_overclaim(self, tmp_path):
        art = tmp_path / "art.md"
        art.write_text("Ciência com metodologia sólida.\n", encoding="utf-8")
        proc = _run(
            "reverse-scan",
            "--target", "metodos.Meta-análise",
            "--file", str(art),
            "--json",
        )
        for pattern in BANNED:
            assert not re.search(pattern, proc.stdout, re.IGNORECASE), pattern


class TestHumanOutput:
    def test_human_labels(self):
        # corpus real da spec R483 + domínio acadêmico: o alvo metodos.*
        # pertence às dimensões epistemológicas (não às do ecossistema)
        probe = ROOT / "specs" / "SPEC-935-R483-reverse-scanner.md"
        proc = _run(
            "reverse-scan",
            "--target", "metodos.Meta-análise",
            "--file", str(probe),
            "--domain", "academic",
        )
        assert proc.returncode == 0
        assert "R(F)" in proc.stdout
        assert "Gap evolutivo" in proc.stdout
        assert "tier=" in proc.stdout

    def test_specs_default_corpus(self):
        # sem --file: usa specs/ como corpus; domínio acadêmico garante
        # que o alvo metodos.* existe no grafo
        proc = _run(
            "reverse-scan", "--target", "metodos.Meta-análise",
            "--domain", "academic",
        )
        assert proc.returncode == 0
        assert "Gap evolutivo" in proc.stdout


class TestHelp:
    def test_help_documents_command(self):
        proc = _run("ajuda")
        assert "reverse-scan" in proc.stdout

    def test_domain_academic_accepted(self, tmp_path):
        art = tmp_path / "art.md"
        art.write_text("Pesquisa qualitativa fenomenológica.\n", encoding="utf-8")
        proc = _run(
            "reverse-scan",
            "--target", "metodos.Meta-análise",
            "--file", str(art),
            "--domain", "academic",
            "--json",
        )
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert "target_state" in data