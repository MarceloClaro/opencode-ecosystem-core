# -*- coding: utf-8 -*-
"""Testes R411 — Versão LaTeX/PDF de submissão RBEP.

Requisitos (SPEC-935-R411):
1. .tex compilável com pdflatex (A4, 12pt, margens ABNT, 1.5 espaçamento).
2. Conteúdo idêntico em substância ao ARTIGO_RBEP_SUBMISSAO.md (R410):
   trilinguismo, resumo/abstract/resumen, palavras-chave, 6 seções, 6
   tabelas, 16 referências ABNT em ordem alfabética com DOI.
3. Corpo sem avisos editoriais; termos bloqueados e linguagem causal ausentes.
4. Números e tabelas idênticos ao MD (proveniência R409) — nada alterado.
5. PDF gerado, não vazio, sem erros de compilação.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent / "academic/papers/arm_education_audit"
LATEX_DIR = BASE / "latex"
TEX = LATEX_DIR / "ARTIGO_RBEP_SUBMISSAO.tex"
PDF = LATEX_DIR / "ARTIGO_RBEP_SUBMISSAO.pdf"
MD = BASE / "ARTIGO_RBEP_SUBMISSAO.md"

TERMOS_BLOQUEADOS = [
    "Qualis A1", "qualis a1", "validado", "validada", "inédito", "inédita",
    "condição necessária", "condicao necessaria", "16,06", "0,997", "0.997",
    "AUC", "percentil", "efeito causal", "causalidade",
    "impulsiona", "leva a",
]

# R412: números centrais do manuscrito expandido (painel de 135 países,
# controles WGI, erros clusterizados). Positivos sem sinal (LaTeX usa $-$).
NUMEROS_CENTRAIS = [
    "0,751", "0,146", "0,542", "0,003", "0,073", "0,169", "0,314", "0,555",
    "0,694", "0,609", "0,615", "0,769", "0,133", "0,194", "0,88", "0,96",
    "27,34", "27,49", "4,21", "1,72", "49,76", "24,28", "0,93", "0,91",
    "0,92", "9,5", "0,5",
]


class TestArquivoTex:
    def test_tex_existe(self):
        assert TEX.exists(), "latex/ARTIGO_RBEP_SUBMISSAO.tex ausente"

    def test_documentclass(self):
        texto = TEX.read_text(encoding="utf-8")
        assert re.search(r"\\documentclass\[[^\]]*12pt[^\]]*\]\{article\}", texto)
        assert "a4paper" in texto

    def test_begin_end_document(self):
        texto = TEX.read_text(encoding="utf-8")
        assert "\\begin{document}" in texto
        assert "\\end{document}" in texto

    def test_margens_abnt(self):
        texto = TEX.read_text(encoding="utf-8")
        # margem esquerda/superior 3cm, direita/inferior 2cm (ABNT)
        assert "left=3cm" in texto or "left=3.0cm" in texto
        assert "top=3cm" in texto
        assert "right=2cm" in texto
        assert "bottom=2cm" in texto

    def test_espacamento_15(self):
        texto = TEX.read_text(encoding="utf-8")
        assert "onehalfspacing" in texto or "\\setstretch{1.5}" in texto

    def test_fonte_times(self):
        texto = TEX.read_text(encoding="utf-8")
        assert "newtxtext" in texto or "times" in texto


class TestConteudoTrilingue:
    def test_titulo_em_3_idiomas(self):
        texto = TEX.read_text(encoding="utf-8")
        assert "Título:" in texto
        assert "Title:" in texto
        assert "Título en español" in texto

    def test_resumo_abstract_resumen(self):
        texto = TEX.read_text(encoding="utf-8")
        for secao in ["Resumo", "Abstract", "Resumen"]:
            assert secao in texto, f"seção '{secao}' ausente no .tex"

    def test_resumos_nao_vazios(self):
        texto = TEX.read_text(encoding="utf-8")
        for secao in ["Resumo", "Abstract", "Resumen"]:
            idx = texto.index(secao)
            trecho = texto[idx : idx + 2000]
            palavras = len(trecho.split())
            assert palavras >= 60, f"{secao} muito curto ({palavras} palavras)"

    def test_palavras_chave_3_idiomas_3_a_5(self):
        texto = TEX.read_text(encoding="utf-8")
        for secao in ["Palavras-chave", "Keywords", "Palabras clave"]:
            idx = texto.index(secao)
            bloco = "\n".join(texto[idx : idx + 400].split("\n")[0:3])
            termos = [t.strip() for t in bloco.split(";") if t.strip()]
            assert 3 <= len(termos) <= 5, (
                f"{secao} com {len(termos)} termos (esperado 3–5)"
            )


class TestAntiOverclaim:
    @pytest.mark.parametrize("termo", TERMOS_BLOQUEADOS)
    def test_termo_proibido_ausente(self, termo):
        texto = TEX.read_text(encoding="utf-8")
        assert termo not in texto, f"termo bloqueado presente: '{termo}'"

    def test_sem_linguagem_causal(self):
        texto = TEX.read_text(encoding="utf-8")
        for causal in ["determina", "garante", "assegura que", "prova que"]:
            assert causal not in texto.lower()
        # Refinamento R414 (alinhado ao gate R413): "causa" e "prova" como
        # palavra são alegações; adjetivos/advérbios ("causais", "provável")
        # em contexto não assertivo são aceitáveis.
        assert not re.search(r"\bcausa\b", texto, re.IGNORECASE), (
            "uso não-negado de 'causa' no .tex"
        )

    @pytest.mark.parametrize("termo", ["candidat", "aguarda revisão",
                                       "revisão por pares", "submissão",
                                       "Qualis", "manuscrito gerado em",
                                       "status:"])
    def test_aviso_editorial_ausente(self, termo):
        texto = TEX.read_text(encoding="utf-8")
        assert termo not in texto.lower(), f"aviso editorial no .tex: '{termo}'"


class TestNumeros:
    @pytest.mark.parametrize("numero", NUMEROS_CENTRAIS)
    def test_numeros_centrais_presentes(self, numero):
        texto = TEX.read_text(encoding="utf-8")
        corpo = texto.split("Referências")[0]
        assert numero in corpo, f"número {numero} ausente do corpo do .tex"

    def test_numeros_identicos_ao_md(self):
        """Todo número decimal do corpo do MD deve aparecer no corpo do .tex.

        Números de cabeçalho de seção do MD (ex.: "4.5 Painel com efeitos
        fixos") são excluídos: o LaTeX numera as seções automaticamente.
        """
        md = MD.read_text(encoding="utf-8")
        tex = TEX.read_text(encoding="utf-8")
        md_corpo = md.split("Referências")[0]
        tex_corpo = tex.split("Referências")[0]
        # remove linhas de cabeçalho de seção do MD (números estruturais)
        linhas_sem_secao = [
            l for l in md_corpo.splitlines() if not l.strip().startswith("#")
        ]
        md_sem_secoes = "\n".join(linhas_sem_secao)
        decimais_md = set(re.findall(r"-?\d+[.,]\d+", md_sem_secoes))
        tex_compacto = tex_corpo.replace(" ", "")
        for d in decimais_md:
            if d not in tex_compacto:
                # números como 1,20e-89 podem ter sido convertidos; aceitar
                # apenas se for notação científica presente no MD
                assert re.match(r"-?\d+,\d+e-\d+$", d), (
                    f"número '{d}' do MD ausente no .tex"
                )

    def test_sem_placeholders(self):
        texto = TEX.read_text(encoding="utf-8")
        corpo = texto.split("Referências")[0]
        assert "..." not in corpo


class TestCitacoesEReferencias:
    def test_citacoes_autor_data_caixa_alta(self):
        texto = TEX.read_text(encoding="utf-8")
        corpo = texto.split("Referências")[0]
        # mesmo critério do R410 (NBR 10520): autor(es) em caixa alta + ano
        padroes = [
            r"\([A-ZÀ-Ú][A-ZÀ-Ú\s;]*,\s*(19|20)\d{2}\)",
            r"\([A-ZÀ-Ú][A-ZÀ-Ú\s;]*;?\s*[A-ZÀ-Ú][A-ZÀ-Ú\s;]*;?\s*,\s*(19|20)\d{2}\)",
        ]
        ocorrencias = sum(len(re.findall(p, corpo)) for p in padroes)
        assert ocorrencias >= 10, f"apenas {ocorrencias} citações autor-data"

    def test_referencias_ordem_alfabetica(self):
        texto = TEX.read_text(encoding="utf-8")
        bloco = texto.split("Referências")[-1]
        linhas = [l.strip() for l in bloco.splitlines()
                  if l.strip() and "textbf" in l]
        sobrenomes = [l.split(",")[0].upper() for l in linhas]
        assert len(sobrenomes) >= 12, f"apenas {len(sobrenomes)} referências"
        assert sobrenomes == sorted(sobrenomes), "referências fora de ordem alfabética"

    def test_referencias_com_doi(self):
        texto = TEX.read_text(encoding="utf-8")
        bloco = texto.split("Referências")[-1]
        dois = re.findall(r"DOI:\s*10\.\d{4,}", bloco)
        assert len(dois) >= 8, f"apenas {len(dois)} DOIs nas referências"


class TestRegressaoNumeracaoTabelas:
    """Bug R411: \caption* + \path{} incrementava o contador de tabelas
    (Tabela 2 virava 3, 4, 5...). Causa raiz: \path (verbatim-like) dentro
    de \caption* (moving argument). Correção: fontes como texto normal."""

    def test_sem_caption_estrelado(self):
        texto = TEX.read_text(encoding="utf-8")
        assert "\\caption*" not in texto, (
            "\\caption* presente: reincidência do bug de numeração"
        )

    def test_fontes_fora_de_caption(self):
        texto = TEX.read_text(encoding="utf-8")
        # fonte deve aparecer como \par após \end{tabular}, nunca em \caption
        for bloco in texto.split("\\end{tabular}")[1:]:
            assert "Fonte:" in bloco[:400], (
                "fonte ausente após \\end{tabular}"
            )

    def test_pdf_tabela_2_correta(self):
        """Se pdftotext estiver disponível, confere a numeração no PDF."""
        if not shutil.which("pdftotext"):
            pytest.skip("pdftotext indisponível")
        if not PDF.exists():
            pytest.skip("PDF ainda não compilado")
        saida = subprocess.run(
            ["pdftotext", "-layout", str(PDF), "-"],
            capture_output=True, timeout=60,
        ).stdout.decode("utf-8", errors="replace")
        assert "Tabela 2: Correlações entre matrícula terciária" in saida, (
            "PDF sem 'Tabela 2: Correlações entre matrícula terciária' "
            "(numeração deslocada)"
        )
        assert "Tabela 5: Correlação em níveis com exclusão" not in saida, (
            "LOOCV ainda rotulada como Tabela 5 (bug de numeração)"
        )


class TestCompilacao:
    def test_pdflatex_disponivel(self):
        assert shutil.which("pdflatex"), "pdflatex não está no PATH"

    def test_tex_compila_e_gera_pdf(self):
        if not shutil.which("pdflatex"):
            pytest.skip("pdflatex indisponível")
        assert TEX.exists(), "arquivo .tex ausente para compilação"
        resultado = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", str(LATEX_DIR), str(TEX)],
            capture_output=True, timeout=180,
        )
        saida = (resultado.stdout or b"") + (resultado.stderr or b"")
        assert resultado.returncode == 0, (
            "pdflatex falhou:\n"
            + saida.decode("utf-8", errors="replace")[-3000:]
        )
        assert PDF.exists(), "PDF não foi gerado"
        assert PDF.stat().st_size > 0, "PDF gerado está vazio"
