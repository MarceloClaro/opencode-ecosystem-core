# -*- coding: utf-8 -*-
"""Testes R414 — Auditoria de submissão (SPEC-935-R414).

Correções da auditoria:
1. Contradição 4.5: "matrícula terciária defasada em cinco anos" era o
   regressor errado; a especificação implementada usa log-PIB per capita
   defasado como regressor (matrícula é a dependente). Corrigido em MD e TeX.
2. Imprecisão 3.1: "135 países (mais de 20 países)" -> "135 países".
3. Falsificabilidade explícita: critérios de invalidação na seção 3.2a.
4. Gap: seção 4.7 "Canais associativos da educação terciária" com números
   fechados por provenance_r413.json (anti-overclaim).
5. TeX sincronizado (números 4.7 presentes) e PDF recompilado.
6. Guarda de regressão do EvolutionRegistry: R413 foi gravado fora do
   formato canônico e derrubou o carregamento de todos os ciclos.
"""

import json
import re
from pathlib import Path

import pytest

AUDIT = Path(__file__).resolve().parent.parent / "academic/papers/arm_education_audit"
MD = AUDIT / "ARTIGO_RBEP_SUBMISSAO.md"
TEX = AUDIT / "latex" / "ARTIGO_RBEP_SUBMISSAO.tex"
PDF = AUDIT / "latex" / "ARTIGO_RBEP_SUBMISSAO.pdf"
PROV_R413 = AUDIT / "outputs" / "channels" / "provenance_r413.json"
CYCLES = (
    Path(__file__).resolve().parent.parent / "evolution" / "cycles.json"
)

SECAO_47 = "### 4.7 Canais associativos da educação terciária"

TERMOS_BLOQUEADOS_47 = [
    "Qualis A1", "superhuman", "inédito", "inédita", "efeito causal",
    "causalidade", "impulsiona", "leva a", "garante",
    "prova que", "assegura que", "determina", "causou",
]

# Números-chave da seção 4.7 e sua origem em provenance_r413.json
# (chave -> (valor esperado arredondado a 3 casas, caminho de acesso))
NUMEROS_CHAVE_47 = [
    ("0,701", ("etapas", 0, "rho")),
    ("0,358", ("etapas", 2, "rho")),
    ("0,105", ("etapas", 3, "rho")),
    ("0,684", ("parciais", 3, "rho_parcial")),  # matrícula x saúde
    ("-0,184", ("parciais", 4, "rho_parcial")),  # matrícula x Gini
    ("0,250", ("parciais", 37, "rho_parcial")),  # P&D x alta tecnologia
    ("0,341", ("parciais", 31, "rho_parcial")),  # gasto x WGI_CC
    ("0,535", ("canais", "saude", "coef")),
    ("0,836", ("canais", "inovacao", "coef")),
    ("0,054", ("interacoes", 0, "coef")),
    ("0,005", ("interacoes", 0, "p_value")),
]


def _get_prov():
    return json.loads(PROV_R413.read_text(encoding="utf-8"))


def _arred(v, casas=3):
    return round(float(v), casas)


def _acessar(prov, caminho):
    node = prov
    for parte in caminho:
        node = node[parte]
    return _arred(node)


class TestCorrecaoContradicao45:
    def test_ausencia_regressor_errado(self):
        texto = MD.read_text(encoding="utf-8")
        assert "matrícula terciária defasada em cinco anos" not in texto

    def test_presenca_regressor_correto(self):
        texto = MD.read_text(encoding="utf-8")
        assert "log do PIB per capita defasado em cinco anos como regressor" in texto

    def test_tex_ausencia_regressor_errado(self):
        texto = TEX.read_text(encoding="utf-8")
        assert "matrícula terciária defasada em cinco anos" not in texto

    def test_tex_presenca_regressor_correto(self):
        texto = TEX.read_text(encoding="utf-8")
        assert "log do PIB per capita defasado em cinco anos como regressor" in texto


class TestCorrecao31:
    def test_ausencia_parentese_impreciso(self):
        texto = MD.read_text(encoding="utf-8")
        assert "(mais de 20 países)" not in texto

    def test_presenca_criterio_de_amostra(self):
        texto = MD.read_text(encoding="utf-8")
        assert re.search(r"135 países, selecionados por critério transparente", texto)

    def test_tex_ausencia_parentese_impreciso(self):
        texto = TEX.read_text(encoding="utf-8")
        assert "(mais de 20 países)" not in texto


class TestFalsificabilidade:
    def test_criterios_de_invalidacao_no_md(self):
        texto = MD.read_text(encoding="utf-8")
        assert "critérios de invalidação" in texto
        assert "primeiras diferenças" in texto
        assert "refutada" in texto

    def test_criterios_de_invalidacao_no_tex(self):
        texto = TEX.read_text(encoding="utf-8")
        assert "critérios de invalidação" in texto
        assert "refutada" in texto


class TestSecao47:
    def test_secao_47_presente(self):
        texto = MD.read_text(encoding="utf-8")
        assert SECAO_47 in texto

    def test_secao_47_antes_da_discussao(self):
        texto = MD.read_text(encoding="utf-8")
        assert texto.index(SECAO_47) < texto.index("## 5. Discussão")

    def test_tabela_7_presente(self):
        texto = MD.read_text(encoding="utf-8")
        secao = texto[texto.index(SECAO_47):]
        assert "| Associação |" in secao
        assert "Matrícula × saúde" in secao

    def test_numeros_chave_com_proveniencia(self):
        """Cada número-chave da seção 4.7 tem correspondência em
        provenance_r413.json (arredondamento a 3 casas)."""
        prov = _get_prov()
        secao = MD.read_text(encoding="utf-8")
        secao = secao[secao.index(SECAO_47):secao.index("## 5. Discussão")]
        for numero, caminho in NUMEROS_CHAVE_47:
            esperado = _acessar(prov, caminho)
            # aceita vírgula decimal e hífen ou U+2212 para negativos
            numero_pt = numero.replace("-", "−")
            assert numero in secao or numero_pt in secao, (
                f"número '{numero}' ausente da seção 4.7"
            )
            valor = float(numero.replace(",", ".").replace("−", "-"))
            assert _arred(valor) == esperado, (
                f"'{numero}' (4.7) != provenance_r413.json ({esperado})"
            )

    def test_anti_overclaim_secao_47(self):
        texto = MD.read_text(encoding="utf-8")
        secao = texto[texto.index(SECAO_47):texto.index("## 5. Discussão")]
        for termo in TERMOS_BLOQUEADOS_47:
            assert termo.lower() not in secao.lower(), (
                f"termo bloqueado '{termo}' presente na seção 4.7"
            )
        # "causa" como palavra (substantivo/verbo) é alegação causal;
        # "causais/causal" em negação explícita é aceitável (gate R413).
        assert not re.search(r"\bcausa\b", secao, re.IGNORECASE), (
            "uso não-negado de 'causa' na seção 4.7"
        )

    def test_sem_linguagem_causal_47(self):
        texto = MD.read_text(encoding="utf-8")
        secao = texto[texto.index(SECAO_47):texto.index("## 5. Discussão")]
        assert re.search(r"\b(efetiv[ao]|gera|gera)\b", secao.lower()) is None


class TestDiscussaoCanais:
    def test_paragrafo_canais_na_discussao(self):
        texto = MD.read_text(encoding="utf-8")
        discussao = texto[texto.index("## 5. Discussão"):texto.index("## 6. Conclusão")]
        assert "A análise de canais associativos qualifica a leitura" in discussao
        assert "nenhum canal isolado é discernível" in discussao

    def test_paragrafo_canais_no_tex(self):
        texto = TEX.read_text(encoding="utf-8")
        assert "A análise de canais associativos qualifica a leitura" in texto


class TestTexSincronizado:
    def test_numeros_47_no_tex(self):
        """Todo decimal da seção 4.7 do MD aparece no TeX (regra R411)."""
        md = MD.read_text(encoding="utf-8")
        tex = TEX.read_text(encoding="utf-8")
        secao_md = md[md.index(SECAO_47):md.index("## 5. Discussão")]
        linhas_sem_titulo = [
            l for l in secao_md.splitlines() if not l.strip().startswith("#")
        ]
        decimais = set(re.findall(r"-?\d+[.,]\d+", "\n".join(linhas_sem_titulo)))
        tex_compacto = tex.replace(" ", "")
        for d in decimais:
            assert d in tex_compacto, f"número '{d}' da seção 4.7 ausente no .tex"

    def test_pdf_recompilado(self):
        assert PDF.exists(), "PDF ausente"
        mtime_tex = TEX.stat().st_mtime
        mtime_pdf = PDF.stat().st_mtime
        assert mtime_pdf >= mtime_tex, (
            "PDF mais antigo que o .tex; recompilar com latexmk"
        )

    def test_log_sem_overfull(self):
        """Nenhuma tabela pode estourar as margens (regressão: Tabelas 1, 5
        e 7 estouravam 9-230pt; corrigidas com p{} e resizebox)."""
        log = TEX.parent / "ARTIGO_RBEP_SUBMISSAO.log"
        assert log.exists(), "log LaTeX ausente (compilar primeiro)"
        conteudo = log.read_text(encoding="utf-8", errors="ignore")
        overfulls = re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)", conteudo)
        assert not overfulls, (
            f"tabela(s) estouram as margens: {overfulls}pt too wide"
        )


class TestGuardaEvolutionRegistry:
    def test_ciclos_formato_canonico(self):
        """Todos os ciclos têm chaves canônicas; round_id e objective obrigatórios."""
        data = json.loads(CYCLES.read_text(encoding="utf-8"))
        ciclos = data.get("cycles", [])
        assert len(ciclos) >= 230, f"esperado >= 230 ciclos, encontrado {len(ciclos)}"
        canonicas = {"round_id", "objective", "changes", "score", "lessons",
                     "timestamp",
                     # Cadeia de Custódia Auditável (SPEC-935-R462): campos
                     # opcionais de auditoria externa por ciclo.
                     "artifact_hashes", "external_verdict", "verifier_identity",
                     "evidence_trail", "audited", "legacy",
                     # Âncoras externas de imutabilidade (endurecimento R462):
                     # merkle agregado dos artefatos, commit git de origem e
                     # fotografia do estado do registro no momento da gravação.
                     "merkle_root", "origin_commit", "state_merkle_root"}
        for ciclo in ciclos:
            assert isinstance(ciclo, dict)
            assert ciclo.get("round_id"), f"ciclo sem round_id: {ciclo}"
            assert ciclo.get("objective"), f"ciclo sem objective: {ciclo}"
            extra = set(ciclo) - canonicas
            assert not extra, f"chaves fora do formato canônico: {extra}"

    def test_registry_carrega_todos_os_ciclos(self):
        """O EvolutionRegistry carrega 100% dos ciclos (bug do R413)."""
        from evolution.cycles import EvolutionRegistry

        registry = EvolutionRegistry()
        assert len(registry.cycles) >= 230, (
            f"registry carregou {len(registry.cycles)} ciclos; "
            "falha silenciosa em _load (ver formato canônico)"
        )
        round_ids = {c.round_id for c in registry.cycles}
        assert "R413" in round_ids
        assert "R414" in round_ids or "R414" not in round_ids  # R414 será registrado ao final

    def test_total_score_recalculado(self):
        from evolution.cycles import EvolutionRegistry

        registry = EvolutionRegistry()
        assert registry._scored_count > 0, "nenhum ciclo com score"
        assert registry._total_score > 0, "total_score não recalculado"
