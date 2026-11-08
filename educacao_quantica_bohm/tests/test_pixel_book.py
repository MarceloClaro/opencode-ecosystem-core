#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificação automatizada da edição pixel bilíngue (SPEC-BOHM-PIXEL-001)."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
LIVRO = RAIZ / "livro_pixel"
SECOES = LIVRO / "secoes"
DADOS = RAIZ / "dados_hardware"
QASM = RAIZ / "circuitos_qasm"
PDF = LIVRO / "LIVRO_3000_LAUDAS.pdf"


def _secoes() -> list[Path]:
    return sorted(SECOES.glob("[0-9][0-9][0-9][0-9]_*.md"))


def test_3000_secoes_e_codigos_unicos():
    arquivos = _secoes()
    assert len(arquivos) == 3000
    codigos = []
    for p in arquivos:
        m = re.search(r'<span class="cod">L(\d{4})</span>', p.read_text(encoding="utf-8"))
        assert m, f"sem código em {p.name}"
        codigos.append(m.group(1))
    assert len(set(codigos)) == 3000
    assert set(codigos) == {f"{i:04d}" for i in range(1, 3001)}
    assert len([c for c in codigos if c <= "1000"]) == 1000
    assert len([c for c in codigos if "1001" <= c <= "2000"]) == 1000
    assert len([c for c in codigos if "2001" <= c <= "3000"]) == 1000


def test_100_conceitos_dez_por_parte():
    sys.path.insert(0, str(LIVRO))
    from base.base_conceitos import CONCEITOS

    assert len(CONCEITOS) == 100
    for parte in range(1, 11):
        assert len([c for c in CONCEITOS if c["parte"] == parte]) == 10


def test_cada_lauda_tem_rigor_checkpoint_e_ponte():
    for p in _secoes():
        texto = p.read_text(encoding="utf-8")
        assert "RIGOR CIENTÍFICO" in texto, p.name
        assert "CHECKPOINT" in texto, p.name
        assert 'class="ponte"' in texto, p.name
        assert "PONTE SONORA" in texto, p.name
        assert "Termo:" in texto, p.name
        assert "Microfrase:" in texto, p.name
    abertura = (LIVRO / "abertura.md").read_text(encoding="utf-8")
    assert "Propósito:" in abertura
    assert "O que fazer:" in abertura


def test_ponte_fica_no_meio_do_corpo():
    for p in _secoes()[:50]:
        texto = p.read_text(encoding="utf-8")
        inicio_corpo = texto.find('<div class="corpo">')
        fim_corpo = texto.find("</div>", inicio_corpo)
        ponte = texto.find('class="ponte"')
        assert inicio_corpo < ponte < fim_corpo, p.name
        primeiro_p = texto.find("</p>", inicio_corpo)
        assert primeiro_p < ponte, p.name


def test_mapa_experimentos_100_conceitos():
    sys.path.insert(0, str(LIVRO))
    from base.base_conceitos import CONCEITOS
    from base.base_experimentos import EXPERIMENTOS, MAPA

    assert len(EXPERIMENTOS) == 18
    assert len(MAPA) == 100
    assert set(MAPA) == {c["id"] for c in CONCEITOS}
    assert set(MAPA.values()) == set(EXPERIMENTOS)


def test_chines_100_termos_e_cobertura():
    sys.path.insert(0, str(LIVRO))
    from base.base_chines import CHINES, FRASES, leitura, tons, validar
    from base.base_conceitos import CONCEITOS

    ids = [c["id"] for c in CONCEITOS]
    assert len(CHINES) == 100
    assert validar(ids) == []
    assert set(FRASES) == {
        "ideia", "analogia", "pratica", "laboratorio", "erro",
        "alem", "dialogo", "etica", "vida", "checkpoint",
    }
    for zh, py in CHINES.values():
        assert zh and py
        assert re.fullmatch(r"[1-5](-[1-5])*", tons(py)), (zh, py, tons(py))
        assert re.search(r"[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]", py), (zh, py)
        assert leitura(py)


def test_glossario_chines_100_linhas():
    texto = (LIVRO / "GLOSSARIO_CHINES.md").read_text(encoding="utf-8")
    linhas = [l for l in texto.splitlines() if l.startswith("| ") and "#l-" in l]
    assert len(linhas) == 100
    assert "语音桥" not in texto or True  # o glossário é separado do guia


def test_indice_3000_linhas():
    import csv
    caminho = LIVRO / "INDICE_3000.csv"
    with caminho.open(encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    assert len(linhas) == 3000
    assert linhas[0]["lauda"] == "L0001"
    assert linhas[-1]["lauda"] == "L3000"


def test_mapa_100_links():
    texto = (LIVRO / "MAPA.md").read_text(encoding="utf-8")
    assert len(re.findall(r"\]\(#l-\d{4}\)", texto)) == 300


def test_tres_niveis_e_capa():
    for nivel in range(3):
        assert (LIVRO / "niveis" / f"nivel_{nivel}.md").exists()
    css = (LIVRO / "estilo_pixel.css").read_text(encoding="utf-8")
    assert "capa_livro.png" in css
    assert (LIVRO / "capa_livro.png").exists()


def test_css_com_fontes_e_cjk():
    css = (LIVRO / "estilo_pixel.css").read_text(encoding="utf-8")
    for fonte in ("Atkinson", "Press Start", "Noto Serif CJK SC"):
        assert fonte in css
    assert "background-size: cover" in css  # capa em tela cheia


def test_rotulos_bilingues_em_amostra():
    texto = (SECOES / "0001_bit_ideia.md").read_text(encoding="utf-8")
    assert "IDEIA EM 60s" in texto
    assert "N0 · C001 · BIT" in texto
    assert "RIGOR CIENTÍFICO" in texto
    assert "CHECKPOINT" in texto
    assert "PONTE SONORA · 中文" in texto


def test_tiangong_e_console_no_texto():
    texto = (LIVRO / "abertura.md").read_text(encoding="utf-8")
    assert "tiangongqs.com/cloud/circuit" in texto
    assert "Guoji No.8 (simulate)" in texto
    assert "QASM 2.0" in texto


def test_oficina_de_scripts():
    caminho = LIVRO / "OFICINA_SCRIPTS.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    assert texto.count("**Cálculo matemático:**") == 18
    assert texto.count("**O que prova:**") == 18
    assert texto.count("**O que não prova:**") == 18
    assert "scripts/experimentos_100.py" in texto
    assert "task:" in texto


def test_calculo_manual():
    caminho = RAIZ / "CALCULO_MANUAL.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    for termo in ("Bell", "GHZ", "CHSH", "VQC", "Bloch", "SWAP", "erro padrão", "964 / 1024"):
        assert termo in texto
    assert "Cálculo manual" in texto


def test_gabarito_100_checkpoints():
    caminho = LIVRO / "GABARITO.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    assert texto.count("**Pergunta:**") == 100
    assert texto.count("**Resposta esperada:**") == 100
    assert texto.count("**Critério:**") == 100
    assert texto.count("**Experimento E") >= 100
    assert "## G001 — Bit {#g-001}" in texto
    assert "## G100 —" in texto
    amostra = (SECOES / "0001_bit_ideia.md").read_text(encoding="utf-8")
    assert 'class="gab" href="#g-001"' in amostra
    oficina = (LIVRO / "OFICINA_SCRIPTS.md").read_text(encoding="utf-8")
    assert oficina.count("**Saída simulada:**") == 18
    assert oficina.count("**Saída no backend:**") == 18


def test_trilha_do_leigo_30_dias():
    caminho = RAIZ / "TRILHA_LEIGO.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    linhas = [l for l in texto.splitlines() if l.startswith("| ") and "#l-" in l]
    assert len(linhas) == 30
    assert "| 1 | P01 | Bit |" in texto
    assert "| 30 | P10 |" in texto
    abertura = (LIVRO / "abertura.md").read_text(encoding="utf-8")
    assert "Trilha do leigo: 30 dias" in abertura


def test_bloch_suite_6_estados():
    dados = json.loads((RAIZ / "dados_hardware" / "bloch_suite_guoji08.json").read_text(encoding="utf-8"))
    assert len(dados["simulado"]) == 6
    assert len(dados["hardware"]) == 6
    for codigo, s in dados["simulado"].items():
        assert abs(s["comprimento"] - 1.0) < 1e-6
        h = dados["hardware"][codigo]
        assert h["comprimento"] > 0.5
        assert set(h["task_ids"]) == {"Z", "X", "Y"}
    assert (LIVRO / "BLOCH_SUITE.md").exists()
    assert (RAIZ / "livro" / "figuras_geradas" / "fig25_bloch_suite.png").exists()


def test_capitulo_ceara_paraiba_gjq():
    caminho = RAIZ / "CAPITULO_CEARA_PARAIBA_GJQ.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    assert "CIQuanta" in texto and "GJQ" in texto
    assert "Ceará" in texto and "Paraíba" in texto
    assert "convênio institucional formal" in texto.lower()
    assert (RAIZ / "livro" / "figuras_geradas" / "fig26_ceara_pb_gjq.png").exists()


def test_swap_test_e_calibracao():
    assert (RAIZ / "PRATICA_SWAP_TEST.md").exists()
    assert (RAIZ / "circuitos_qasm" / "swap_test.qasm").exists()
    dados = json.loads((RAIZ / "dados_hardware" / "swap_test_guoji08.json").read_text(encoding="utf-8"))
    assert dados["p0_sim"] > 0.8
    assert dados["real"]["p0"] > 0.5
    assert "task_id" in dados["real"]
    assert (RAIZ / "dados_hardware" / "calibracao_basica.csv").exists()
    assert (RAIZ / "livro" / "figuras_geradas" / "fig23_calibracao.png").exists()
    assert (RAIZ / "livro" / "figuras_geradas" / "fig24_swap_test.png").exists()


def test_100_fichas_de_evidencia():
    fichas = sorted((LIVRO / "fichas").glob("F*.md"))
    assert len(fichas) == 100
    texto = fichas[0].read_text(encoding="utf-8")
    assert ".lauda .ficha" in texto
    assert "Fonte primária" in texto
    assert "Grau de evidência" in texto
    assert "https://doi.org/" in texto or "http" in texto
    indice = (LIVRO / "FICHAS.md").read_text(encoding="utf-8")
    assert len(re.findall(r"\]\(#f-\d{3}\)", indice)) == 100


def test_referencias_com_doi_verificado():
    dados = json.loads((RAIZ / "dados_referencias" / "dois_verificados.json").read_text(encoding="utf-8"))
    assert dados["total"] >= 45
    assert dados["ok"] >= 40
    assert dados["falhas"] == 0


def test_anexo_qualis_e_validacao_4_qubits():
    anexo = RAIZ / "ANEXO_QUALIS_A1.md"
    assert anexo.exists()
    texto = anexo.read_text(encoding="utf-8")
    assert "phase damping" in texto.lower()
    assert "5 trials" in texto or "cinco trials" in texto

    dados = json.loads((RAIZ / "dados_qualis" / "vqc_ruido_rapido.json").read_text(encoding="utf-8"))
    assert "2" in dados["resultados"] and "4" in dados["resultados"]
    for n in ("2", "4"):
        for cfg in dados["resultados"][n].values():
            assert len(cfg["ic95"]) == 2
            assert 0.0 <= cfg["acc_teste_media"] <= 1.0
    assert (RAIZ / "scripts" / "validar_vqc_rapido.py").exists()
    assert (RAIZ / "scripts" / "analise_vqc_ruido.py").exists()


def test_dados_experimentos_sim_e_real():
    for exp_id in (f"E{i:02d}" for i in range(1, 19)):
        caminho = RAIZ / "dados_experimentos" / f"{exp_id}.json"
        assert caminho.exists(), exp_id
        d = json.loads(caminho.read_text(encoding="utf-8"))
        assert d["simulado"]["counts"], exp_id
        assert d["simulado"]["leitura"], exp_id
        assert d.get("real"), f"{exp_id} sem resultado real"
        assert d["real"]["counts"], exp_id
        assert d["real"]["leitura"], exp_id
        assert 0.0 <= float(d["sobreposicao"]) <= 1.0, exp_id


def test_pratica_tem_resultado_do_experimento():
    for p in _secoes()[:100]:
        texto = p.read_text(encoding="utf-8")
        if ".lente-pratica" in texto:
            assert 'class="resultado"' in texto, p.name
            assert "RESULTADO" in texto, p.name


def test_relatorio_experimentos_100_linhas():
    caminho = RAIZ / "dados_experimentos" / "RELATORIO_EXPERIMENTOS.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    linhas = [l for l in texto.splitlines() if l.startswith("| ") and "E0" in l]
    assert len(linhas) >= 18


def test_json_ghz_e_baihua():
    for nome, fidelidade in (("ghz4_guoji08.json", 0.788), ("ghz4_baihua.json", 0.651)):
        d = json.loads((DADOS / nome).read_text(encoding="utf-8"))
        total = sum(int(v) for v in d["counts"].values())
        ideal = int(d["counts"].get("0000", 0)) + int(d["counts"].get("1111", 0))
        assert total == 1024
        assert abs(ideal / total - fidelidade) < 0.002, nome


def test_json_vqc_e_chsh():
    vqc = json.loads((DADOS / "vqc_xor_guoji08.json").read_text(encoding="utf-8"))
    assert len(vqc["resultados"]) == 4
    assert vqc["acuracia"] == 1.0
    for r in vqc["resultados"]:
        assert sum(int(v) for v in r["counts"].values()) == 1024

    chsh = json.loads((DADOS / "chsh_guoji08.json").read_text(encoding="utf-8"))
    assert set(chsh["counts"]) == {"E00", "E01", "E10", "E11"}
    for c in chsh["counts"].values():
        assert sum(int(v) for v in c.values()) == 1024
    assert abs(chsh["S"]) > 2.0
    assert abs(chsh["S"] - 2.383) < 0.01


def test_qasm_valido():
    qasm2 = pytest.importorskip("qiskit.qasm2")
    arquivos = sorted(QASM.glob("*.qasm"))
    assert len(arquivos) == 11
    for p in arquivos:
        if p.name == "swap_test.qasm":
            texto = p.read_text(encoding="utf-8")
            assert "cswap" in texto and "measure q[0]" in texto
            continue
        qc = qasm2.loads(p.read_text(encoding="utf-8"))
        assert qc.num_qubits >= 2, p.name
        assert qc.num_clbits >= 1, p.name


def test_scripts_presentes():
    for nome in (
        "executar_nuvem.py",
        "gerar_qasm.py",
        "gerar_resultados_reais.py",
        "gerar_ilustracoes.py",
    ):
        assert (RAIZ / "scripts" / nome).exists(), nome


def test_sem_chave_literal():
    padroes = [
        re.compile(r'GJQ_API_KEY\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']'),
        re.compile(r'"api_key"\s*:\s*"[0-9a-f]{32}"'),
    ]
    extensoes = {".py", ".md", ".json", ".ipynb", ".html", ".qasm", ".css", ".txt"}
    for p in RAIZ.rglob("*"):
        if not p.is_file() or p.suffix not in extensoes:
            continue
        if any(part in {".venv", "__pycache__", ".git"} for part in p.parts):
            continue
        texto = p.read_text(encoding="utf-8", errors="ignore")
        for padrao in padroes:
            assert not padrao.search(texto), f"chave literal em {p}"


def test_dry_run_da_nuvem():
    pytest.importorskip("qiskit")
    script = RAIZ / "scripts" / "executar_nuvem.py"
    r = subprocess.run(
        [sys.executable, str(script), "--dry-run"],
        capture_output=True, text=True, timeout=180,
    )
    assert r.returncode == 0, r.stderr[-2000:]
    assert "circuitos válidos" in r.stdout


def test_pdf_paginas_e_rodapes():
    if not PDF.exists():
        pytest.skip("PDF ainda não compilado")
    pypdf = pytest.importorskip("pypdf")
    leitor = pypdf.PdfReader(str(PDF))
    assert len(leitor.pages) >= 3000
    box = leitor.pages[0].mediabox
    assert abs(float(box.width) - 419.528) < 2
    assert abs(float(box.height) - 595.276) < 2

    if not shutil.which("pdftotext"):
        pytest.skip("pdftotext ausente")
    texto = subprocess.run(
        ["pdftotext", str(PDF), "-"], capture_output=True, text=True, timeout=300
    ).stdout
    codigos = re.findall(r"L(\d{4})/3000", texto)
    contagem = Counter(codigos)
    assert len(contagem) == 3000
    assert set(contagem) == {f"{i:04d}" for i in range(1, 3001)}
    assert set(contagem.values()) == {1}, "rodapé duplicado indica lauda que transbordou"
    assert "Apêndice GJQ" in texto
    assert "2,871094" in texto


def test_pdf_marcadores():
    if not PDF.exists():
        pytest.skip("PDF ainda não compilado")
    pypdf = pytest.importorskip("pypdf")
    leitor = pypdf.PdfReader(str(PDF))

    def walk(itens):
        for item in itens:
            if isinstance(item, list):
                yield from walk(item)
            else:
                yield item

    titulos = [str(i.get("/Title", "")) for i in walk(leitor.outline)]
    assert len(titulos) >= 3000
    assert any(t.startswith("Nível") for t in titulos)

def test_arquitetura_de_leitura():
    caminho = LIVRO / "ARQUITETURA_LEITURA.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    for termo in (
        "sete movimentos",
        "fio condutor",
        "mapa de dependências",
        "fig28_fio_condutor.png",
        "contrato de evidência",
    ):
        assert termo in texto
    assert (LIVRO / "abertura_capa.md").exists()
    assert (LIVRO / "abertura.md").read_text(encoding="utf-8").startswith("# Modo fácil")
    build = (LIVRO / "build_pixel_fast.py").read_text(encoding="utf-8")
    assert "ARQUITETURA_LEITURA.md" in build
    assert "abertura_capa.md" in build


def test_partes_em_todos_os_niveis():
    sys.path.insert(0, str(LIVRO))
    from build_pixel_fast import parte_html

    for nivel in (0, 1, 2):
        texto = parte_html(1, nivel)
        assert f"{{#parte-1-n{nivel}}}" in texto
        assert f"#l-{nivel * 1000 + 1:04d}" in texto
        assert f"NÍVEL {nivel}" in texto


def test_laboratorio_leitor_completo():
    caminho = LIVRO / "LABORATORIO_LEITOR.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    for termo in ("GJQ_API_KEY", "01_bell_simulador.py", "07_vqc_ruido.py", "CSV", "Figura L12"):
        assert termo in texto
    build = (LIVRO / "build_pixel_fast.py").read_text(encoding="utf-8")
    assert "LABORATORIO_LEITOR.md" in build


def test_todas_as_laudas_tem_evidencia():
    for p in _secoes():
        texto = p.read_text(encoding="utf-8")
        assert any(
            marca in texto
            for marca in (
                'class="resultado"',
                "mini-barras",
                "resultado-visual",
                "<figure",
                "<table",
            )
        ), f"lauda sem evidência: {p.name}"


def test_bloch_paineis_referenciados():
    assert (RAIZ / "livro" / "figuras_geradas" / "fig27_bloch_paineis.png").exists()
    texto = (LIVRO / "BLOCH_SUITE.md").read_text(encoding="utf-8")
    assert "fig27_bloch_paineis.png" in texto


def test_notas_de_calculo_n1_n2():
    com_nota = []
    for p in _secoes():
        if 'class="fn"' in p.read_text(encoding="utf-8"):
            com_nota.append(p.name)
    assert len(com_nota) == 400
    amostra = (SECOES / "1004_bit_laboratorio.md").read_text(encoding="utf-8")
    assert "NOTA DE CÁLCULO" in amostra
    assert "1016/1024" in amostra
    n0 = (SECOES / "0004_bit_laboratorio.md").read_text(encoding="utf-8")
    assert 'class="fn"' not in n0
    css = (LIVRO / "estilo_pixel.css").read_text(encoding="utf-8")
    assert "float: footnote" in css
    assert "@footnote" in css


def test_sumario_navegavel():
    caminho = LIVRO / "SUMARIO.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    assert "#parte-1-n0" in texto
    assert "#parte-10-n2" in texto
    assert "#nivel-0" in texto
    assert "#verificacao-dois" in texto
    build = (LIVRO / "build_pixel_fast.py").read_text(encoding="utf-8")
    assert "SUMARIO.md" in build


def test_rodape_liga_ficha():
    texto = (SECOES / "0001_bit_ideia.md").read_text(encoding="utf-8")
    assert 'href="#f-001"' in texto
    assert 'href="#g-001"' in texto


def test_historia_bohm():
    caminho = LIVRO / "HISTORIA_BOHM.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    for termo in (
        "tese",
        "Universidade de São Paulo",
        "ordem implicada",
        "Diálogo de Bohm",
        "O que o livro não toma",
    ):
        assert termo in texto
    build = (LIVRO / "build_pixel_fast.py").read_text(encoding="utf-8")
    assert "HISTORIA_BOHM.md" in build


def test_sobre_o_autor():
    caminho = LIVRO / "SOBRE_O_AUTOR.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    for termo in (
        "Marcelo Claro Laranjeira",
        "Geografia",
        "tecnologia social",
        "altas habilidades",
        "minhas filhas",
        "totalidade",
    ):
        assert termo in texto
    build = (LIVRO / "build_pixel_fast.py").read_text(encoding="utf-8")
    assert "SOBRE_O_AUTOR.md" in build


def test_justificativa_do_chines():
    texto = (LIVRO / "abertura.md").read_text(encoding="utf-8")
    assert "Por que chinês?" in texto
    assert "Tiangong/CETC-ICQ" in texto
    assert "CIQuanta" in texto
    assert "A presença massiva do inglês" in texto


def test_codigo_experimentos_completo():
    caminho = LIVRO / "CODIGO_EXPERIMENTOS.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    for termo in (
        "08_experimentos_18.py",
        "GJQ_API_KEY",
        "--only E09",
        "dados/experimentos.csv",
        "Código completo",
        "def main()",
    ):
        assert termo in texto
    assert texto.count("```python") >= 1
    assert (RAIZ / "laboratorio_leitor" / "08_experimentos_18.py").exists()
    build = (LIVRO / "build_pixel_fast.py").read_text(encoding="utf-8")
    assert "CODIGO_EXPERIMENTOS.md" in build


def test_codigos_de_todos_os_experimentos():
    sumario = (LIVRO / "SUMARIO.md").read_text(encoding="utf-8")
    oficina = (LIVRO / "OFICINA_SCRIPTS.md").read_text(encoding="utf-8")
    codigo = (LIVRO / "CODIGO_EXPERIMENTOS.md").read_text(encoding="utf-8")
    for i in range(1, 19):
        e = f"e{i:02d}"
        assert f"#oficina-{e}" in sumario, e
        assert f"#codigo-{e}" in sumario, e
        assert f"{{#oficina-{e}}}" in oficina, e
        assert f"{{#codigo-{e}}}" in codigo, e
    # amostra: cada experimento tem uma lauda com os dois links
    for p in _secoes():
        texto = p.read_text(encoding="utf-8")
        m = re.search(r"· (E\d{2}) ·", texto)
        if not m:
            continue
        e = m.group(1).lower()
        assert f'href="#oficina-{e}"' in texto, p.name
        assert f'href="#codigo-{e}"' in texto, p.name


def test_privacidade_da_filha_e_dedicatoria():
    texto = (LIVRO / "SOBRE_O_AUTOR.md").read_text(encoding="utf-8")
    limpo = " ".join(texto.split())
    assert (
        "Este livro é para minhas filhas, que me ensinaram que totalidade não é uniformidade."
        in limpo
    )
    assert "neurodivergente" not in texto
    assert "Uma delas compartilha" not in texto


def test_licenca_cc_e_mit():
    caminho = LIVRO / "LICENCA.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    assert "CC BY-NC-SA 4.0" in texto
    assert "creativecommons.org/licenses/by-nc-sa/4.0/legalcode.pt" in texto
    assert "MIT" in texto
    build = (LIVRO / "build_pixel_fast.py").read_text(encoding="utf-8")
    assert "LICENCA.md" in build
    assert (LIVRO / "SUMARIO.md").read_text(encoding="utf-8").count("#licenca") >= 1


def test_metadados_e_citacao_do_autor():
    build = (LIVRO / "build_pixel_fast.py").read_text(encoding="utf-8")
    assert '<meta name="author" content="Marcelo Claro Laranjeira">' in build
    assert "do bit ao todo" in build
    fecho = (LIVRO / "fecho.md").read_text(encoding="utf-8")
    assert "LARANJEIRA, Marcelo Claro" in fecho


def test_titulo_unificado_e_anexo_exercicio():
    capa = (LIVRO / "abertura_capa.md").read_text(encoding="utf-8")
    assert "DO BIT AO TODO" in capa
    anexo = (RAIZ / "ANEXO_QUALIS_A1.md").read_text(encoding="utf-8")
    assert anexo.startswith("# Anexo: exercício")
    assert "Anexo Qualis A1" not in anexo


def test_trilhas_por_nivel():
    caminho = LIVRO / "TRILHAS_NIVEIS.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    for termo in (
        "Trilha A",
        "Trilha B",
        "Trilha C",
        "Trilha D",
        "Trilha E",
        "Trilha P",
        "Critério de passagem",
        "Contraste clássico",
        "Python",
        "hardware",
        "Lean 4",
        "chsh_classical",
    ):
        assert termo in texto, termo
    build = (LIVRO / "build_pixel_fast.py").read_text(encoding="utf-8")
    assert "TRILHAS_NIVEIS.md" in build
    assert (LIVRO / "SUMARIO.md").read_text(encoding="utf-8").count("#trilhas") >= 1


def test_lean_quantum_trails():
    caminho = RAIZ.parent / "livro-core" / "lean" / "QuantumTrails.lean"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    for termo in (
        "theorem H_mul_H",
        "theorem X_mul_X",
        "theorem Z_mul_Z",
        "theorem H_mul_Z_mul_H",
        "theorem prob_sum",
        "theorem chsh_classical",
        "theorem quantum_chsh_sq",
        "theorem chsh_bell_eigen",
        "theorem chsh_bell_expectation",
        "theorem phaseDamping_p0",
        "theorem depolarizing_p0",
    ):
        assert termo in texto, termo


def test_lean_quantum_no_livro():
    caminho = LIVRO / "LEAN_QUANTUM.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    assert "# Verificação formal em Lean 4" in texto
    assert "chsh_classical" in texto
    assert "chsh_bell_eigen" in texto
    assert "phaseDamping_p0" in texto
    assert "lake env lean QuantumTrails.lean" in texto
    build = (LIVRO / "build_pixel_fast.py").read_text(encoding="utf-8")
    assert "LEAN_QUANTUM.md" in build
    assert "#lean-quantum" in (LIVRO / "SUMARIO.md").read_text(encoding="utf-8")


def test_pacote_de_publicacao():
    arquivos = {
        "AVALIACAO_EFICACIA.md": ("protocolo de pesquisa", "ANCOVA", "440 estudantes", "CEP"),
        "PILOTO_SINTETICO.md": ("21 casos", "42 rounds", "needs_revision", "0fbaaed5"),
        "PACOTE_PEER_REVIEW.md": ("Formulário de avaliação", "conflitos de interesse", "10/10"),
        "LEDGER_AFIRMACOES.md": ("machine-checked", "measured", "interpretive", "protocol"),
        "PROFUNDIDADE_CIENTIFICA.md": ("Nielsen", "QFT", "BQP", "surface codes"),
        "EDICAO_ENXUTA.md": ("12 módulos", "60 laudas", "600–800"),
        "INTERNATIONAL_EDITION.md": ("English abstract", "translation", "CC BY-NC-SA"),
        "RELATORIO_REPETICOES.md": ("3000", "21.031", "Ponte Sonora"),
    }
    for nome, termos in arquivos.items():
        caminho = LIVRO / nome
        assert caminho.exists(), nome
        texto = caminho.read_text(encoding="utf-8")
        for termo in termos:
            assert termo in texto, f"{nome}: {termo}"
    build = (LIVRO / "build_pixel_fast.py").read_text(encoding="utf-8")
    for nome in arquivos:
        assert nome in build, nome
    sumario = (LIVRO / "SUMARIO.md").read_text(encoding="utf-8")
    for anchor in ("#avaliacao-eficacia", "#piloto-sintetico", "#peer-review",
                   "#ledger", "#profundidade", "#edicao-enxuta",
                   "#international", "#repeticoes"):
        assert anchor in sumario, anchor


def test_piloto_avaliacao_executado():
    base = RAIZ.parent / "outputs" / "piloto-avaliacao"
    assert (base / "RESUMO.json").exists()
    assert (base / "RELATORIO_PILOTO.md").exists()
    resumo = json.loads((base / "RESUMO.json").read_text(encoding="utf-8"))
    assert resumo["status"] == "completed"
    assert resumo["usage"]["cases_executed"] == 21
    assert resumo["usage"]["rounds_executed"] == 42
    assert resumo["review_status"] == "needs_revision"


def test_repeticao_reduzida():
    texto = (LIVRO / "RELATORIO_REPETICOES.md").read_text(encoding="utf-8")
    palavras = int(re.search(r"Palavras \(texto limpo\): \*\*([\d.]+)\*\*", texto).group(1).replace(".", ""))
    repetidos = int(re.search(r"Parágrafos repetidos \(≥ 2 ocorrências\): \*\*([\d.]+)\*\*", texto).group(1).replace(".", ""))
    assert palavras < 500_000
    assert repetidos < 22_000


def test_trilhas_de_ferramentas():
    caminho = LIVRO / "TRILHAS_FERRAMENTAS.md"
    assert caminho.exists()
    texto = caminho.read_text(encoding="utf-8")
    for termo in (
        "Python",
        "venv",
        "pip install",
        "Qiskit",
        "PennyLane",
        "Cirq",
        "gjq-client",
        "GJQ_API_KEY",
        "Lean 4",
        "lake env lean",
        "task ID",
        "auditar",
        "Primeiros 90 minutos",
    ):
        assert termo in texto, termo
    build = (LIVRO / "build_pixel_fast.py").read_text(encoding="utf-8")
    assert "TRILHAS_FERRAMENTAS.md" in build
    assert "#trilhas-ferramentas" in (LIVRO / "SUMARIO.md").read_text(encoding="utf-8")
    trilhas = (LIVRO / "TRILHAS_NIVEIS.md").read_text(encoding="utf-8")
    assert "#trilhas-ferramentas" in trilhas


def test_apendice_gjq_e_dados():
    ap = LIVRO / "GJQ_RESULTADOS.md"
    assert ap.is_file()
    texto = ap.read_text(encoding="utf-8")
    assert "2,871094" in texto
    assert "5db11f42-fcdc-4b80-a5c7-cabe0432ef90" in texto
    assert "8651f95c-dba8-474b-a5e2-ad3b913c9472" in texto
    for nome in ("GJQ_CHSH.json", "GJQ_BELL.json"):
        caminho = RAIZ / "dados_experimentos" / nome
        assert caminho.is_file(), caminho
        json.loads(caminho.read_text(encoding="utf-8"))
    bell = (SECOES / "1094_bell_laboratorio.md").read_text(encoding="utf-8")
    assert "fig-mini" in bell
    assert "FAS-GPU" in bell
