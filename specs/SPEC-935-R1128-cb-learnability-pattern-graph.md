# SPEC-935-R1128 — Aprendizabilidade de Pauli e grafo de padrões do CZ

**Status:** implementação local, sem hardware
**Data:** 2026-11-10
**Depende de:** R1125, R1126
**Fonte primária:** Chen, Liu, Otten, Seif, Fefferman e Jiang, *The learnability
of Pauli noise*, Nature Communications 14, 52 (2023),
DOI `10.1038/s41467-022-35759-4`, Teoremas 1 e 2.

## 1. Correção necessária

A R1126 mostrou que o desenho **somente-CZ com médias de órbita** tem posto 9.
Isso não é o limite fundamental da informação aprendível. Chen et al. provam
que, para um Clifford de 2 qubits com ruído de Pauli e SPAM twirlado:

- uma fidelidade de Pauli `λ_a` é aprendível se e somente se o **padrão de peso**
  de `P_a` é preservado pela porta;
- o espaço de funções aprendíveis é o **espaço de ciclos** do grafo de
  transferência de padrões;
- o espaço não aprendível é o **espaço de cortes**;
- para um Clifford de 2 qubits, há no máximo **2 graus não aprendíveis**;
- cycle benchmarking é ótimo para extrair toda a informação aprendível.

Para o CZ, o grafo tem 15 arestas, 4 vértices e 2 componentes. Logo:

```
posto de ciclos = 15 − 4 + 2 = 13
posto de cortes = 4 − 2 = 2
```

As 13 funções aprendíveis incluem 7 fidelidades individuais (padrão preservado)
e 6 produtos ao longo de ciclos. As 2 funções não aprendíveis são combinações
de fidelidades cujo padrão de peso muda (por exemplo, `IX/IY/ZX/ZY` e
`XI/XZ/YI/YZ`). O posto 9 da R1126 é o subespaço medido pelo desenho de
médias de órbita, não o espaço aprendível completo.

## 2. Técnica que faltava

A Figura 1(b) de Chen et al. mostra CB com **Cliffords de 1 qubit intercalados**
para mapear o Pauli de volta ao mesmo padrão de peso. É isso que permite
aprender fidelidades individuais quando o padrão é preservado, em vez de apenas
produtos de órbita. A hipótese é que as portas de 1 qubit são suficientemente
menos ruidosas; o resultado é interpretado como o canal do **ciclo vestido**.

## 3. Requisitos

- **R1.** Implementar o grafo de padrões do CZ, a matriz de incidência, os
  espaços de ciclos e de cortes, e a lista de fidelidades individuais.
- **R2.** Reportar `E=15`, `V=4`, `c=2`, `cycle_rank=13`, `cut_rank=2`.
- **R3.** Comparar com o posto 9 da R1126: `missing=4`.
- **R4.** Declarar que as 2 funções de corte exigem hipótese adicional
  (preparação perfeita, GST ou restrição física) e não são medidas pelo CB
  padrão.
- **R5.** Nenhum hardware, rede, submissão ou credencial.
- **R6.** Testes determinísticos e bases verificadas por ortogonalidade.
- **R7.** Não declarar taxas medidas; PEC 2q continua bloqueado.

## 4. Não objetivos

- Gerar ou executar os circuitos com Cliffords intercalados.
- Resolver as 2 funções não aprendíveis.
- Provar que o ruído real é Pauli ou que as portas de 1 qubit são ideais.
- Declarar GST ou diamond norm.

## 5. Critérios de aceitação

- grafo do CZ com 15 arestas, 4 vértices e 2 componentes;
- `cycle_rank=13`, `cut_rank=2`;
- 7 fidelidades individuais aprendíveis: `IZ, ZI, XX, XY, YX, YY, ZZ`;
- base de ciclos com 13 vetores e base de cortes com 2;
- `B @ cycle = 0` e `cut^T @ cycle = 0`;
- comparação com o posto 9: faltam 4 funções;
- grafo da identidade com `cycle_rank=15`, `cut_rank=0`;
- nenhuma string de hardware/submissão no módulo;
- relatório e documentação citam a fonte e os limites.
