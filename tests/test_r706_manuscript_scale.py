"""Testes RED/GREEN da SPEC-935-R706 — Motor de produção em escala.

Suíte hermética: nenhum subprocess real, rede ou LLM; runners injetáveis
via tmp_path e monkeypatch; nenhum código do repositório é modificado.
"""
import os

import pytest

from research.manuscript.config import ArticleConfig, TIPOS
from research.manuscript import scaffold as scaffold_mod
from research.manuscript import texparse
from research.manuscript import gates as gates_mod
from research.manuscript import pipeline as pipeline_mod


def _cfg(**kw):
    base = dict(titulo="Brincar e atenção em pré-escolares",
                autores=["Autora Um", "Autora Dois"],
                area="Psicologia", tipo="revisao-integrativa")
    base.update(kw)
    return ArticleConfig(**base)


# ---------------------------------------------------------------- AC1: config
def test_config_valida_gera_slug_e_modulos():
    cfg = _cfg()
    assert cfg.slug == "brincar-e-atencao-em-pre-escolares"
    assert "introducao" in cfg.modulos and "referencias" in cfg.modulos


def test_config_rejeita_tipo_invalido():
    with pytest.raises(ValueError):
        _cfg(tipo="poesia-concreta")


def test_config_rejeita_titulo_e_autores_vazios():
    with pytest.raises(ValueError):
        _cfg(titulo="  ")
    with pytest.raises(ValueError):
        _cfg(autores=["  "])


def test_tipos_cobrem_cinco_modalidades():
    assert set(TIPOS) == {"revisao-integrativa", "estudo-de-caso", "artigo-original",
                          "tcc", "dissertacao"}


# ---------------------------------------------------------------- AC2: scaffold
def test_scaffold_cria_workspace_isolado(tmp_path):
    cfg = _cfg(saida_base=str(tmp_path))
    saida = scaffold_mod.scaffold_workspace(cfg)
    ws = os.path.join(str(tmp_path), cfg.slug)
    assert saida["workspace"] == ws
    for rel in ["main.tex", "modulos/introducao.tex", "referencias.bib",
                "triagem.jsonl", "README.md"]:
        assert os.path.isfile(os.path.join(ws, rel)), rel
    with open(os.path.join(ws, "main.tex"), encoding="utf-8") as fh:
        assert "\\input{modulos/introducao}" in fh.read()


def test_scaffold_nega_sobrescrita_sem_force(tmp_path):
    cfg = _cfg(saida_base=str(tmp_path))
    scaffold_mod.scaffold_workspace(cfg)
    with pytest.raises(FileExistsError):
        scaffold_mod.scaffold_workspace(cfg)
    # com force, recria sem erro
    saida = scaffold_mod.scaffold_workspace(cfg, force=True)
    assert saida["total"] > 0


# ---------------------------------------------------------------- texparse
TAB_FIXTURE = (
    "\\begin{tabular}{p{2cm} p{4cm}}\n\\toprule\n"
    "\\textbf{Domínio} & \\textbf{Antes} \\\\\n\\midrule\n"
    "Atenção & Não parava \\\\\nHiperatividade & Corria \\\\\n\\bottomrule\n"
    "\\end{tabular}"
)

BBL_FIXTURE = (
    "\\bibitem[Autor 2020]{autor2020}\n\\abntrefinfo{Autor}{AUTOR}{2020}\n"
    "{AUTOR, A. \\textbf{Título do livro}. Cidade: Ed, 2020.}\n\n"
    "\\bibitem[Outro 2021]{outro2021}\n\\abntrefinfo{Outro}{OUTRO}{2021}\n"
    "{OUTRO, B. Artigo qualquer. \\textbf{Revista}, v. 1, 2021.}\n"
)


def test_parse_tabular_cabecalho_linhas_regras():
    cabec, linhas = texparse.parse_tabular(TAB_FIXTURE)
    assert len(cabec) == 2
    assert len(linhas) == 2
    assert linhas[0][0] == "Atenção"


def test_parse_bbl_duas_referencias_com_negrito():
    refs = texparse.parse_bbl(BBL_FIXTURE)
    assert len(refs) == 2
    assert "\\textbf{" in refs[0]


def test_citacoes_expandem_autor_data():
    aux = ("\\bibcite{autor2020}{Autor 2020}\n"
           "\\bibciteYEAR{autor2020}{2020}\n")
    c = texparse.Citacoes(aux)
    assert c.rotulo("autor2020") == "AUTOR, 2020"


def test_iter_blocos_reconhece_tipos():
    tex = ("\\section{Introdução}\n\nTexto um.\n\n"
           "\\subsection{Pergunta}\n\nTexto dois.\n\n"
           "\\begin{enumerate}\n\\item a) primeiro\n\\end{enumerate}\n")
    tipos = [b[0] for b in texparse.iter_blocos(tex)]
    assert tipos == ["secao", "para", "subsecao", "para", "item"]


# ---------------------------------------------------------------- AC4: gates
def _workspace_gates(tmp_path):
    ws = os.path.join(str(tmp_path), "art")
    os.makedirs(os.path.join(ws, "modulos"))
    with open(os.path.join(ws, "a.tex"), "w", encoding="utf-8") as fh:
        fh.write("Texto com \\cite{ok2020} e \\cite{falta2021}.\n")
    with open(os.path.join(ws, "r.bib"), "w", encoding="utf-8") as fh:
        fh.write("@book{ok2020,\n author={Ok},\n}\n")
    return ws


def test_gates_citacoes_indefinidas(tmp_path):
    ws = _workspace_gates(tmp_path)
    r = gates_mod.run_gates(ws)
    assert r["ok"] is True
    assert r["citacoes"]["indefinidas"] == ["falta2021"]
    assert r["citacoes"]["pronto"] is False


def test_gates_diretorio_inexistente():
    r = gates_mod.run_gates("/tmp/opencode/inexistente-r706-xyz")
    assert r["ok"] is False


def test_gates_forca_alegacao_sinaliza(tmp_path):
    r = gates_mod.run_gates(str(tmp_path), texto="Este estudo prova que tudo cura sempre.")
    assert r["alegacoes"]["total"] >= 1


# ---------------------------------------------------------------- AC5: lote
def test_produzir_lote_isola_falhas(tmp_path, monkeypatch):
    import integrations.artigo_academico_mcp as mcp
    monkeypatch.setattr(mcp.subprocess, "run",
                        lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError("sem git")))
    c1 = _cfg(titulo="Artigo um", saida_base=str(tmp_path))
    c2 = _cfg(titulo="Artigo dois", saida_base=str(tmp_path))
    lote = pipeline_mod.produzir_lote([c1, c2])
    assert lote["total"] == 2 and lote["concluidos"] == 2
    assert {r["slug"] for r in lote["resultados"]} == {c1.slug, c2.slug}
    # segunda rodada sem force: ambos falham isoladamente, sem derrubar o lote
    lote2 = pipeline_mod.produzir_lote([c1, c2])
    assert lote2["concluidos"] == 0
    assert all("FileExistsError" in r["erro"] for r in lote2["resultados"])


# ---------------------------------------------------------------- AC6: pptx_theme fail-closed
def test_pptx_theme_falha_fechada_sem_dependencia():
    from research.manuscript import pptx_theme
    try:
        import pptx  # noqa: F401
        pytest.skip("python-pptx instalado; guarda não acionada aqui")
    except ImportError:
        with pytest.raises(RuntimeError):
            pptx_theme.nova_apresentacao()


# ---------------------------------------------------------------- AC3: docx_builder genérico
def test_docx_builder_generico(tmp_path):
    pytest.importorskip("docx")
    from research.manuscript import docx_builder
    ws = os.path.join(str(tmp_path), "art")
    os.makedirs(os.path.join(ws, "modulos"))
    with open(os.path.join(ws, "main.tex"), "w", encoding="utf-8") as fh:
        fh.write("\\input{modulos/01-capa}\n\\input{modulos/02-corpo}\n")
    with open(os.path.join(ws, "modulos", "01-capa.tex"), "w", encoding="utf-8") as fh:
        fh.write("\\begin{center}\n{\\bfseries TÍTULO}\n\\end{center}\n")
    with open(os.path.join(ws, "modulos", "02-corpo.tex"), "w", encoding="utf-8") as fh:
        fh.write("\\section{Introdução}\n\nTexto com \\cite{autor2020}.\n\n"
                 "\\begin{quadro}{Quadro 1 -- Teste}\n"
                 "\\begin{tabular}{p{2cm} p{4cm}}\n\\toprule\nA & B \\\\\n\\midrule\n"
                 "c1 & c2 \\\\\n\\bottomrule\n\\end{tabular}\n\\end{quadro}\n")
    with open(os.path.join(ws, "main.aux"), "w", encoding="utf-8") as fh:
        fh.write("\\bibcite{autor2020}{Autor 2020}\n\\bibciteYEAR{autor2020}{2020}\n")
    with open(os.path.join(ws, "main.bbl"), "w", encoding="utf-8") as fh:
        fh.write("\\bibitem[Autor 2020]{autor2020}\n{AUTOR, A. \\textbf{Livro}. Cid: Ed, 2020.}\n")
    saida = os.path.join(ws, "saida.docx")
    r = docx_builder.build_docx(ws, saida)
    assert os.path.isfile(saida)
    assert r["tabelas"] == 1 and r["referencias"] == 1
    import zipfile
    with zipfile.ZipFile(saida) as zf:
        xml = zf.read("word/document.xml").decode("utf-8")
    assert "(AUTOR, 2020)" in xml
    assert "Quadro 1" in xml
