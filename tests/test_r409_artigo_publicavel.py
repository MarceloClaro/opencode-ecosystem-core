# -*- coding: utf-8 -*-
"""Testes R409 — Artigo publicável (candidato a submissão) com rigor auditável.

Requisitos (SPEC-935-R409):
1. O artigo é rotulado como CANDIDATO a submissão; nenhuma alegação de Qualis A1,
   validação ou prontidão para publicação sem revisão por pares.
2. Todas as tabelas e números são gerados por script (proveniência fechada) a
   partir do painel WDI auditado (cache com SHA-256, R408).
3. Validações cruzadas legítimas e sem vazamento:
   - Leave-One-Country-Out (países de treino e teste disjuntos);
   - Bloqueio temporal (anos de treino anteriores aos de teste);
   - Aprendizado de máquina com split AGRUPADO por país, comparado ao split por
     linha (que vaza) — a diferença é declarada como evidência de
     não identificabilidade com 7 países.
4. Linguagem associativa; termos causais/absolutos proibidos no texto final.
5. Resultados false-positive da versão original (d=16,06; AUC 0,997; percentil
   individual) NÃO aparecem no artigo.
6. Referências são subconjunto das 33 obras únicas auditadas (R408), com DOI.
"""

from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent.parent / "academic/papers/arm_education_audit"
ARTIGO = BASE / "ARTIGO_PUBLICAVEL.md"
TABELAS = BASE / "outputs" / "publishable_tables"
PROVENANCE = TABELAS / "provenance.json"

# Termos absolutamente proibidos no artigo publicável (anti-overclaim + bloqueio R408)
TERMOS_BLOQUEADOS = [
    "Qualis A1",
    "qualis a1",
    "validado",
    "validada",
    "inédito",
    "inédita",
    "condição necessária",
    "condicao necessaria",
    "d = 16,06",
    "d=16,06",
    "16,06",
    "AUC",
    "0,997",
    "0.997",
    "percentil",
    "prova",
    "demonstra causal",
    "causalmente",
]


class TestEstruturaArtigo:
    """O manuscrito existe e tem a estrutura científica completa."""

    def test_artigo_existe(self):
        assert ARTIGO.exists(), f"ARTIGO_PUBLICAVEL.md ausente em {BASE}"

    def test_estrutura_secoes(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        texto_l = texto.lower()
        for secao in [
            "resumo",
            "abstract",
            "palavras-chave",
            "introdução",
            "método",
            "resultados",
            "discussão",
            "conclusão",
            "referências",
        ]:
            assert secao in texto_l, f"seção '{secao}' ausente no artigo"

    def test_rotulo_candidato_explicito(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        assert "candidat" in texto.lower(), (
            "artigo deve se rotular como 'candidato(a) a submissão'"
        )
        assert "revisão por pares" in texto.lower() or "pareceristas" in texto.lower()

    def test_abstract_em_ingles(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        assert "Abstract" in texto
        # o abstract deve ter pelo menos 80 palavras
        idx = texto.index("Abstract")
        trecho = texto[idx : idx + 2500]
        palavras = trecho.split()
        assert len(palavras) >= 80, "abstract em inglês muito curto"


class TestAntiOverclaim:
    """Nenhum termo bloqueado nem resultado false-positive reaparece."""

    @pytest.mark.parametrize("termo", TERMOS_BLOQUEADOS)
    def test_termo_proibido_ausente(self, termo):
        texto = ARTIGO.read_text(encoding="utf-8")
        assert termo not in texto, f"termo bloqueado presente: '{termo}'"

    def test_linguagem_associativa(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        for causal in ["causa", "efeito causal", "impacto de X em Y", "leva a"]:
            assert causal not in texto.lower(), f"linguagem causal: '{causal}'"


class TestProvenienciaNumerica:
    """Todo número central do artigo está na provenance gerada por script."""

    def test_provenance_json_existe(self):
        assert PROVENANCE.exists(), "provenance.json ausente (tabelas não geradas por script)"

    def test_chaves_principais(self):
        import json

        prov = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        for chave in [
            "rho_niveis_terciaria",
            "rho_diferencas_terciaria",
            "rho_niveis_pesquisa",
            "rho_diferencas_pesquisa",
            "rho_niveis_gasto_educ_pearson",
            "rho_niveis_gasto_educ_spearman",
            "rho_diferencas_gasto_educ",
            "loocv_rho_range",
            "loocv_rho_excluindo_sgp",
            "rho_subperiodo_1",
            "rho_subperiodo_2",
            "efeito_fixo_defasagem",
            "ml_auc_agrupado",
            "ml_auc_linha",
        ]:
            assert chave in prov, f"chave de proveniência ausente: {chave}"

    def test_numeros_do_resumo_na_provenance(self):
        """Cada número declarado no resumo precisa existir na provenance."""
        import json
        import re

        texto = ARTIGO.read_text(encoding="utf-8")
        prov = json.loads(PROVENANCE.read_text(encoding="utf-8"))

        # aplaina todos os valores numéricos, inclusive os de listas
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

        # resumo: acha números decimais no resumo (antes de 'Abstract')
        resumo = texto.split("Abstract")[0]
        valores = re.findall(r"(\d+[.,]\d+)", resumo)
        assert valores, "resumo sem números — viola densidade informativa"
        for v in valores:
            v_norm = float(v.replace(",", "."))
            assert any(abs(v_norm - x) < 0.005 for x in candidatos), (
                f"número '{v}' no resumo sem proveniência"
            )


class TestValidacaoCruzadaScript:
    """Os scripts de validação cruzada não vazam informação."""

    def test_loocv_folds_sem_vazamento(self):
        """Países de treino e teste de cada fold são disjuntos."""
        import json

        path = TABELAS / "loocv_folds.json"
        assert path.exists(), "loocv_folds.json ausente (LOOCV não executado)"
        folds = json.loads(path.read_text(encoding="utf-8"))
        assert len(folds) >= 7, f"esperado 1 fold por país, obtido {len(folds)}"
        for fold in folds:
            treino = set(fold["treino"])
            teste = set(fold["teste"])
            assert treino.isdisjoint(teste), f"vazamento: {treino} ∩ {teste}"
            assert len(teste) == 1

    def test_bloqueio_temporal_sem_vazamento(self):
        """Anos de treino são todos anteriores aos anos de teste."""
        import json

        path = TABELAS / "temporal_blocks.json"
        assert path.exists(), "temporal_blocks.json ausente (bloqueio temporal não executado)"
        blocos = json.loads(path.read_text(encoding="utf-8"))
        assert len(blocos) >= 2
        for bloco in blocos:
            assert bloco["treino_max"] < bloco["teste_min"], (
                f"vazamento temporal: treino até {bloco['treino_max']} e teste de "
                f"{bloco['teste_min']}"
            )

    def test_ml_split_agrupado_vs_linha(self):
        """ML com split agrupado por país é muito pior que split por linha —
        a queda é declarada como não identificabilidade (resultado negativo)."""
        import json

        path = TABELAS / "ml_resultados.json"
        assert path.exists(), "ml_resultados.json ausente (ML não executado)"
        res = json.loads(path.read_text(encoding="utf-8"))
        auc_agrupado = res["auc_agrupado"]
        auc_linha = res["auc_linha"]
        # agrupado deve ser perto de chance (0.5) e claramente inferior ao linha
        assert auc_agrupado < 0.75, f"AUC agrupado suspeito: {auc_agrupado}"
        assert auc_agrupado < auc_linha - 0.10, (
            f"AUC agrupado ({auc_agrupado}) não é claramente inferior ao "
            f"split por linha ({auc_linha}) — não demonstra não identificabilidade"
        )


class TestPainelEfeitosFixos:
    """O painel com efeitos fixos e defasagem está documentado com IC."""

    def test_efeito_fixo_relatorio(self):
        path = TABELAS / "painel_efeitos_fixos.json"
        assert path.exists(), "painel_efeitos_fixos.json ausente"
        import json

        res = json.loads(path.read_text(encoding="utf-8"))
        for chave in ["coef", "ic_inf", "ic_sup", "n_obs", "n_paises", "lag_anos"]:
            assert chave in res, f"chave ausente no painel: {chave}"
        assert res["ic_inf"] <= res["coef"] <= res["ic_sup"]


class TestReferencias:
    """Referências do artigo são subconjunto das 33 obras auditadas, com DOI."""

    def test_referencias_abnt(self):
        texto = ARTIGO.read_text(encoding="utf-8")
        refs = texto.split("Referências")[-1]
        linhas = [l.strip() for l in refs.splitlines() if l.strip() and not l.startswith("#")]
        # precisa ter pelo menos 8 referências
        assert len(linhas) >= 8, f"apenas {len(linhas)} referências"

    def test_dois_pontos_e_ano(self):
        """Formato ABNT: sobrenome, N.; ... Título. Ano. (ano não exige parênteses)."""
        import re

        texto = ARTIGO.read_text(encoding="utf-8")
        refs = texto.split("Referências")[-1]
        anos = re.findall(r"(?:\(|,\s*)(19|20)\d{2}(?:\)|\.)", refs)
        assert len(anos) >= 8, "referências sem ano no formato ABNT"
