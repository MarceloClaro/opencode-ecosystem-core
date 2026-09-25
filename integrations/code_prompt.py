#!/usr/bin/env python3
"""
R506 — Prompt generator para código executável.
Gera prompts que pedem ao LLM um script Python completo
que resolve o problema da IMO e imprime a resposta final.
"""

CODE_SYSTEM_PROMPT = """\
Você é um programador matemático especialista. Para cada problema abaixo,
escreva um script Python COMPLETO que:

1. Resolva o problema usando lógica, cálculo ou enumeração
2. Imprima EXATAMENTE a resposta final com print()
3. NÃO use input() — o script roda sem intervenção
4. NÃO baixe dados da internet
5. Pode usar apenas a biblioteca padrão (math, itertools, sympy se disponível)
6. Seja eficiente — timeouts de 30 segundos

IMPORTANTE: NÃO use ferramentas externas (bash, exec, etc). 
Escreva APENAS o código como texto na sua resposta.

Formato de saída:
```python
# Solução
código aqui
print(resposta_final)
```

A última linha SEMPRE deve ser print() com a resposta."""

PROBLEMS = [
    {
        "id": "r506-algebra-001",
        "category": "algebra",
        "prompt": (
            "Encontre o valor de ⌊2025/7⌋ + ⌊2025/8⌋ + ⌊2025/9⌋.\n"
            "(⌊x⌋ denota o maior inteiro menor ou igual a x.)"
        ),
        "expected": "866",
        "expected_num": 866,
        "solver_type": "arithmetic",
    },
    {
        "id": "r506-algebra-004",
        "category": "algebra",
        "prompt": (
            "Seja u ≥ 2 um inteiro. Prove que para todo inteiro n ≥ u, "
            "existe um subconjunto de {1, 2, ..., n} de tamanho exatamente u cuja soma "
            "é divisível por u. Qual é o NÚMERO MÍNIMO de subconjuntos que garantem "
            "a existência? (Responda com o valor numérico.)"
        ),
        "expected": "1",
        "expected_num": 1,
        "solver_type": "proof_value",
    },
    {
        "id": "r506-nt-001",
        "category": "number_theory",
        "prompt": (
            "Encontre todos os pares de primos (p, q) tais que p³ - q⁵ = (p + q)².\n"
            "Responda com o par ordenado, ex: (7, 3)"
        ),
        "expected": "(7, 3)",
        "expected_num": None,
        "solver_type": "diophantine",
    },
    {
        "id": "r506-comb-001",
        "category": "combinatorics",
        "prompt": (
            "Seja f(n) o número de subconjuntos S de {1, 2, ..., 2n} tais que "
            "|S| = n e a soma dos elementos de S é um máximo LOCAL (maior que "
            "a soma de qualquer subconjunto vizinho com uma troca).\n"
            "Qual é f(n) em função de n? Se a resposta é 2^{k} para algum k, "
            "qual é k? (Responda com o expoente.)"
        ),
        "expected": "n-1",
        "expected_num": None,
        "solver_type": "combinatorial",
    },
    {
        "id": "r506-algebra-002",
        "category": "algebra",
        "prompt": (
            "Encontre o menor inteiro n > 1 tal que 2^n > n²."
        ),
        "expected": "5",
        "expected_num": 5,
        "solver_type": "inequality",
    },
    {
        "id": "r506-nt-002",
        "category": "number_theory",
        "prompt": (
            "Encontre todos os primos p tais que p² divide 2^p + 1.\n"
            "Responda com o conjunto de soluções, ex: {3}"
        ),
        "expected": "{3}",
        "expected_num": None,
        "solver_type": "divisibility",
    },
    {
        "id": "r506-nt-003",
        "category": "number_theory",
        "prompt": (
            "Calcule o expoente do maior potência de 3 que divide 2023! "
            "(ou seja, v₃(2023!) onde vₚ(n!) é a soma de ⌊2023/3^k⌋ para k = 1, 2, ...)"
        ),
        "expected": "1006",
        "expected_num": 1006,
        "solver_type": "legendre",
    },
    {
        "id": "r506-comb-002",
        "category": "combinatorics",
        "prompt": (
            "Seja S₅ o conjunto das permutações de {1,2,3,4,5}. "
            "Uma permutação σ tem um máximo local na posição i (1 < i < 5) "
            "se σ(i-1) < σ(i) > σ(i+1).\n"
            "Quantas permutações em S₅ têm EXATAMENTE 2 máximos locais?"
        ),
        "expected": "88",
        "expected_num": 88,
        "solver_type": "enumeration",
    },
    {
        "id": "r506-geo-001",
        "category": "geometry",
        "prompt": (
            "Em um polígono convexo regular de 2023 lados, quantas diagonais "
            "existem? (Uma diagonal conecta dois vértices não-adjacentes.)"
        ),
        "expected": "2043230",
        "expected_num": 2043230,
        "solver_type": "formula",
    },
]


def get_code_prompt(problem: dict) -> str:
    """Gera o prompt completo para geração de código."""
    return f"""{CODE_SYSTEM_PROMPT}

---
PROBLEMA ({problem['category'].upper()}):
{problem['prompt']}
"""

def get_all_problems():
    """Retorna lista de problemas."""
    return PROBLEMS

if __name__ == "__main__":
    for p in PROBLEMS:
        print(f"\n{'='*60}")
        print(f"PROBLEMA: {p['id']}")
        print(f"RESPOSTA ESPERADA: {p['expected']}")
        print(f"PROMPT:")
        print(get_code_prompt(p)[:300] + "...")