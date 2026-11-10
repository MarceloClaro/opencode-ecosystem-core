# SPEC-935-R1129 — CB intercalado com 13 funções do CZ

**Status:** implementação local, sem hardware
**Data:** 2026-11-10
**Depende de:** R1128 (grafo de padrões), R1125 (paridade/ajuste)
**Fonte:** Chen et al., Nat. Commun. 14, 52 (2023),
DOI `10.1038/s41467-022-35759-4`.

## 1. Objetivo

Implementar o desenho de cycle benchmarking com correções de 1 qubit que
recupera as **13 funções aprendíveis** do CZ: 7 fidelidades individuais
(`IZ, ZI, XX, XY, YX, YY, ZZ`) e 6 produtos de pares
(`IX·ZX, IX·ZY, IY·ZX, XI·XZ, XI·YZ, YI·XZ`).

As 2 funções de corte permanecem não aprendíveis sem hipótese adicional.

## 2. Convenções

- Ruído de Pauli **antes** de cada CZ, como no modelo do artigo.
- Correções de 1 qubit ideais no simulador.
- Profundidades pares (0,2,4,8,16) para evitar o sinal `(-1)^m` dos ciclos
  cruzados.
- Medição na base do Pauli inicial; a paridade é a expectativa do Pauli.
- Nenhum twirl de Pauli é aplicado neste piloto; o canal já é Pauli no
  simulador. Hardware exige twirl/compensação e auditoria da compilação.

## 3. Requisitos

- **R1.** Tabela de Cliffords de 1 qubit e correção para pares de mesmo padrão.
- **R2.** Circuito `cycle_body` para um ciclo fechado, sem base de medida.
- **R3.** Circuito `cycle_circuit` com base e medição.
- **R4.** Matriz de desenho 13×15 com posto 13 e resíduo de incidência zero.
- **R5.** Simulador com ruído antes do CZ e recuperação exata das 13 funções.
- **R6.** Testes de ciclos inválidos, profundidades inválidas, QASM e ausência
  de strings de hardware.
- **R7.** Relatório/artefato com erro máximo e limites.
- **R8.** Nenhum hardware, rede, submissão ou credencial.

## 4. Não objetivos

- Executar o desenho no Baihua.
- Modelar ruído das correções de 1 qubit.
- Resolver as 2 funções de corte.
- Declarar taxas medidas, PEC 2q ou vantagem.

## 5. Critérios de aceitação

- 13 funções: 7 individuais + 6 pares;
- matriz 13×15 com posto 13 e nulidade 2;
- `B @ D.T = 0` (ciclos no espaço de ciclos);
- expectativa ideal +1 em profundidades pares para os 13 ciclos;
- sinal -1 em profundidade 1 para os 4 ciclos cruzados;
- recuperação exata com erro < 1e-10;
- 2 funções de corte declaradas como não medidas;
- comando `interleaved` no harness;
- nenhuma taxa medida e nenhum hardware.
