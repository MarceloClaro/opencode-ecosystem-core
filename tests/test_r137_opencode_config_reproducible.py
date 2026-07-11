# -*- coding: utf-8 -*-
"""
Testes R137 — opencode.json reproduzível e chaveado por slug
=============================================================
O `opencode.json` é um artefato GERADO. Antes da R137 ele havia sido
montado à mão pela frente cloud com chaveamento inconsistente (agentes
cloud por slug; agentes antigos por nome de exibição), de forma que o
comando documentado de regeneração (`python3 -m integrations.opencode_cli`)
NÃO reproduzia o arquivo commitado — rodá-lo quebraria os testes cloud.

A R137 reconcilia o gerador: todo agente do catálogo é chaveado pelo
**slug do nome do arquivo** (estável, único, reproduzível). Estes testes
travam essa garantia:

1. O gerador chaveia por slug (ex.: `cloud-alloydb-specialist`,
   `adr-manager`), nunca por nome de exibição (`Cloud AlloyDB Specialist`).
2. A geração é determinística (duas chamadas → resultado idêntico).
3. O `opencode.json` commitado é EXATAMENTE o que o gerador produz
   (regenerar não gera diff).

Requisitos: SPEC-935-R137.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_gerador_chaveia_catalogo_por_slug():
    from integrations.opencode_cli import build_config

    agents = build_config().get("agent", {})
    # Slugs de arquivo esperados (chave = basename sem .md).
    esperados_slug = [
        "cloud-alloydb-specialist",
        "cloud-bigquery-specialist",
        "adr-manager",
        "architecture-analyzer",
        "mira-extract",
    ]
    for slug in esperados_slug:
        assert slug in agents, f"Agente '{slug}' não chaveado por slug no opencode.json"

    # Nenhuma chave deve ser um nome de exibição (com espaços/maiúsculas).
    nomes_exibicao = [k for k in agents if " " in k]
    assert not nomes_exibicao, (
        f"Chaves com nome de exibição (deveriam ser slug): {nomes_exibicao[:5]}"
    )


def test_geracao_deterministica():
    from integrations.opencode_cli import build_config

    a = build_config()
    b = build_config()
    assert a == b, "build_config() não é determinístico (duas chamadas divergem)"


def test_opencode_json_commitado_reproduz_o_gerador():
    """Garantia central: regenerar não produz diff — o arquivo em disco é
    exatamente a saída do gerador."""
    from integrations.opencode_cli import build_config

    committed = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    generated = build_config()
    assert committed == generated, (
        "opencode.json em disco DIVERGE do gerador — rode "
        "`python3 -m integrations.opencode_cli` e commite o resultado"
    )
