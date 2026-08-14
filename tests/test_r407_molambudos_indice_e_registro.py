# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R407: Índice de Fragmentos e registro de tratamento.

Dois defeitos que sobreviveram a todos os ciclos anteriores porque nenhuma
verificação olhava para lá.

**O índice.** Num livro-hipertexto o Índice de Fragmentos é o instrumento com
que o leitor localiza um fragmento pelo nome --- e ele estava mantido à mão em
quatro arquivos independentes. Divergiu: a edição inglesa listava 73 dos 84
fragmentos (faltavam DOC-20 a DOC-27, incluindo ``O Homem do Pano Preto'',
LUC-13, LUC-14 e MEM-27); a chinesa e a trilíngue ainda rotulavam DOC-26 com o
ano **1981**, que o R406 removeu do corpus por contradizer o cânone; DOC-09
anunciava a escala do ``1.261'' --- Oliveira --- quando o fragmento é a escala
do **1.263**, o leitor; e MEM-27 tinha um título por edição, repetindo em
português o título de MEM-26.

**O tratamento.** Em chinês, 您 é o tratamento formal e 你 o íntimo. Os
fragmentos de Contaminação --- a parte em que a obra fala com o leitor ---
usavam 您 em 528 ocorrências contra 1: uma convenção deliberada e clínica, que
é metade do efeito. Mas o aparato (índice, frontmatter, mapas, dossiê) tratava
o leitor por 你, e o dossiê acadêmico citava a obra com o pronome errado. Num
livro cujo mecanismo é interpelar o leitor, o pronome não pode oscilar.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BOOK = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"

pytestmark = pytest.mark.skipif(not BOOK.is_dir(), reason="corpus fora do controle de versão")


# --------------------------------------------------------------- índice ----
def test_indice_integro_nas_quatro_edicoes():
    from scripts.molambudos_indice import verificar

    problemas = verificar()
    assert not problemas, "índice divergente:\n" + "\n".join(f"  {p}" for p in problemas)


def test_toda_edicao_indexa_os_84_fragmentos():
    from scripts.molambudos_indice import estrutura_pt

    esperado = [fid for _, ents in estrutura_pt() for fid, _ in ents]
    assert len(esperado) == 84
    for arq, regex in (
        ("main.tex", r"\\fraglink\{([A-Z]{3,4}-[A-Za-z0-9-]+)\}"),
        ("en/main_en.tex", r"\\fraglink\{([A-Z]{3,4}-[A-Za-z0-9-]+)\}"),
        ("zh/main_zh.tex", r"\\fraglink\{([A-Z]{3,4}-[A-Za-z0-9-]+)\}"),
        ("tri/main_tri.tex", r"\\fraglinktri\{([A-Z]{3,4}-[A-Za-z0-9-]+)\}"),
    ):
        achados = re.findall(regex, (BOOK / arq).read_text(encoding="utf-8"))
        assert achados == esperado, (
            f"{arq}: índice diverge da edição de referência "
            f"(faltam {sorted(set(esperado) - set(achados))})")


def test_nenhum_titulo_de_fragmento_se_repete_dentro_da_mesma_edicao():
    """MEM-27 chamava-se ``A Última Página'' --- igual a MEM-26."""
    for pasta in ("fragmentos", "en/fragmentos", "zh/fragmentos"):
        titulos: dict[str, str] = {}
        for p in sorted((BOOK / pasta).rglob("*.tex")):
            m = re.search(r"\\section\*\{\\textbf\{[^}]+\}\s*---\s*(.+?)\}\s*$",
                          p.read_text(encoding="utf-8"), re.M)
            if not m:
                continue
            t = m.group(1).strip()
            assert t not in titulos, f"{pasta}: {p.stem} e {titulos[t]} têm o título {t!r}"
            titulos[t] = p.stem


def test_verificador_de_indice_acusa_entrada_removida(tmp_path, monkeypatch):
    """Um verificador que não falha quando o defeito volta é decoração."""
    from scripts import molambudos_indice as indice

    original = (BOOK / "en/main_en.tex").read_text(encoding="utf-8")
    alvo = "\\fraglink{DOC-25}"
    assert alvo in original, "DOC-25 deveria estar no índice inglês"
    linha = next(l for l in original.splitlines() if l.startswith(alvo))
    try:
        (BOOK / "en/main_en.tex").write_text(original.replace(linha + "\n", ""), encoding="utf-8")
        problemas = indice.verificar()
        assert any("DOC-25" in p for p in problemas), f"não acusou a remoção: {problemas}"
    finally:
        (BOOK / "en/main_en.tex").write_text(original, encoding="utf-8")
    assert not indice.verificar(), "o índice não voltou ao estado íntegro"


# ------------------------------------------------------------ tratamento ----
def _conta(caminhos, char: str) -> int:
    return sum(p.read_text(encoding="utf-8").count(char) for p in caminhos)


def test_contaminacao_trata_o_leitor_so_por_voce_formal():
    """A obra fala com o leitor em 您; personagens falam entre si em 你."""
    cont = sorted((BOOK / "zh/fragmentos/cont").rglob("*.tex"))
    assert cont, "fragmentos CONT chineses não encontrados"
    informal = _conta(cont, "你")
    assert informal == 0, f"{informal} ocorrência(s) de 你 na Contaminação chinesa"
    assert _conta(cont, "您") > 400


def test_aparato_chines_nao_oscila_no_tratamento_do_leitor():
    aparato = [BOOK / "zh/main_zh.tex", BOOK / "tri/main_tri.tex", BOOK / "dossie/dossie_zh.tex"]
    aparato += sorted((BOOK / "zh/frontmatter").glob("*.tex"))
    aparato += sorted((BOOK / "tri/frontmatter").glob("*.tex"))
    culpados = [p.relative_to(BOOK).as_posix() for p in aparato
                if p.is_file() and "你" in p.read_text(encoding="utf-8")]
    assert not culpados, f"aparato ainda trata o leitor por 你: {culpados}"


def test_dialogo_entre_personagens_preserva_o_tratamento_intimo():
    """A correção não podia formalizar a fala das personagens nas memórias."""
    mem = sorted((BOOK / "zh/fragmentos/mem").rglob("*.tex"))
    assert _conta(mem, "你") > 100, "o 你 das memórias foi apagado junto"


# ---------------------------------------------------------------- cânone ----
def test_canone_cobre_o_aparato_e_nao_so_os_fragmentos():
    from scripts.molambudos_canone import verificar

    r = verificar()
    assert r["arquivos_de_aparato"] > 50, "o aparato saiu da cobertura do verificador"
    assert r["ok"], r["problemas"]


def test_arvore_canonica_acompanha_a_edicao():
    """Havia uma segunda cópia do corpus, e ela ficou dois ciclos para trás.

    `projetos/molambudos/fragmentos` não entra em nenhum build, mas guardava
    ainda o «Dr. Heitor Oliveira faleceu em 1981» que o R406 removeu — só da
    edição. Uma cópia fora de verificação vira fonte de contradição na primeira
    vez que alguém a usar.
    """
    from scripts.molambudos_canone import BOOK, CANON

    if not CANON.is_dir():
        pytest.skip("árvore canônica ausente")
    divergentes = [p.relative_to(CANON).as_posix() for p in sorted(CANON.rglob("*.tex"))
                   if (BOOK / "fragmentos" / p.relative_to(CANON)).is_file()
                   and (BOOK / "fragmentos" / p.relative_to(CANON)).read_text(
                       encoding="utf-8") != p.read_text(encoding="utf-8")]
    assert not divergentes, f"árvore canônica fora de sincronia: {divergentes}"


def test_canone_acusa_arvore_canonica_dessincronizada():
    from scripts import molambudos_canone as canone

    alvo = canone.CANON / "doc" / "DOC-07.tex"
    if not alvo.is_file():
        pytest.skip("árvore canônica ausente")
    original = alvo.read_text(encoding="utf-8")
    try:
        alvo.write_text(original.replace("desapareceu em 13 de junho de 1979, dois meses",
                                         "faleceu em 1981, dois anos"), encoding="utf-8")
        r = canone.verificar()
        assert not r["ok"], "divergência na árvore canônica passou despercebida"
        tipos = {p["tipo"] for p in r["problemas"]}
        assert {"contradição", "cópia divergente"} <= tipos, tipos
    finally:
        alvo.write_text(original, encoding="utf-8")
    assert canone.verificar()["ok"]


def test_canone_acusa_contradicao_reintroduzida_no_indice():
    """O 1981 sobreviveu no índice justamente porque nada o lia."""
    from scripts import molambudos_canone as canone

    alvo = BOOK / "zh/main_zh.tex"
    original = alvo.read_text(encoding="utf-8")
    assert "{奥利维拉的笔记——机制}{1979}" in original
    try:
        alvo.write_text(original.replace("{奥利维拉的笔记——机制}{1979}",
                                         "{奥利维拉的笔记——机制}{1981}"), encoding="utf-8")
        r = canone.verificar()
        assert not r["ok"], "1981 no índice passou despercebido"
        assert any(p["edicao"] == "aparato" and "zh/main_zh.tex" in p.get("arquivos", [])
                   for p in r["problemas"]), r["problemas"]
    finally:
        alvo.write_text(original, encoding="utf-8")
    assert canone.verificar()["ok"]
