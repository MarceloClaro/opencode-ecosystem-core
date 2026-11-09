# SPEC-935-R1113 — Incerteza e calibração completa de 4 estados no GJQ

**Status:** implementação local + execução real no Baihua
**Data:** 2026-11-09
**Depende de:** R1110 (mitigação), R1112 (loop)

## 1. Contexto

O loop R1112 mostrou que o vencedor mitigado inverteu entre 4096 e 2048 shots:
baseline 0,0249 vs otimizado 0,0277 na primeira; baseline 0,0150 vs otimizado
0,0141 na segunda. A diferença de 0,0009 é menor que a variação observada.
Além disso, a calibração |00>/|11> não corrige a população que sai para 01/10.

O operador autorizou repetir o loop com mais shots, calibração completa dos 4
estados e estimativa de incerteza antes de qualquer comparação de layouts.

## 2. Requisitos

- **R1.** Calibrar |00>, |01>, |10> e |11> nos mesmos qubits de cada caso.
- **R2.** Construir a matriz 4x4 completa e inverter com clipping/renormalização.
- **R3.** Executar `N` repetições do Bell por caso, com a mesma calibração,
  agregar counts e calcular média, desvio, mínimo e máximo por repetição.
- **R4.** `compare --full-calibration --repetitions N` deve gerar
  `submissions_estimated = 2N + 8`.
- **R5.** O loop deve propagar `--shots`, `--repetitions` e
  `--full-calibration` ao plano e à execução.
- **R6.** O score deve preferir a TVD mitigada 4x4 quando disponível.
- **R7.** O relatório deve mostrar a incerteza por repetição e a matriz 4x4.
- **R8.** Hardware só após SDD, TDD, simulação, `--confirm` e
  `--allow-hardware`.
- **R9.** Testes R1113 sem rede e sem submissão.
- **R10.** Não declarar vantagem se a diferença estiver dentro da incerteza.

## 3. Método

### 3.1 Matriz 4x4

Para cada estado preparado `s` em `{00,01,10,11}`, medir os counts e preencher
a coluna `s` da matriz `A[medido, preparado] = P(medido|preparado)`. A mitigação
é `p_mit = A^{-1} p_obs`, com clipping e renormalização.

### 3.2 Repetições

Executar `N` Bell por caso e agregar os counts. Para cada repetição, registrar:

- correlação raw 00/11;
- TVD raw vs ideal;
- TVD mitigada 4x4;
- correlação mitigada.

Calcular média, desvio, mínimo e máximo. A incerteza reportada é a dispersão
entre repetições, não uma prova estatística definitiva.

### 3.3 Plano

Com `N=3` e calibração completa:

```text
baseline: 4 cal + 3 Bell = 7 jobs
otimizado: 4 cal + 3 Bell = 7 jobs
total: 14 jobs
```

## 4. Critérios de aceitação

- plano com 4 estados de calibração e 3 repetições;
- `submissions_estimated = 14`;
- matriz 4x4 e mitigação com 01/10;
- counts agregados com total `N * shots`;
- `repetition_stats` com média/desvio/min/max;
- relatório com seção de repetições;
- score usa TVD mitigada 4x4;
- testes R1113 passam;
- nenhuma chave ou overclaim.

## 5. Não objetivos

- Provar superioridade de layout.
- Reduzir a incerteza a zero.
- Corrigir state preparation ou crosstalk.
- Implementar ZNE/PEC/DD.

## 6. Riscos

- **Matriz mal condicionada:** usar pseudoinversa e reportar condição.
- **Leakage residual:** a matriz 4x4 corrige 01/10, mas não state preparation.
- **Amostra pequena:** 3 repetições estimam dispersão, não significância.
- **Custo:** 14 submissões por iteração.
