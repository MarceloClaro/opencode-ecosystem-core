# -*- coding: utf-8 -*-
"""Testes RED para SPEC-935-R608: bootstrap tolerante a frontmatter com head.

Herméticos: montam cards em ``tmp_path`` (com/sem cabeçalho antes do
frontmatter), além de uma verificação sem rede sobre o catálogo real do repo
(B4). Não tocam singletons globais (apenas ``load_catalog_agents``/
``parse_agent_catalog_md``, stateless).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mci.agent_registry_bootstrap import load_catalog_agents, parse_agent_catalog_md


HEADER_CARD = """<!--
card gerado a partir do backup Antigravity (SPEC-935-R130)
-->
# Nome do Agente

---
name: agente-exemplo
description: >
  Agente de exemplo com descrição em bloco.
skills:
  - id: skill-alfa
tags: [roteador, exemplo]
---
Corpo do card.
"""

PLAIN_CARD = """---
name: agente-fino
description: Agente sem cabeçalho.
---
"""

NO_FENCE_CARD = """nome: sem-fence
description: metadados fora do esquema YAML ---.
"""


def _write(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


def test_parse_aceita_card_com_cabecalho(tmp_path: Path):
    p = _write(tmp_path, "agente-exemplo.md", HEADER_CARD)
    info = parse_agent_catalog_md(p)
    assert info is not None
    assert info["agent_id"] == "agente-exemplo"
    assert info["name"] == "agente-exemplo"
    assert "skill-alfa" in info["capabilities"]
    assert "roteador" in info["capabilities"]
    assert "exemplo com descrição" in info["description"]


def test_parse_sem_regressao_no_frontmatter_inicial(tmp_path: Path):
    p = _write(tmp_path, "agente-fino.md", PLAIN_CARD)
    info = parse_agent_catalog_md(p)
    assert info is not None
    assert info["agent_id"] == "agente-fino"
    assert info["name"] == "agente-fino"
    assert info["capabilities"]


def test_parse_pula_card_sem_fence(tmp_path: Path):
    p = _write(tmp_path, "sem-fence.md", NO_FENCE_CARD)
    assert parse_agent_catalog_md(p) is None


@pytest.mark.parametrize("bom", ["\ufeff", ""])
def test_parse_ignora_bom_e_comentario(tmp_path: Path, bom: str):
    p = _write(tmp_path, "agente-exemplo.md", bom + "<!-- x -->\n\n---\nname: com-bom\n---\n")
    info = parse_agent_catalog_md(p)
    assert info is not None
    assert info["name"] == "com-bom"


MALFORMED_EXPECTED = set()  # ciclo R608-R609: catálogo 100% parseável


def test_catalogo_real_registra_todos_os_cards():
    """R608-R609: todo card atual deve ser parseável e descrito.

    A tolerância a cabeçalho é o que garante que as famílias que abrem com
    comentário HTML (mira, cloud, literary) estejam registradas em runtime; o
    reparo das descrições garante nenhum card com frontmatter vazio/quebrado.
    R618 acrescentou as 4 fichas dos agentes essenciais que só existiam inline
    (academic_writer, auditor, coder, researcher): 212 -> 216, cobertura 1:1.
    """
    catalog = PROJECT_ROOT / "agents" / "catalog"
    assert catalog.is_dir()
    agents = load_catalog_agents(catalog)
    ids = {a["agent_id"] for a in agents}
    total = len(list(catalog.glob("*.md")))
    assert total > 0
    assert len(agents) == total
    assert MALFORMED_EXPECTED.isdisjoint(ids)
    # todos os cards registrados têm nome, descrição e capacidades não vazias
    assert all(
        a["name"].strip() and a["description"].strip() and a["capabilities"]
        for a in agents
    )
    # caso antes descartado por `startswith("---")`: agora registrado
    for fam in ("mira-planner", "cloud-alloydb-specialist",
                "literary-orchestrator-phd", "haystack-rag"):
        assert fam in ids, f"card não registrado: {fam}"
