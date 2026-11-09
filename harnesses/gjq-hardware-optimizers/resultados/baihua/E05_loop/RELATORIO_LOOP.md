# Loop GJQ — plano, simulação, hardware e mitigação

Loop `gjq-loop-20261109T122129` · backend **Baihua** · circuito **E05** · **2048 shots**.

## Gates

| Gate | Estado |
|---|---|
| SDD | True |
| TDD | True |
| Simulação | True |
| Hardware | True |

Submissões estimadas: **6** · usadas: **6**.

## Simulação

- Equivalência ideal (TVD): 0.000e+00.
- Gate: **True** · vencedor simulado: **optimized**.
- TVD ruidosa baseline: 0.0176.
- TVD ruidosa otimizado: 0.0078.

> A simulação usa modelo depolarizante do perfil e não prevê o hardware.

## Hardware

| Caso | Qubits | Raw 00/11 | TVD raw | TVD mitigada | Task ID |
|---|---:|---:|---:|---:|---|
| baseline | [0, 1] | 0.9365 | 0.0635 | 0.0150 | `f36d0036-1994-4281-a42e-e7fcbf332bc0` |
| otimizado | [106, 107] | 0.9253 | 0.0747 | 0.0141 | `25fab68e-27d6-4ca2-9bb2-71908fc07d4c` |

## Score e reflexão

- Proxy: baseline 3.379e-02 · otimizado 5.985e-03 · vencedor **optimized**.
- Raw: vencedor **baseline** · mitigado: vencedor **optimized**.
- Proxy confirmado (raw): **False** · (mitigado): **True**.
- Lição: Proxy e resultado mitigado concordam no otimizado; o raw favoreceu o baseline. A diferença mitigada é pequena; repetir com mais shots e calibrar os 4 estados antes de qualquer conclusão.
- Próxima ação: repetir com mais shots e calibração completa dos 4 estados.
- Score (1 - TVD mitigada do otimizado): 0.9859.

## Limites

- Simulação não é hardware; o modelo depolarizante não prevê fidelidade.
- Uma execução por caso não é estudo estatístico.
- A calibração |11> usa `rx(pi)` e inclui preparação do |1>.
- A inversão 00/11 não corrige leakage para 01/10.
- Não há ZNE, PEC, DD ou correção quântica de erro.
- O loop registra lições; não promove confiança automaticamente.
