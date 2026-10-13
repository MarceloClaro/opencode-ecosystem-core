# -*- coding: utf-8 -*-
"""Testes da integração IVA/SNS/SCE no DiagnosticPipeline (R496).

A camada profunda (deep=True) do pipeline passa a incluir:
  - report["inertia"]     (R493) — QIV = Potencial − Inércia
  - report["noise"]       (R494) — SPS/NRR/FLI do corpus
  - report["compression"] (R495) — CR/CPS/FLI/DG + texto comprimido
deep=False mantém o comportamento anterior (R8 test_deep_diagnose).
Hermético, anti-overclaim.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from scanners.pipeline import DiagnosticPipeline

BANNED = [r"\bsuperhuman\b", r"\bverificad[oa]s?\b", r"\bqualis a1\b", r"\bsuperação\b"]

# Corpus com repetição e ruído para exercitar SNS/SCE
CORPUS = (
    "A metacognição supervisiona os agentes do ecossistema e coordena as "
    "decisões de roteamento. " * 3
    + "O feedback e a memória compartilhada alimentam a metacognição em "
    "tempo real. " * 2
    + "ex: Jaccard mede similaridade entre conjuntos. ex: Jaccard mede "
    "similaridade entre conjuntos. "
    + "a a a a a a a a a a"
)

GOALS = [
    {"name": "publicar_artigo",
     "description": "Publicar artigo de alto impacto sobre metacognição multiagente",
     "weight": 2.0, "goal_type": "strategic"},
]


@pytest.fixture(scope="module")
def deep_report():
    pipeline = DiagnosticPipeline()
    return pipeline.run(CORPUS, domain="multiagent_systems",
                        goals=GOALS, deep=True)


@pytest.fixture(scope="module")
def shallow_report():
    pipeline = DiagnosticPipeline()
    return pipeline.run(CORPUS, domain="multiagent_systems", goals=GOALS)


# ═══════════════════════════════════════════════════════════════════════
# CA1-CA4 — chaves novas no deep
# ═══════════════════════════════════════════════════════════════════════

class TestDeepBlocks:
    def test_inertia_block(self, deep_report):
        inv = deep_report.get("inertia", {})
        assert "error" not in inv, inv.get("error")
        assert inv.get("n_assessments", 0) > 0
        assert len(inv.get("top", [])) > 0

    def test_inertia_qiv_range(self, deep_report):
        for a in deep_report["inertia"]["top"]:
            assert 0.0 <= a["qiv"] <= 1.0
            assert 0.0 <= a["inertia"] <= 1.0
            for v in ("complexity", "dependencies", "cost", "coupling"):
                assert 0.0 <= a[v] <= 1.0, v

    def test_noise_block(self, deep_report):
        noise = deep_report.get("noise", {})
        assert "error" not in noise, noise.get("error")
        assert 0.0 <= noise.get("sps", -1) <= 1.0
        assert 0.0 <= noise.get("nrr", -1) <= 1.0
        assert 0.0 <= noise.get("fli", -1) <= 1.0
        assert noise.get("level") in ("seguro", "moderado", "destrutivo")

    def test_compression_block(self, deep_report):
        comp = deep_report.get("compression", {})
        assert "error" not in comp, comp.get("error")
        assert 0.0 <= comp.get("cps", -1) <= 1.0
        assert comp.get("cr", 0) >= 1.0
        assert isinstance(comp.get("compressed_text"), str)


# ═══════════════════════════════════════════════════════════════════════
# CA5-CA7 — backcompat, report_md, anti-overclaim
# ═══════════════════════════════════════════════════════════════════════

class TestQuality:
    def test_shallow_without_new_keys(self, shallow_report):
        for key in ("inertia", "noise", "compression"):
            assert key not in shallow_report, key
        for key in ("noological", "teleological", "potentiality",
                    "evolutionary", "reversa"):
            assert key in shallow_report

    def test_report_md_present(self, deep_report):
        for key in ("inertia", "noise", "compression"):
            md = deep_report[key].get("report_md", "")
            assert isinstance(md, str) and md.strip(), key
            assert "#" in md, key

    def test_no_anti_overclaim_deep(self, deep_report):
        for pattern in BANNED:
            assert not re.search(pattern, str(deep_report), re.IGNORECASE), pattern


# ═══════════════════════════════════════════════════════════════════════
# CA8-CA10 — efetividade e robustez
# ═══════════════════════════════════════════════════════════════════════

class TestEffectiveness:
    def test_compression_cr_gt1(self, deep_report):
        assert deep_report["compression"]["cr"] > 1.0
        assert deep_report["compression"]["tokens_saved"] > 0

    def test_noise_removed_duplicates(self, deep_report):
        # corpus tem ruído + duplicatas → algo foi removido
        assert deep_report["noise"]["n_removed"] > 0

    def test_deep_without_goals_still_runs(self):
        pipeline = DiagnosticPipeline()
        report = pipeline.run(CORPUS, domain="x", deep=True)
        assert "inertia" in report
        assert "noise" in report
        assert "compression" in report
        assert "duration_s" in report


# ═══════════════════════════════════════════════════════════════════════
# R498 — contrato do pipe real: o comando /diagnose (opencode.json)
# roda o pipeline com deep=True por padrão (blocos novos SEMPRE ativos)
# ═══════════════════════════════════════════════════════════════════════

ROOT = Path(__file__).resolve().parent.parent


def _diagnose_from_config(config):
    """Executa a ferramenta solicitada pelo prompt, sem simular o pipeline.

    OpenCode entrega esse template ao agente. A prova cobre a chamada
    estruturada local; a interpretação do prompt por um modelo é externa.
    """
    command = config["command"]["diagnose"]
    assert command["agent"] == "marceloclaro"
    assert config["tools"]["core_command"] is False
    assert config["agent"][command["agent"]]["tools"]["core_command"] is True
    operation = re.match(r'^Execute core_command com command="([a-z-]+)"\.',
                         command["template"])
    assert operation, "O prompt precisa encaminhar a operação à ferramenta real."
    assert operation.group(1) == "diagnose"
    assert "$ARGUMENTS" in command["template"]

    node = shutil.which("node")
    assert node, "Node é necessário para executar a ferramenta OpenCode real."
    document = ROOT / "specs" / "SPEC-935-R200-LIVRO-ALFABETIZACAO.md"
    script = """
import {readFileSync} from 'node:fs';
const {default: operation} = await import(process.argv[1]);
const request = JSON.parse(readFileSync(0, 'utf8'));
const result = await operation.execute(request.args, {
  agent: request.agent, worktree: process.argv[2], directory: process.argv[2],
  abort: new AbortController().signal, sessionID:'R496', messageID:'deep-diagnose'
});
console.log(result);
"""
    process = subprocess.run(
        [node, "--experimental-strip-types", "--input-type=module", "-e", script,
         (ROOT / ".opencode/tools/core_command.ts").as_uri(), str(ROOT)],
        input=json.dumps({"args": {"command": operation.group(1),
                                  "arguments": str(document)},
                          "agent": command["agent"]}, ensure_ascii=False),
        capture_output=True, text=True, cwd=ROOT, timeout=90, shell=False,
    )
    assert process.returncode == 0, process.stderr[-1500:]
    envelope = json.loads(process.stdout)
    assert envelope["success"] and envelope["status"] == "completed", envelope
    assert envelope["coordinator"] == "marceloclaro"
    assert envelope["command"] == "diagnose"
    assert envelope["input"]["arguments"] == str(document)
    assert envelope["process"]["returncode"] == 0
    report = envelope["result"]
    assert report["inertia"]["n_assessments"] > 0
    assert report["noise"]["level"] in ("seguro", "moderado", "destrutivo")
    assert {"cr", "cps", "dg", "compressed_text"} <= set(report["compression"])
    assert report["successors"]["total"] >= 1
    for section in ("inertia", "noise", "compression"):
        assert "error" not in report[section], report[section]
        assert report[section]["report_md"].strip(), section
    return report


class TestRealPipeContract:
    """O pipe invocado pelo usuário não é demo: carrega a camada profunda."""

    def test_opencode_json_diagnose_uses_deep(self):
        cfg = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
        _diagnose_from_config(cfg)

    def test_generated_diagnose_command_runs_deep(self):
        from integrations.opencode_cli import build_config
        _diagnose_from_config(build_config())

    def test_real_document_run_deep_report(self):
        """Pipe real sobre documento real do repo (spec R200) entrega blocos novos."""
        corpus = (ROOT / "specs" / "SPEC-935-R200-LIVRO-ALFABETIZACAO.md").read_text(encoding="utf-8")
        report = DiagnosticPipeline().run(corpus, domain="academic", deep=True)
        assert report["noise"]["level"] in ("seguro", "moderado", "destrutivo")
        assert "report_md" in report["inertia"]
        assert report["successors"]["total"] >= 1
        assert {"cr", "cps", "dg"} <= set(report["compression"])
