"""SPEC-935-R618 — Reconciliação catálogo <-> runtime e Leitura guiada do Módulo 10.

Contexto factual (verificado em 29/09/2026): o Módulo 10 afirmava que 39 das 255
fichas "não estavam registradas no runtime". A auditoria mostrou que a afirmação
era FALSA: as 212 fichas de agents/catalog/ estão todas registradas, apenas sob
a convenção de slug (kebab-case) do opencode.json, enquanto o frontmatter usa o
nome humano. A diferença era artefato de comparação textual, não lacuna de runtime.

Este módulo fixa o invariante correto: catálogo e runtime devem reconciliar sem
resíduo, e o livro não pode afirmar ausência de registro sem prova.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIVRO = ROOT / "livro-core"
MOD10 = LIVRO / "mod-10-catalogo.tex"

pytestmark = pytestmark = pytest.mark.skipif(not MOD10.exists(), reason="mod-10 ausente")


def _carregar_gen():
    spec = importlib.util.spec_from_file_location("gen_mod10", LIVRO / "gen_mod10.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower())


# ------------------------------------------------------- AC1
def test_ac1_toda_ficha_reconcilia_com_um_agente_registrado():
    """AC1: nenhuma ficha documentada pode estar ausente do runtime."""
    gen = _carregar_gen()
    cfg = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    runtime = set(cfg["agent"])
    cards = gen.carregar_cards(ROOT)
    nao_reg = gen.nao_registrados(cards, runtime)
    assert nao_reg == [], f"fichas sem agente no runtime: {nao_reg}"


def test_ac1b_reconciliacao_e_deterministica_e_total():
    """AC1: a reconciliação deve cobrir todos os cards, duas vezes iguais."""
    gen = _carregar_gen()
    cfg = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    runtime = list(cfg["agent"])
    cards = gen.carregar_cards(ROOT)
    m1 = gen.reconciliar(cards, runtime)
    m2 = gen.reconciliar(cards, runtime)
    assert m1 == m2, "reconciliação não determinística"
    assert len(m1) == len(cards), f"{len(cards) - len(m1)} fichas sem par"


def test_ac1c_alias_explicito_necessario():
    """AC1: o caso que o slug não resolve precisa estar declarado, não adivinhado."""
    gen = _carregar_gen()
    assert any("Synthetic University" in k for k in gen.ALIASES), (
        "alias de Synthetic University removido — a reconciliação voltaria a falhar"
    )


# ------------------------------------------------------- AC2
def test_ac2_todo_agente_runtime_tem_ficha_ou_inline_declarado():
    """AC2: nenhum agente registrado pode ser invisível ao catálogo sem decisão."""
    gen = _carregar_gen()
    cfg = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    runtime = list(cfg["agent"])
    cards = gen.carregar_cards(ROOT)
    pares = set(gen.reconciliar(cards, runtime).values())
    sem_ficha = sorted(set(runtime) - pares - set(gen.INLINE_DECLARADOS))
    assert sem_ficha == [], f"agentes runtime sem ficha e sem declaração: {sem_ficha}"


def test_ac2b_inventario_bate():
    """AC2: cards + inline declarados == agentes registrados."""
    gen = _carregar_gen()
    cfg = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    runtime = list(cfg["agent"])
    cards = gen.carregar_cards(ROOT)
    pares = gen.reconciliar(cards, runtime)
    assert len(cards) + len(set(runtime) - set(pares.values())) == len(runtime), (
        f"inventário não fecha: {len(cards)} cards + inline != {len(runtime)} agentes"
    )


# ------------------------------------------------------- AC3
def test_ac3_livro_nao_alega_ausencia_de_registro():
    """AC3 (anti-overclaim): a alegação falsa de R616 não pode voltar."""
    t = MOD10.read_text(encoding="utf-8")
    proibidos = [
        r"fichas? (documentadas )?n[ãa]o (est[ãa]o |foram )?registrad",
        r"fichas? restantes? \(ex\.:",
        r"39 fichas",
    ]
    for p in proibidos:
        assert not re.search(p, t, re.I), f"alegação de ficha não registrada presente: {p!r}"


def test_ac3b_titulo_conta_agentes_de_fato():
    """AC3: o número no título do capítulo deve ser o de agentes registrados."""
    gen = _carregar_gen()
    cfg = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    t = MOD10.read_text(encoding="utf-8")
    m = re.search(r"\\chapter\{Catálogo Completo — (\d+) Fichas de Agente", t)
    assert m, "título sem contagem explícita de fichas"
    assert int(m.group(1)) == len(cfg["agent"]), (
        f"título afirma {m.group(1)} fichas; runtime tem {len(cfg['agent'])} agentes"
    )


def test_ac3c_registro_da_convencao_de_nomes():
    """AC3: a causa real (slug vs nome humano) precisa estar documentada."""
    t = MOD10.read_text(encoding="utf-8")
    assert re.search(r"kebab|slug|conven[çc][ãa]o de nome", t, re.I), (
        "convenção de nomes (kebab-case) não é mencionada — o leitor não entende a discrepância"
    )


# ------------------------------------------------------- AC4
def test_ac4_leitura_guiada_n10_completa():
    """AC4: o Módulo 10 (enumerativo) passa a ter leitura guiada canônica."""
    t = MOD10.read_text(encoding="utf-8")
    m = re.search(r"\\section\[Leitura guiada\]\{[^}]*M[oó]dulo 10", t, re.I) or \
        re.search(r"\\section\[Leitura guiada\]\{([^}]*)\}", t)
    assert m, "Módulo 10 sem Leitura guiada"
    bloco = t[m.end(): m.end() + 9000]
    fim = re.search(r"\n\\section", bloco)
    if fim:
        bloco = bloco[: fim.start()]
    for box in ("descricao", "definicao", "metodo", "resultado", "aviso"):
        assert f"\\begin{{{box}}}" in bloco, f"N-10 sem caixa {box}"
    for rotulo in ("O fenômeno", "Grandezas e definições", "Dedução passo a passo",
                   "Exemplo resolvido", "Ordem de grandeza", "Limite de validade",
                   "Exercícios"):
        assert rotulo in bloco, f"N-10 sem bloco {rotulo!r}"


def test_ac4b_gerador_produz_n10_e_e_reexecutavel():
    """AC4: N-10 vive no gerador; rodar duas vezes não duplica nada."""
    gen = _carregar_gen()
    t = MOD10.read_text(encoding="utf-8")
    fonte = (LIVRO / "gen_mod10.py").read_text(encoding="utf-8")
    assert "Leitura guiada" in fonte, "N-10 não está no gerador — será perdida na regeração"
    assert t.count("ARQUIVO GERADO") == 1


# ------------------------------------------------------- AC5
def test_ac5_permissoes_curadas_sobrevivem_ao_merge_do_catalogo():
    """AC5 (regressão real): o merge do catálogo não pode rebaixar permissões.

    R618: ao criar os cards dos 4 agentes essenciais, `agents.update(_catalog_agents())`
    sobrescreveu `coder` {edit: allow, bash: allow} por {deny, deny} — deixando o
    único agente com bash inutilizável. Este teste falha se isso voltar.
    """
    sys.path.insert(0, str(ROOT))
    from integrations.opencode_cli import _ESSENTIAL_AGENT_PERMISSIONS, build_config

    cfg = build_config()["agent"]
    for agent_id, esperado in _ESSENTIAL_AGENT_PERMISSIONS.items():
        if agent_id not in cfg:
            continue
        assert cfg[agent_id]["permission"] == esperado, (
            f"{agent_id}: permissão {cfg[agent_id]['permission']} != {esperado}"
        )
    # o caso mais perigoso, verificado explicitamente
    assert cfg["coder"]["permission"]["bash"] == "allow"
    assert cfg["coder"]["permission"]["edit"] == "allow"


# ------------------------------------------------------- AC6
def test_ac6_inventario_citado_bate_com_o_runtime():
    """AC6 (gate que faltava): o livro não pode citar um total de agentes obsoleto.

    R618 descobriu que o Módulo 8 afirmava 255 fichas e 84,7% de cobertura
    num capítulo cujo número real era 216 com cobertura 100% — o gate R617 só
    conferia contagens de specs/testes/ciclos, não de agentes. Este teste fecha
    a lacuna: qualquer afirmação sobre o total do inventário precisa casar com
    o runtime.
    """
    import glob

    cfg = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    n = len(cfg["agent"])
    obsoletos = {"255", "212"}  # totais históricos de catálogo
    for f in sorted(glob.glob(str(ROOT / "livro-core" / "mod-*.tex"))):
        t = Path(f).read_text(encoding="utf-8")
        for m in re.finditer(r"\b(\d{3})\s+fichas\b", t):
            assert m.group(1) != "255", (
                f"{Path(f).name}: ainda cita o total obsoleto 255 fichas"
            )
        for m in re.finditer(r"(\\d{3})/(\\d{3})", t):
            den = int(m.group(2))
            if den in (255, 212):
                raise AssertionError(
                    f"{Path(f).name}: fração com denominador obsoleto: {m.group(0)}"
                )
    # o total correto precisa estar presente no capítulo do catálogo
    alvo = r"\\textbf\{" + str(n) + r"\} agentes"
    assert re.search(alvo, MOD10.read_text(encoding="utf-8"))
