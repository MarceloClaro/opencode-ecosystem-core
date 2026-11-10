# R1128 — Aprendibilidade de Pauli no CZ

Fonte: Chen et al., *The learnability of Pauli noise*, Nat. Commun. 14, 52 (2023), DOI 10.1038/s41467-022-35759-4.

## Resultado

- Grafo de padrões do CZ: 15 arestas, 4 vértices, 2 componentes.
- Espaço de ciclos (aprendível): **13**.
- Espaço de cortes (não aprendível): **2**.
- Fidelidades individuais aprendíveis: IZ, XX, XY, YX, YY, ZI, ZZ.
- Desenho de médias de órbita (R1126): posto 9; faltam 4 funções.

## Técnica extraída

A Figura 1(b) do artigo insere **Cliffords de 1 qubit** entre aplicações do CZ para mapear o Pauli de volta ao mesmo padrão de peso. Isso permite aprender fidelidades individuais quando o padrão é preservado, em vez de apenas produtos de órbita. O CB é ótimo para o espaço de ciclos; as 2 funções de corte exigem hipótese adicional (preparação perfeita, GST ou restrição física).

## Consequência para o harness

- Não chamar o posto 9 de limite fundamental: ele é o subespaço do desenho atual.
- O próximo desenho deve incluir correções de 1 qubit e validar o posto 13.
- Não liberar PEC 2q: 2 graus permanecem não aprendíveis e as taxas não foram medidas.
- A hipótese de Cliffords de 1 qubit suficientemente menos ruidosos não foi validada no Baihua.

## Limites

13 funções aprendíveis e 2 não aprendíveis para o CZ sob ruído de Pauli e SPAM twirlado. As 2 funções de corte exigem hipótese adicional (preparação perfeita, GST ou restrição física) e não são medidas pelo CB padrão. Cliffords de 1 qubit intercalados são supostos suficientemente menos ruidosos; isso não foi validado no Baihua. Nenhuma taxa foi medida; PEC 2q permanece bloqueado.

## Artefatos

- `learnability.json` — grafo, bases de ciclo/corte e comparação.
- `quantum_mitigation/cb_learnability.py` — implementação.
- `tests/test_r1128_cb_learnability.py` — contraprovas.
