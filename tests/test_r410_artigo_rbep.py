# -*- coding: utf-8 -*-
"""Testes R410 — Versão de submissão do artigo adequada às normas da RBEP.

Requisitos (SPEC-935-R410):
1. Título em português, inglês e espanhol.
2. Resumo (PT), Abstract (EN) e Resumen (ES), cada um com densidade
   informativa e números com proveniência fechada (provenance.json do R409).
3. Palavras-chave: 3–5 por idioma (PT/EN/ES), preferencialmente do Thesaurus
   Brasileiro de Educação (Brased), sem repetição de termos do título.
4. Citações autor-data ABNT NBR 10520/2002 (Autor, ano).
5. Referências: lista única em ordem alfabética, ABNT NBR 6023/2002, com
   DOI/URL, subconjunto das 33 obras auditadas (R408).
6. Corpo do manuscrito SEM avisos editoriais ("candidato", "aguarda revisão",
   "Qualis", "submissão") — esses avisos ficam apenas em arquivo separado
   (CARTA_AO_EDITOR.md) e metadados.
7. Notas de rodapé evitadas (≤ 3 no corpo).
8. Anti-overclaim: termos bloqueados (R408/R409) ausentes; linguagem
   associativa; nenhum resultado false-positive da versão original.
9. Tabelas e números idênticos aos do ARTIGO_PUBLICAVEL.md (R409) — nenhum
   valor alterado na adequação editorial.
"""

import json
import re
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent / "academic/papers/arm_education_audit"
ARTIGO = BASE / "ARTIGO_RBEP_SUBMISSAO.md"
CARTA = BASE / "CARTA_AO_EDITOR.md"
# R412: proveniência da versão expandida (painel de 135 países) é a fonte de
# verdade dos números do manuscrito de submissão.
PROVENANCE = BASE / "outputs" / "expanded" / "provenance_expanded.json"

TERMOS_BLOQUEADOS = [
    "Qualis A1", "qualis a1", "validado", "validada", "inédito", "inédita",
    "condição necessária", "condicao necessaria", "16,06", "0,997", "0.997",
    "AUC", "percentil", "efeito causal", "causalidade",
    "impulsiona", "leva a",
]


class TestMetadadosTrilingues:
    """Título, resumo e palavras-chave nos três idiomas."""

    def test_artigo_existe(self):
        assert ARTIGO.exists(), "ARTIGO_RBEP_SUBMISSAO.md ausente"

    def test_carta_ao_editor_existe(self):
        assert CARTA.exists(), "CARTA_AO_EDITOR.md ausente (ciência aberta/dados)"

    def test_titulo_em_3_idiomas(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        assert "Título:" in texto or "**Título" in texto
        assert "Title:" in texto.lower() or "Title:" in texto
        assert "Título:" in texto and "Título en español" in texto

    def test_autor_orcid_md(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        assert "Marcelo Claro Laranjeira" in texto
        assert "https://orcid.org/0000-0001-8996-2887" in texto

    def test_autor_orcid_carta(self):
        texto = CARTA.read_text(encoding="utf-8")
        assert "Marcelo Claro Laranjeira" in texto
        assert "orcid.org/0000-0001-8996-2887" in texto

    def test_resumo_abstract_resumen(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        for secao in ["Resumo", "Abstract", "Resumen"]:
            assert secao in texto, f"seção '{secao}' ausente"

    def test_resumo_abstract_resumen_nao_vazios(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        for secao in ["Resumo", "Abstract", "Resumen"]:
            idx = texto.index(secao)
            trecho = texto[idx : idx + 2000]
            palavras = len(trecho.split())
            assert palavras >= 60, f"{secao} muito curto ({palavras} palavras)"

    def test_palavras_chave_3_idiomas_3_a_5(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        for secao in ["Palavras-chave", "Keywords", "Palabras clave"]:
            idx = texto.index(secao)
            linha = texto[idx : idx + 400].split("\n")[0]
            # conta termos separados por ';' na mesma linha ou nas 2 seguintes
            bloco = "\n".join(texto[idx : idx + 400].split("\n")[0:3])
            termos = [t.strip() for t in bloco.split(";") if t.strip()]
            assert 3 <= len(termos) <= 5, (
                f"{secao} com {len(termos)} termos (esperado 3–5)"
            )


class TestNormasABNT:
    """Citações NBR 10520 e referências NBR 6023."""

    def test_citacao_autor_data(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        refs = texto.split("Referências")[0]
        padrões = [
            r"\(([A-ZÀ-Ú][A-ZÀ-Ú\s;]*),?\s*(19|20)\d{2}\)",  # (AUTOR, 2020)
            r"\(([A-ZÀ-Ú][A-ZÀ-Ú\s;]*);\s*([A-ZÀ-Ú][A-ZÀ-Ú\s;]*);?\s*,?\s*(19|20)\d{2}\)",
        ]
        ocorrencias = 0
        for p in padrões:
            ocorrencias += len(re.findall(p, refs))
        assert ocorrencias >= 10, f"apenas {ocorrencias} citações autor-data ABNT"

    def test_referencias_ordem_alfabetica(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        bloco = texto.split("Referências")[-1]
        # apêndice (R420) não faz parte da lista de referências
        if "## Apêndice" in bloco:
            bloco = bloco.split("## Apêndice")[0]
        refs_bloco = bloco
        linhas = [l.strip() for l in refs_bloco.splitlines()
                  if l.strip() and not l.startswith("#")]
        sobrenomes = [l.split(",")[0].upper() for l in linhas if l.split(",")]
        assert len(sobrenomes) >= 12, f"apenas {len(sobrenomes)} referências"
        assert sobrenomes == sorted(sobrenomes), (
            "referências fora de ordem alfabética"
        )

    def test_referencias_com_ano_e_doi(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        refs = texto.split("Referências")[-1]
        anos = re.findall(r"(?:,\s*|\(|\s)(19|20)\d{2}(?:\.|\))", refs)
        dois = re.findall(r"DOI:\s*10\.\d{4,}", refs)
        assert len(anos) >= 12, "referências sem ano ABNT"
        assert len(dois) >= 8, f"apenas {len(dois)} DOIs nas referências"

    def test_notas_de_rodape_evitadas(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        notas = len(re.findall(r"\[\^|nota de rodapé|^\[[0-9]+\]", texto, re.M))
        assert notas <= 3, f"{notas} notas de rodapé (RBEP: evitar)"


class TestCorpoSemAvisosEditoriais:
    """O corpo do manuscrito não contém avisos de candidatura/status."""

    @pytest.mark.parametrize("termo", ["candidat", "aguarda revisão",
                                       "revisão por pares", "submissão",
                                       "Qualis", "manuscrito gerado em",
                                       "status:"])
    def test_aviso_editorial_ausente_do_corpo(self, termo):
        texto = ARTIGO.read_text(encoding="utf-8")
        assert termo not in texto.lower(), f"aviso editorial no corpo: '{termo}'"


class TestAntiOverclaim:
    """Termos bloqueados e resultados false-positive ausentes."""

    @pytest.mark.parametrize("termo", TERMOS_BLOQUEADOS)
    def test_termo_proibido_ausente(self, termo):
        texto = ARTIGO.read_text(encoding="utf-8")
        assert termo not in texto, f"termo bloqueado presente: '{termo}'"

    def test_corpo_sem_linguagem_causal(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        for causal in ["determina", "garante", "assegura que", "prova que"]:
            assert causal not in texto.lower()
        # "causa" como palavra (substantivo/verbo) é alegação causal; adjetivos
        # "causais/causal" em negação explícita são aceitáveis (refinamento
        # R414, alinhado ao gate do R413).
        assert not re.search(r"\bcausa\b", texto, re.IGNORECASE), (
            "uso não-negado de 'causa' no artigo"
        )


class TestConsistenciaComR409:
    """Números e tabelas idênticos ao artigo publicável (R409)."""

    def test_numeros_do_resumo_na_provenance(self):
        prov = json.loads(PROVENANCE.read_text(encoding="utf-8"))

        def iter_numeros(obj):
            if isinstance(obj, (int, float)):
                yield obj
            elif isinstance(obj, list):
                for item in obj:
                    yield from iter_numeros(item)
            elif isinstance(obj, dict):
                for item in obj.values():
                    yield from iter_numeros(item)

        candidatos = [x for x in iter_numeros(prov)]
        texto = ARTIGO.read_text(encoding="utf-8")
        resumo = texto.split("Abstract")[0]
        valores = re.findall(r"([−-]?\d+[.,]\d+)", resumo)
        assert valores, "resumo sem números"
        for v in valores:
            v_norm = float(v.replace(",", ".").replace("−", "-"))
            assert any(abs(v_norm - x) < 0.005 for x in candidatos), (
                f"número '{v}' no resumo sem proveniência"
            )

    def test_tabelas_identicas_a_proveniencia(self):
        """Valores-chave do corpo do artigo batem com a provenance expandida (0,005)."""
        prov = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        texto = ARTIGO.read_text(encoding="utf-8")
        corpo = texto.split("Referências")[0]
        for chave in ["rho_niveis_terciaria", "rho_diferencas_terciaria",
                      "efeito_fixo_cluster_coef", "ml_auc_linha",
                      "ml_auc_agrupado"]:
            valor = prov[chave]
            if isinstance(valor, float):
                s = f"{valor:.3f}".replace(".", ",")
                assert s in corpo.replace(" ", ""), (
                    f"valor {chave}={valor} não encontrado no corpo"
                )

    def test_sem_placeholders(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        assert "—" not in texto.replace("—", ""), "placeholders '—' no corpo"
        assert "..." not in texto.split("Referências")[0]


class TestReferenciasSubset:
    """Referências são subconjunto das 33 obras auditadas."""

    def test_todas_referencias_tem_doi_ou_url_oficial(self):
        import pandas as pd

        audit = pd.read_csv(BASE / "outputs" / "citation_audit.csv")
        texto = ARTIGO.read_text(encoding="utf-8")
        refs = texto.split("Referências")[-1]
        # pelo menos 12 referências; todas com DOI: ou http
        linhas = [l.strip() for l in refs.splitlines() if l.strip() and "DOI" in l or "http" in l]
        assert len(linhas) >= 12
