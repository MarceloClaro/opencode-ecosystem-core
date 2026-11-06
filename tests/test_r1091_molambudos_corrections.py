"""R1091: correções críticas do miolo Molambudos R1075.

Os testes descrevem o estado *corrigido*. Eles devem falhar no estado anterior
à aplicação (RED) e passar depois da compilação (GREEN).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "literatura/molambudos/Molambudos_Revisada_R1075"
FRAG = BOOK / "fragmentos"
REPORT = ROOT / "reports/r1091/avaliacao_critica_pos_correcao.md"


def read(rel: str) -> str:
    return (BOOK / rel).read_text(encoding="utf-8")


def fragments() -> list[Path]:
    return sorted(p for p in FRAG.rglob("*.tex") if "_removidos" not in str(p))


def test_62_cluster_is_consistent() -> None:
    doc01 = read("fragmentos/doc/DOC-01.tex")
    assert "A do 1.260 era recente. Pelo mapa, 1979." in doc01
    assert "sessenta e dois dias depois" in doc01
    assert "morto há 62 dias" in doc01
    assert "morto há 62 anos" not in doc01
    assert "enterrado com um paciente em 1917" not in doc01
    assert doc01.count("Notas do coveiro Genésio Barbosa") == 1

    assert "poucos dias. O que mais poderia acontecer?" in read("fragmentos/doc/DOC-21.tex")
    assert "Durante 62 dias, o diário cresceu dentro da terra" in read("fragmentos/cont/CONT-01.tex")
    assert "sessenta e quatro anos" in read("fragmentos/mem/MEM-26.tex")
    assert "É uma assinatura, não um calendário." in read("fragmentos/doc/DOC-26.tex")


def test_lucia_timeline_and_custody_are_explicit() -> None:
    luc06 = read("fragmentos/luc/LUC-06.tex")
    assert "não foi vista em público desde então" in luc06
    assert "voltou ao prédio em julho" in luc06

    luc12 = read("fragmentos/luc/LUC-12.tex")
    assert "peguei de volta no cofre em julho" in luc12

    doc20 = read("fragmentos/doc/DOC-20.tex")
    assert "guardou o objeto entre 2019 e 2026" in doc20

    luc14 = read("fragmentos/luc/LUC-14.tex")
    assert "modificado pela última vez em 12 de maio" in luc14
    assert "Não há outro registro de acesso posterior" in luc14

    assert "A caligrafia sugere 1956. Não há datação." in read("fragmentos/luc/LUC-03.tex")
    assert "O ciclo já tinha começado." in read("fragmentos/luc/LUC-05.tex")
    assert "o crânio que ela supunha ser de Oliveira" in read("fragmentos/luc/LUC-09.tex")
    assert "A primeira leitura integral do diário ocorreu em abril." in read("fragmentos/luc/LUC-10.tex")
    assert "Antes de devolvê-lo, em maio, passou duas semanas digitando" in read("fragmentos/luc/LUC-11.tex")


def test_documentary_frame_is_consistent() -> None:
    doc19 = read("fragmentos/doc/DOC-19.tex")
    assert "uma invenção que se apoia nos 60 mil" in doc19
    assert "Trecho citado para fins de contexto histórico" in doc19
    assert "um dos 60 mil" not in doc19
    assert "Transcrição autorizada" not in doc19

    doc05 = read("fragmentos/doc/DOC-05.tex")
    assert "reação traumática crônica" in doc05
    assert "Transtorno de Estresse Pós-Traumático" not in doc05

    doc07 = read("fragmentos/doc/DOC-07.tex")
    assert "cronologia do prontuário" in doc07
    assert "cronologia ficcional" not in doc07
    assert "\\textbf{Eixo" not in doc07

    doc12 = read("fragmentos/doc/DOC-12.tex")
    assert "anos seguintes" in doc12
    assert "anos 80" not in doc12

    doc27 = read("fragmentos/doc/DOC-27.tex")
    assert "na margem da ficha de catalogação, em caligrafia não identificada" in doc27
    assert "ficha de catalogação de 1916" not in doc27

    assert "Clorpromazina 100mg. Duas vezes ao dia." in read("fragmentos/doc/DOC-06.tex")
    assert "no dia da morte do paciente 1.260" in read("fragmentos/doc/DOC-13.tex")
    assert "Durante a análise das páginas" in read("fragmentos/doc/DOC-24.tex")


def test_navigation_is_consistent() -> None:
    main = read("main.tex")
    raw = [
        line for path in fragments()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("> **↪ Rotas:**")
    ]
    assert not raw, f"rotas em Markdown literal: {raw[:3]}"

    calls = sum(len(re.findall(r"\\rota\{", p.read_text(encoding="utf-8"))) for p in fragments())
    assert calls == 223, calls
    assert "223 rotas" in main
    assert "223 conexões" in main
    assert "Investigação Lúcia (26)" in main
    assert "Contaminação (7)" in main
    assert "223 rotas" in read("frontmatter/como_ler.tex")

    for frag in ("LUC-13.tex", "LUC-15.tex", "CONT-07.tex", "CONT-13.tex"):
        assert "\\margnota{" not in read(f"fragmentos/{'luc' if frag.startswith('LUC') else 'cont'}/{frag}")
    assert "\\NE{o som de folhas sendo viradas" in read("fragmentos/luc/LUC-13.tex")
    assert "incorporadas aos documentos" in main


def test_paratexts_are_harmonized() -> None:
    assert "Se precisar parar, pare." in read("frontmatter/cuidado.tex")
    assert "Formulário opcional, sem valor clínico." in read("frontmatter/ficha_beta_diegetica.tex")
    nota = read("frontmatter/nota_historica.tex")
    assert "A versão narrativa do Colônia é ficcional; a instituição histórica existiu" in nota
    assert "estimativas históricas" in nota
    arquivista = read("frontmatter/nota_arquivista.tex")
    assert "O prontuário de Joaquim, porém, é uma reconstituição ficcional" in arquivista
    assert "segundo Daniela Arbex" in arquivista
    assert "narrado no exame ficcional" in read("frontmatter/glossario_historico.tex")
    editorial = read("frontmatter/nota_editorial.tex")
    assert "Novembro de 2026" in editorial
    assert "Nota sobre os documentos" in editorial
    assert "2. ed. rev." in read("frontmatter/ficha_catalografica.tex")
    assert "2.ª edição revista" in read("frontmatter/copyrightpage.tex")
    epilogo = read("fragmentos/epilogo_revisado.tex")
    assert "edição impressa" in epilogo
    assert "o ciclo se completou" in epilogo
    assert "diagnóstico está confirmado" not in epilogo


def test_interior_excludes_cover_and_backcover() -> None:
    title = read("frontmatter/titlepage.tex")
    assert "capa.png" not in title
    main = read("main.tex")
    assert "frontmatter/backpage" not in main
    assert "frontmatter/colofao" in main
    colofao = read("frontmatter/colofao.tex")
    assert "979-8-18-917049-2" in colofao
    assert "978-65-01-23456-7" not in colofao


def test_pdf_and_manifests_are_updated() -> None:
    fitz = pytest.importorskip("fitz")
    pdf_path = BOOK / "main_kdp_pt_160x230mm.pdf"
    assert pdf_path.is_file()
    pdf = fitz.open(pdf_path)
    assert 415 <= pdf.page_count <= 430
    text = "\n".join(page.get_text() for page in pdf)
    assert "> **↪ Rotas:" not in text
    assert "um dos 60 mil" not in text
    assert "978-65-01-23456-7" not in text
    assert "979-8-18-917049-2" in text
    first = pdf[0]
    assert abs(first.rect.width - 453.543) < 0.5
    assert abs(first.rect.height - 651.968) < 0.5

    digest = __import__("hashlib").sha256(pdf_path.read_bytes()).hexdigest()
    manifest = json.loads((ROOT / "reports/r1075/revision_manifest.json").read_text(encoding="utf-8"))
    assert manifest["revised"]["pdf_sha256"] == digest
    design = json.loads((ROOT / "reports/r1076/design_manifest.json").read_text(encoding="utf-8"))
    assert design["pdf"]["sha256"] == digest
    assert design["pdf"]["pages"] == pdf.page_count


def test_correction_report_has_rubric_and_limits() -> None:
    assert REPORT.is_file()
    text = REPORT.read_text(encoding="utf-8")
    assert "rubrica" in text.lower()
    assert "10 critérios" in text.lower() or "dez critérios" in text.lower()
    assert "não certifica" in text.lower()
    assert "10/10" in text
