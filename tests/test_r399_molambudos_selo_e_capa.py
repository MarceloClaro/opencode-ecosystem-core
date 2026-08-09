# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R399: selo de integridade verificável e capa de impressão.

Dois artefatos de publicação que existiam sem nenhuma guarda:

1. `SELO_INTEGRIDADE_MERKLE.json` era um JSON avulso — ninguém o gerava,
   ninguém o conferia. Declarava 74 fragmentos (o corpus tem 84), 359 páginas,
   e nenhum dos hashes correspondia aos arquivos reais. Agora é produzido e
   conferido por `scripts/molambudos_selo.py`, e este teste falha se o selo
   ficar defasado em relação ao corpus.

2. A capa de impressão tinha lombada dimensionada para ~623 páginas e painéis
   num trim diferente do miolo, e o PDF entregue renderizava o conteúdo fora
   da página. A capa de brochura 160×230mm é gerada a partir de parâmetros e
   sua geometria é conferida aqui contra a paginação real do miolo.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BOOK = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"

MIOLO_PT = BOOK / "main_kdp_pt_160x230mm.pdf"
CAPA_PT = BOOK / "capa_completa_pt_160x230mm.pdf"
CAPA_TEX = BOOK / "capa_completa_pt_160x230mm.tex"

TRIM_L_IN = 160.0 / 25.4
TRIM_A_IN = 230.0 / 25.4
SANGRIA_IN = 0.125
ESPESSURA_COR_BRANCO = 0.002347   # in/página, impressão em cor da KDP

fitz = pytest.importorskip("fitz", reason="PyMuPDF ausente")


def _selo(acao: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "scripts.molambudos_selo", acao],
        cwd=ROOT, capture_output=True, text=True,
    )


# ---------------------------------------------------------------------------
# Selo de integridade
# ---------------------------------------------------------------------------


def test_selo_confere_com_o_corpus_atual():
    """Se um fragmento mudou sem o selo ser regerado, isto falha.

    É o ponto inteiro do exercício: um selo que ninguém confere não sustenta
    alegação nenhuma de proveniência.
    """
    resultado = _selo("verificar")
    assert resultado.returncode == 0, (
        "selo defasado em relação ao corpus — rode "
        f"`python3 -m scripts.molambudos_selo gerar`:\n{resultado.stderr}"
    )


def test_selo_cobre_os_fragmentos_das_tres_edicoes():
    """R405: o selo cobria apenas o corpus português.

    A lacuna apareceu na prática: dois fragmentos chineses foram substituídos
    por inteiro (CONT-05 e DOC-26, que contradiziam a cronologia da obra) e o
    merkle root não se moveu. Um selo que não reage a mudança de conteúdo numa
    das edições publicadas atesta um terço da obra, não a obra.
    """
    import json

    selo = json.loads((BOOK / "SELO_INTEGRIDADE_MERKLE.json").read_text(encoding="utf-8"))
    reais = sum(
        len(list((BOOK / edicao).rglob("*.tex")))
        for edicao in ("fragmentos", "en/fragmentos", "zh/fragmentos")
    )
    assert selo["total_fragmentos"] == reais, (
        f"selo cobre {selo['total_fragmentos']} fragmentos; as três edições somam {reais}"
    )
    assert len(selo["fragmentos"]) == reais
    cobertas = {f["arquivo"].split("/")[0] for f in selo["fragmentos"]}
    assert cobertas == {"fragmentos", "en", "zh"}, f"edições cobertas: {cobertas}"


def test_selo_declara_explicitamente_o_que_nao_atesta():
    """Contra a reincidência do problema: um artefato de aparência criptográfica
    que o leitor confunde com validação externa."""
    import json

    selo = json.loads((BOOK / "SELO_INTEGRIDADE_MERKLE.json").read_text(encoding="utf-8"))
    escopo = selo.get("escopo", "")
    assert "NÃO constitui validação externa" in escopo
    assert "algoritmo" in selo and "merkle-sha256-v1" in selo["algoritmo"]


def test_merkle_root_muda_quando_um_fragmento_muda():
    from scripts.molambudos_selo import merkle_root

    a = merkle_root(["00" * 32, "11" * 32, "22" * 32])
    b = merkle_root(["00" * 32, "11" * 32, "23" * 32])
    assert a != b
    assert merkle_root([]) != a


# ---------------------------------------------------------------------------
# Capa de impressão
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not MIOLO_PT.is_file(), reason="miolo PT de impressão não construído")
def test_miolo_pt_tem_o_trim_de_160x230mm():
    with fitz.open(MIOLO_PT) as doc:
        largura_mm = doc[0].rect.width / 72 * 25.4
        altura_mm = doc[0].rect.height / 72 * 25.4
    assert abs(largura_mm - 160.0) < 0.5, f"largura {largura_mm:.2f}mm"
    assert abs(altura_mm - 230.0) < 0.5, f"altura {altura_mm:.2f}mm"


@pytest.mark.skipif(
    not (MIOLO_PT.is_file() and CAPA_PT.is_file()),
    reason="miolo ou capa de impressão não construídos",
)
def test_lombada_da_capa_corresponde_a_paginacao_real_do_miolo():
    """A KDP recusa capa cuja lombada não corresponda à contagem de páginas.

    A capa anterior tinha lombada de 1.404in — dimensionada para ~623 páginas —
    enquanto os miolos existentes tinham 415 e 1115.
    """
    with fitz.open(MIOLO_PT) as doc:
        paginas = doc.page_count
    with fitz.open(CAPA_PT) as doc:
        capa_l = doc[0].rect.width / 72
        capa_a = doc[0].rect.height / 72

    lombada_esperada = paginas * ESPESSURA_COR_BRANCO
    largura_esperada = 2 * SANGRIA_IN + 2 * TRIM_L_IN + lombada_esperada
    altura_esperada = 2 * SANGRIA_IN + TRIM_A_IN

    assert abs(capa_l - largura_esperada) < 0.01, (
        f"largura da capa {capa_l:.4f}in; esperada {largura_esperada:.4f}in "
        f"para {paginas} páginas"
    )
    assert abs(capa_a - altura_esperada) < 0.01, (
        f"altura da capa {capa_a:.4f}in; esperada {altura_esperada:.4f}in"
    )


@pytest.mark.skipif(not CAPA_TEX.is_file(), reason="fonte da capa ausente")
def test_a_paginacao_declarada_na_capa_bate_com_o_miolo():
    import re

    texto = CAPA_TEX.read_text(encoding="utf-8")
    m = re.search(r"\\def\\Paginas\{(\d+)\}", texto)
    assert m, "a fonte da capa não declara \\Paginas"
    declarado = int(m.group(1))
    if not MIOLO_PT.is_file():
        pytest.skip("miolo PT de impressão não construído")
    with fitz.open(MIOLO_PT) as doc:
        assert declarado == doc.page_count, (
            f"capa declara {declarado} páginas; o miolo tem {doc.page_count}"
        )


@pytest.mark.skipif(not CAPA_PT.is_file(), reason="capa não construída")
def test_a_capa_desenha_conteudo_dentro_da_pagina():
    """A capa dura entregue (capa_completa.pdf) tinha todo o conteúdo empurrado
    para fora da página: `overlay` sem ancorar em `current page.south west` faz
    as coordenadas partirem do ponto de texto corrente. Sobrava um retângulo
    escuro com uma tira no topo."""
    with fitz.open(CAPA_PT) as doc:
        pagina = doc[0]
        rect = pagina.rect
        imagens = pagina.get_images()
        assert len(imagens) >= 2, "capa e contracapa deveriam estar presentes"
        # Um render da metade inferior não pode ser uniforme: se o conteúdo
        # estivesse fora da página, sobraria só o preenchimento de fundo.
        meio = fitz.Rect(rect.x0, rect.y0 + rect.height / 2, rect.x1, rect.y1)
        pix = pagina.get_pixmap(clip=meio, dpi=20)
        cores = {pix.pixel(x, y) for x in range(0, pix.width, 7) for y in range(0, pix.height, 7)}
        assert len(cores) > 12, f"metade inferior praticamente uniforme ({len(cores)} cores)"


def test_selo_nao_grava_paginacao_zero_de_pdf_em_construcao(tmp_path, monkeypatch):
    """Um PDF sendo reescrito por um build concorrente abre e reporta 0 páginas.

    Gravar esse zero seria pior que não gravar nada: o selo passaria a afirmar,
    com aparência de fato medido, uma paginação que nunca existiu — e é a
    paginação que determina a largura da lombada da capa.
    """
    from scripts import molambudos_selo as selo

    truncado = tmp_path / "meio_build.pdf"
    truncado.write_bytes(b"%PDF-1.7\n")          # cabeçalho sem páginas
    monkeypatch.setattr(selo, "BOOK", tmp_path)
    assert selo._paginas("meio_build.pdf") is None

    ausente = selo._paginas("nao_existe.pdf")
    assert ausente is None


def test_selo_registra_a_paginacao_das_quatro_edicoes_de_impressao():
    import json

    selo = json.loads((BOOK / "SELO_INTEGRIDADE_MERKLE.json").read_text(encoding="utf-8"))
    for lingua in ("pt", "en", "zh", "tri"):
        chave = f"paginas_impressao_{lingua}_160x230mm"
        assert chave in selo, f"selo não registra a paginação de impressão {lingua}"


def test_cada_edicao_de_impressao_tem_wrapper_com_jobname_proprio():
    """Quatro wrappers chamados main_kdp_print_160x230mm.tex — raiz, en/, zh/ e
    tri/ — produziam o MESMO PDF: quem compilasse dois sobrescrevia o outro."""
    esperados = [
        "main_kdp_pt_160x230mm.tex", "main_kdp_en_160x230mm.tex",
        "main_kdp_zh_160x230mm.tex", "main_kdp_tri_160x230mm.tex",
    ]
    for nome in esperados:
        assert (BOOK / nome).is_file(), f"falta o wrapper de impressão {nome}"
    # `_archive/` guarda os backups de cada ciclo e deve preservá-los como
    # estavam — a colisão só importa no corpus ativo, que é o que se compila.
    colidentes = [
        p for p in BOOK.rglob("main_kdp_print_160x230mm.tex")
        if "_archive" not in p.parts
    ]
    assert not colidentes, (
        f"wrappers com basename colidente ainda existem: {colidentes}"
    )
