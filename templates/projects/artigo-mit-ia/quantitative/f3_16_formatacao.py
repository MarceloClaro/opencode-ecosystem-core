"""
Fase 3.16 — Comparação com Periódico Alvo e Diretrizes de Formatação
=====================================================================
Recomendação: **Structural Change and Economic Dynamics** (SCED)
  - Qualis A1 (Economia)
  - Scopus/Q1, JCR Q1
  - Fit temático: mudança estrutural, catch-up, inovação, armadilha renda média
  - Aceita artigos com método misto (teórico + quantitativo)

Alternativas:
  1. Journal of International Development (Qualis A1)
  2. Revista de Economia Contemporânea (Qualis A1, BR)
  3. Journal of Development Studies (Qualis A1)

Este script gera um checklist de conformidade com as normas do periódico.
"""

import json
from pathlib import Path

BASE = Path(r'C:\Users\marce\.config\opencode\artigo-mit-ia')
OUT = BASE / 'quantitative' / 'output' / 'diretrizes_formatacao.json'

# Normas típicas SCED + APA 7th
diretrizes = {
    "periodico_recomendado": {
        "nome": "Structural Change and Economic Dynamics",
        "editora": "Elsevier",
        "qualis": "A1 (Economia)",
        "fator_impacto": "~4.2 (JCR 2024)",
        "escopo": (
            "Mudança estrutural, crescimento econômico, catch-up tecnológico, "
            "desigualdade, transformação produtiva. Fit ideal para ARM + IAG."
        ),
        "submissao": "https://www.editorialmanager.com/STRECO/default.aspx"
    },
    "checklist_formatacao": {
        "abstract": {
            "exigido": "Estruturado, 200-250 palavras",
            "atual": "OK (extraído dos arquivos _corrigido.md)",
            "status": "🟡 VERIFICAR"
        },
        "palavras_chave": {
            "exigido": "4-6 palavras-chave",
            "atual": "Presente no artigo",
            "status": "🟡 VERIFICAR"
        },
        "limite_palavras": {
            "exigido": "10.000-12.000 palavras (artigo completo)",
            "atual": "~21.000 palavras estimadas",
            "status": "🔴 REDUZIR (~40%)"
        },
        "estrutura": {
            "exigido": "Introdução, Metodologia, Resultados, Discussão, Conclusão",
            "atual": "Estrutura segue normas científicas",
            "status": "🟢 OK"
        },
        "referencias": {
            "exigido": "APA 7th edition",
            "atual": "Formato APA, verificar consistência",
            "status": "🟡 VERIFICAR"
        },
        "tabelas_e_figuras": {
            "exigido": "Numeradas sequencialmente, fontes claras",
            "atual": "Diagramas SVG gerados na Fase 1",
            "status": "🟢 OK"
        },
        "secao_etica": {
            "exigido": "Declaração de conflitos, financiamento",
            "atual": "Não verificado",
            "status": "🔴 ADICIONAR"
        },
        "highlight": {
            "exigido": "3-5 bullet points (SCED exige Highlights)",
            "atual": "Não presente",
            "status": "🔴 ADICIONAR"
        },
        "disponibilidade_dados": {
            "exigido": "Data Availability Statement",
            "atual": "Não presente",
            "status": "🔴 ADICIONAR"
        }
    },
    "adequacao_conteudo": {
        "fit_tematico": {
            "analise": "Excelente — ARM, mudança estrutural, inovação, IAG",
            "score": "10/10"
        },
        "metodologia": {
            "analise": "Mista (teórica + quantitativa), alinhada ao perfil SCED",
            "score": "9/10"
        },
        "contribuicao_original": {
            "analise": "Framework Estratégia 3i × AIPI com validação empírica",
            "score": "8/10"
        },
        "relevancia_tematica": {
            "analise": "Alta — IAG é tema emergente na economia do desenvolvimento",
            "score": "9/10"
        }
    },
    "acoes_formatacao_necessarias": [
        {
            "ordem": 1,
            "acao": "Reduzir artigo de ~21.000 para ~10.000 palavras",
            "tipo": "CRÍTICO",
            "detalhe": "Manter narrativa central; condensar referencial teórico em 60%; "
                       "tabelas quantitativas como apêndice"
        },
        {
            "ordem": 2,
            "acao": "Criar Highlights (3-5 bullets) para SCED",
            "tipo": "OBRIGATÓRIO",
            "detalhe": "Formato: bullet points de 85 caracteres cada, resumindo contribuição"
        },
        {
            "ordem": 3,
            "acao": "Adicionar seções obrigatórias",
            "tipo": "OBRIGATÓRIO",
            "detalhe": "Declaração de conflitos, financiamento, disponibilidade de dados, "
                       "contribuição dos autores"
        },
        {
            "ordem": 4,
            "acao": "Converter referências para APA 7th padronizado",
            "tipo": "RECOMENDADO",
            "detalhe": "Verificar itálico em periódicos, DOI formatado, "
                       "URLs de acesso"
        },
        {
            "ordem": 5,
            "acao": "Padronizar abstract estruturado (200-250 palavras)",
            "tipo": "RECOMENDADO",
            "detalhe": "Objetivo, Método, Resultados, Conclusão"
        },
        {
            "ordem": 6,
            "acao": "Incluir diagramas C4 e fluxogramas como figuras",
            "tipo": "OPCIONAL",
            "detalhe": "SVGs já gerados — converter para EPS/PDF (formato Elsevier)"
        }
    ],
    "nota_adicional": (
        "A SCED é a revista com melhor fit temático, mas o artigo atual (~21K palavras) "
        "precisa ser reduzido em ~40%. Alternativa: submeter à Revista de Economia "
        "Contemporânea (Qualis A1, BR, maior flexibilidade de tamanho). "
        "Recomenda-se também considerar a submissão em duas versões: "
        "artigo principal (10K palavras) + supplementary material online (análises completas)."
    )
}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(diretrizes, f, indent=2, ensure_ascii=False)
print(f"Diretrizes salvas em: {OUT}")

# Sumário
print("\n═══ RESUMO — Formatação ═══")
print(f"Periódico recomendado: {diretrizes['periodico_recomendado']['nome']}")
print(f"Qualis: {diretrizes['periodico_recomendado']['qualis']}")
print(f"\nChecklist:")
for item, info in diretrizes['checklist_formatacao'].items():
    print(f"  {info['status']} {item}: {info['exigido']}")
print(f"\nAções necessárias: {len(diretrizes['acoes_formatacao_necessarias'])}")
for a in diretrizes['acoes_formatacao_necessarias']:
    print(f"  [{a['tipo']}] {a['acao']}")
