"""SPEC-935-R619 — Cobertura didática de 100% dos módulos do livro Core.

Até R618, 14 de 17 módulos pedagógicos tinham Leitura guiada completa. Faltavam
os Módulos 11 (biblioteca e metodologia ABNT), 13 (ativação de agentes) e 14
(fichas condensadas por categoria) — os três justamente os que ensinam *como*
usar o sistema, e que mais se beneficiariam do exemplo resolvido.

Este gate exige 100% de cobertura, com a exclusão da capa explicitamente
declarada e justificada (a folha de rosto não é módulo pedagógico) — para que
"100%" seja auditável e não uma afirmação.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIVRO = ROOT / "livro-core"
MODS = sorted(LIVRO.glob("mod-*.tex"))

# Única exclusão permitida, com justificativa: folha de rosto.
NAO_MODULO = {"mod-00-capa.tex"}

pytestmark = pytest.mark.skipif(not MODS, reason="livro-core/mod-*.tex ausente")

BLOCOS = (
    "O fenômeno",
    "Grandezas e definições",
    "Dedução passo a passo",
    "Exemplo resolvido",
    "Ordem de grandeza e verificação",
    "Limite de validade",
    "Exercícios",
)


def _secoes(t: str) -> list[tuple[str, str]]:
    """(título, bloco) de cada \\section[Leitura guiada]{...}."""
    out = []
    for m in re.finditer(r"\\section\[Leitura guiada\]\{([^}]*)\}", t):
        bloco = t[m.end(): m.end() + 12000]
        fim = re.search(r"\n\\section", bloco)
        if fim:
            bloco = bloco[: fim.start()]
        out.append((m.group(1), bloco))
    return out


# ------------------------------------------------------- AC1
def test_ac1_cobertura_de_100_por_cento():
    """AC1: todo módulo pedagógico tem exatamente uma Leitura guiada."""
    faltando, duplicadas = [], []
    for f in MODS:
        if f.name in NAO_MODULO:
            continue
        n = len(_secoes(f.read_text(encoding="utf-8")))
        if n == 0:
            faltando.append(f.name)
        elif n > 1:
            duplicadas.append((f.name, n))
    assert not faltando, f"módulos sem Leitura guiada: {faltando}"
    assert not duplicadas, f"módulos com Leitura guiada duplicada: {duplicadas}"


def test_ac1b_exclusao_da_capa_e_justificada():
    """AC1: a exclusão não pode crescer em silêncio."""
    modulos = {f.name for f in MODS if f.name not in NAO_MODULO}
    assert modulos, "nenhum módulo pedagógico identificado"
    capa = (LIVRO / "mod-00-capa.tex")
    assert capa.exists(), "a capa não pode ser removida para inflar a cobertura"
    assert "\\chapter" not in capa.read_text(encoding="utf-8"), (
        "mod-00-capa.tex virou capítulo: revise a lista NAO_MODULO"
    )


# ------------------------------------------------------- AC2
@pytest.mark.parametrize("bloco_rotulo", BLOCOS)
def test_ac2_todos_os_blocos_canonicos_em_todos_os_modulos(bloco_rotulo):
    """AC2: os 7 blocos do método, em todos os módulos (não só nos primeiros)."""
    for f in MODS:
        if f.name in NAO_MODULO:
            continue
        for titulo, bloco in _secoes(f.read_text(encoding="utf-8")):
            assert bloco_rotulo in bloco, (
                f"{f.name} :: {titulo!r} sem bloco {bloco_rotulo!r}"
            )


def test_ac2b_ordem_dos_blocos_preservada():
    """AC2: a ordem didática é o que torna a leitura coerente."""
    for f in MODS:
        if f.name in NAO_MODULO:
            continue
        for titulo, bloco in _secoes(f.read_text(encoding="utf-8")):
            pos = [bloco.find(b) for b in BLOCOS]
            assert all(p >= 0 for p in pos), (
                f"{f.name} :: {titulo!r} bloco ausente ({pos})"
            )
            assert pos == sorted(pos), f"{f.name} :: {titulo!r} fora de ordem ({pos})"


# ------------------------------------------------------- AC3
@pytest.mark.parametrize("modulo", ["mod-11-apendices.tex", "mod-13-ativacao-agentes.tex",
                                    "mod-14-lote-categorias.tex"])
def test_ac3_modulos_de_uso_com_leitura_guiada(modulo):
    """AC3: os três módulos que ensinam o uso do sistema foram fechados."""
    f = LIVRO / modulo
    assert f.exists(), f"{modulo} ausente"
    secs = _secoes(f.read_text(encoding="utf-8"))
    assert len(secs) == 1, f"{modulo}: {len(secs)} seções de leitura guiada"


# ------------------------------------------------------- AC4
def test_ac4_novas_secoes_citam_biblioteca_verificada():
    """AC4 (R110): nenhuma seção nova pode afirmar sem lastro verificável."""
    bibliografia = (LIVRO / "mod-11-apendices.tex").read_text(encoding="utf-8")
    dois_dois = re.compile(r"10\.\d{4,9}/[^\s}{]+")  # para no fechamento do campo
    dois_validos = set(dois_dois.findall(bibliografia))
    assert dois_validos, "bibliografia sem DOI recognized"
    for modulo in ("mod-11-apendices.tex", "mod-13-ativacao-agentes.tex",
                   "mod-14-lote-categorias.tex"):
        t = (LIVRO / modulo).read_text(encoding="utf-8")
        for _, bloco in _secoes(t):
            assert "\\citref{" in bloco, f"{modulo}: seção sem \\citref"
            for doi in dois_dois.findall(bloco):
                assert doi in dois_validos, f"{modulo}: DOI fora da biblioteca: {doi}"


# ------------------------------------------------------- AC5
def test_ac5_numeros_das_queries_derivam_do_repositorio():
    """AC5: os números das seções novas precisam ser os medidos, não estimados."""
    import json

    cfg = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    n_agentes = len(cfg["agent"])
    refs = (LIVRO / "mod-11-apendices.tex").read_text(encoding="utf-8").count("\\begin{referencia}")
    calls = sum(
        len(re.findall(r"\\citref\{", f.read_text(encoding="utf-8"))) for f in MODS
    )
    fichas_condensadas = len(
        re.findall(r"\\elemento\{ficha-", (LIVRO / "mod-14-lote-categorias.tex").read_text(encoding="utf-8"))
    )
    t11 = (LIVRO / "mod-11-apendices.tex").read_text(encoding="utf-8")
    t14 = (LIVRO / "mod-14-lote-categorias.tex").read_text(encoding="utf-8")

    def presente(txt: str, n: int) -> bool:
        return re.search(rf"(?<![\d.,]){n}(?![\d.,])", txt) is not None

    assert presente(t11, refs), f"Módulo 11 deve citar as {refs} referências medidas"
    assert presente(t11, calls), f"Módulo 11 deve citar as {calls} chamadas medidas"
    assert presente(t14, fichas_condensadas), (
        f"Módulo 14 deve citar as {fichas_condensadas} fichas condensadas medidas"
    )
    assert presente(t14, n_agentes), f"Módulo 14 deve citar os {n_agentes} agentes do runtime"
