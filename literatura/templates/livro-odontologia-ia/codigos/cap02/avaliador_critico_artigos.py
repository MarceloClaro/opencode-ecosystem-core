#!/usr/bin/env python3
"""
avaliador_critico_artigos.py — Checklist PRISMA/CLAIM para avaliação de artigos
Autor: Edson Laranjeiras — Livro OdontoIA
"""

import json

PRISMA_CHECKLIST = [
    "Título identifica o estudo como revisão sistemática?",
    "Resumo estruturado (objetivo, métodos, resultados, conclusão)?",
    "Critérios de elegibilidade claramente definidos?",
    "Fontes de informação especificadas (bases, datas)?",
    "Estratégia de busca completa reproduzível?",
    "Processo de seleção descrito (número de revisores)?",
    "Extração dos dados padronizada?",
    "Risco de viés avaliado (ex: QUADAS-2)?",
    "Métodos de síntese apropriados (meta-análise)?",
    "Limitações discutidas?",
]

CLAIM_CHECKLIST = [
    "Título/Resumo identifica uso de IA?",
    "Objetivo do modelo de IA claramente definido?",
    "População do estudo descrita (origem, período)?",
    "Pré-processamento dos dados detalhado?",
    "Divisão treino/validação/teste especificada?",
    "Arquitetura do modelo descrita?",
    "Hiperparâmetros e treinamento documentados?",
    "Métricas de desempenho definidas?",
    "Comparação com padrão de referência?",
    "Análise de erros realizada?",
]

def avaliar_artigo(titulo, doi, checklist):
    """Avalia um artigo segundo um checklist."""
    score = 0
    resultados = {}
    for i, item in enumerate(checklist):
        # Simulação didática — em uso real, seria avaliação humana
        resultados[f"Q{i+1}"] = {"item": item, "status": "✅" if (i % 3 != 0) else "⚠️"}
        if resultados[f"Q{i+1}"]["status"] == "✅":
            score += 1
    return {"titulo": titulo, "doi": doi, "score": f"{score}/{len(checklist)}", "checklist": resultados}

# TDD
def test_prisma_tamanho():
    assert len(PRISMA_CHECKLIST) == 10

def test_claim_tamanho():
    assert len(CLAIM_CHECKLIST) == 10

def test_avaliacao_retorna_dict():
    result = avaliar_artigo("Teste", "10.000/test", PRISMA_CHECKLIST[:3])
    assert isinstance(result, dict)
    assert "score" in result

if __name__ == "__main__":
    test_prisma_tamanho()
    test_claim_tamanho()
    test_avaliacao_retorna_dict()
    # Exemplo
    exemplo = avaliar_artigo("Khanagar et al. 2021", "10.1016/j.jds.2020.06.019", PRISMA_CHECKLIST)
    print(json.dumps(exemplo, indent=2, ensure_ascii=False))
    print("✅ Avaliador crítico funcionando!")
