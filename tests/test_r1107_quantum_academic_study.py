#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contratos da camada de estudo acadêmico quântico (R1107)."""
from __future__ import annotations

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SPEC = RAIZ / "specs" / "SPEC-935-R1107-quantum-academic-study.md"
SKILL = RAIZ / ".opencode" / "skills" / "estudo-quantico-academico" / "SKILL.md"
AGENTE = RAIZ / "agents" / "catalog" / "quantum-academic-study.md"
DOC = RAIZ / "docs" / "ESTUDO_QUANTICO_ACADEMICO_R1107.md"


def _frontmatter(texto: str) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", texto, flags=re.S)
    assert m, "frontmatter ausente"
    return m.group(1)


def test_arquivos_existem():
    for caminho in (SPEC, SKILL, AGENTE, DOC):
        assert caminho.exists(), caminho
        assert caminho.stat().st_size > 500, caminho


def test_spec_tem_requisitos_e_criterios():
    texto = SPEC.read_text(encoding="utf-8")
    for i in range(1, 11):
        assert f"**R{i}.**" in texto, f"R{i} ausente"
    for termo in ("Critérios de sucesso", "Não objetivos", "Testes"):
        assert termo in texto, termo


def test_skill_frontmatter_e_conteudo():
    texto = SKILL.read_text(encoding="utf-8")
    fm = _frontmatter(texto)
    assert "name: estudo-quantico-academico" in fm
    assert "description:" in fm
    for termo in (
        "seis eixos",
        "16 semanas",
        "pré-registro",
        "IC95%",
        "Lean",
        "anti-overclaim",
        "Não declare Qualis",
    ):
        assert termo.lower() in texto.lower(), termo


def test_agente_frontmatter_e_rotas():
    texto = AGENTE.read_text(encoding="utf-8")
    fm = _frontmatter(texto)
    for termo in (
        "agent_id: quantum-academic-study",
        "lifecycle: managed-v1",
        "type: specialist",
        "category: engineering",
        "language: pt-BR",
        "parent: marceloclaro",
        "spec_file: specs/SPEC-935-R1107-quantum-academic-study.md",
        "test_file: tests/test_r1107_quantum_academic_study.py",
        "allow_edit: true",
        "webfetch: deny",
        "bash: true",
        "edit: true",
        "write: true",
    ):
        assert termo in fm, termo
    for rota in (
        "21_agente_matematica_aplicada_modelagem_formal",
        "27_agente_computacao_quantica_aplicada",
        "quantum-experiment-auditor",
        "quantum-lean-verifier",
        "academic_writer",
        "abnt-latex-modular",
        "bibtex-crossref-auditor",
    ):
        assert rota in texto, rota


def test_agente_registrado_no_opencode():
    import json

    cfg = json.loads((RAIZ / "opencode.json").read_text(encoding="utf-8"))
    assert "quantum-academic-study" in cfg["agent"]
    entry = cfg["agent"]["quantum-academic-study"]
    assert entry["prompt"] == "{file:./agents/catalog/quantum-academic-study.md}"


def test_documento_tem_trilha_e_criterios():
    texto = DOC.read_text(encoding="utf-8")
    for termo in (
        "16 semanas",
        "Fase 1",
        "Fase 4",
        "Critérios de sucesso",
        "pré/pós-teste",
        "replicação independente",
        "Lean",
        "Limites",
    ):
        assert termo.lower() in texto.lower(), termo


def test_sem_segredo_literal():
    padroes = [
        re.compile(r"GJQ_API_KEY\s*=\s*[\"'][A-Za-z0-9_-]{16,}[\"']"),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    ]
    for caminho in (SKILL, AGENTE, DOC, SPEC):
        texto = caminho.read_text(encoding="utf-8")
        for padrao in padroes:
            assert not padrao.search(texto), f"segredo em {caminho}"


def test_sem_overclaim():
    proibidos = (
        "Qualis A1 garantido",
        "peer review concluído",
        "eficácia comprovada",
        "hardware executado",
        "Lean prova a física",
        "simulação é equivalente",
    )
    for caminho in (SKILL, AGENTE, DOC):
        texto = caminho.read_text(encoding="utf-8").lower()
        for termo in proibidos:
            assert termo.lower() not in texto, f"overclaim em {caminho}: {termo}"
