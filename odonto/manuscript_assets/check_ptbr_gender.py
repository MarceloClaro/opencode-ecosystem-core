"""Scan de concordancia de genero: artigo feminino + substantivo masculino.

Verificacao pontual de qualidade linguistica da traducao PT-BR. Nao e prova
de gramatica completa, mas pega a classe de erro mais comum em traducao
automatica (artigo herdado do original em ingles, que nao tem genero).
"""

import re
from pathlib import Path
from collections import Counter

PT = Path(__file__).resolve().parent.parent / "Journal_of_Dentistry_Example_OdontoCA_PT.md"

MASC = {
    "exame", "modelo", "dado", "metodo", "processo", "criterio", "parametro",
    "denominador", "numerador", "estimador", "classificador", "pipeline",
    "fluxo", "codigo", "software", "marcador", "intervalo", "limite", "passo",
    "ponto", "termo", "conjunto", "grupo", "cenario", "contraste",
    "pressuposto", "registro", "analise", "calculo", "referencia", "rasgo",
    "amostre", "amostra", "random", "acesso", "aumento", "decremento",
    "escore", "intervalos", "modelos", "dados", "exames", "erro", "uso",
    "momento", "padrao", "corte", "risco", "sinal", "passo", "teste",
    "arranjo", "ordenamento", "subgrupo", "subgrupo",
}

# Substantivoselistados como femininos reais (excecoesKnown).
FEM = {"amostra", "analise", "calculo", "referencia", "abordagem", "coorte",
       "base", "fonte", "tabela", "figura", "medida", "politica", "clinica",
       "transicao", "calibracao", "previsao", "decisao", "versao", "secao",
       "proporcao", "relacao", "regra", "etapa", "escola", "criterio"}


def main() -> int:
    text = PT.read_text()
    counts = Counter()
    for m in re.finditer(r"\b(da|do|a|o|na|no|na[s]?|nos)\s+([A-Za-zÀ-ÿ\-]+)", text):
        art, word = m.group(1), m.group(2)
        low = word.lower()
        if low in MASC and low not in FEM:
            counts[(art, word)] += 1
    suspicious = {k: v for k, v in counts.items() if k[0] in ("da", "a", "na")}
    if not suspicious:
        print("nenhuma combinacao suspeita de artigo + substantivo")
        return 0
    print("revisar combinacoes:")
    for (art, word), n in sorted(suspicious.items()):
        print(f"   {art:4s} {word:16s} x{n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
