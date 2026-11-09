# Loop GJQ — plano, simulação, hardware e mitigação

Loop `gjq-loop-20261109T125854` · backend **Baihua** · circuito **E05** · **8192 shots** por repetição · 3 repetições · calibração 4x4: True.

## Gates

| Gate | Estado |
|---|---|
| SDD | True |
| TDD | True |
| Simulação | True |
| Hardware | True |

Submissões estimadas: **14** · usadas: **14** · órfãs: **6**.

## Tentativas anteriores

| Etapa | Task IDs | Motivo | Usado no resultado final |
|---|---|---|---|
| execute | `c09633b6-cc84-40db-8de2-cfc936942fb9, 72ff2d48-a606-4f1c-b832-3fb5defe5088, eab2b271-f0f8-4eb4-96f4-d324aaad089c, 3e311222-35cd-41c1-9014-3d842b93fc92, 2215516f-a611-4c7a-be48-2d744bbe2c42` | NameError: correlation; 5 jobs submetidos e não usados | False |
| execute/repetition | `760869c6-b768-400e-8f63-b91ad2d7f2c1` | RUNNING/timeout; substituído por 3 repetições novas | False |

## Simulação

- Equivalência ideal (TVD): 0.000e+00.
- Gate: **True** · vencedor simulado: **optimized**.
- TVD ruidosa baseline: 0.0190.
- TVD ruidosa otimizado: 0.0073.

> A simulação usa modelo depolarizante do perfil e não prevê o hardware.

## Hardware

| Caso | Qubits | Raw 00/11 | TVD raw | TVD mitigada | Task ID |
|---|---:|---:|---:|---:|---|
| baseline | [0, 1] | 0.9268 | 0.0732 | 0.0091 | `b95a5e17-68da-4e17-b17f-7aaaa7cc506b` |
| otimizado | [106, 107] | 0.9152 | 0.0848 | 0.0168 | `20ae794b-9a3c-4e61-b344-1956fd3fdeec` |

### Repetições — baseline

| Métrica | Média | Desvio | Mín. | Máx. |
|---|---:|---:|---:|---:|
| Raw 00/11 | 0.9268 | 0.0018 | 0.9248 | 0.9279 |
| TVD raw | 0.0732 | 0.0018 | 0.0721 | 0.0752 |
| TVD mitigada | 0.0092 | 0.0029 | 0.0058 | 0.0109 |
| Correlação mitigada | 0.9998 | 0.0003 | 0.9994 | 1.0000 |

### Repetições — otimizado

| Métrica | Média | Desvio | Mín. | Máx. |
|---|---:|---:|---:|---:|
| Raw 00/11 | 0.9152 | 0.0034 | 0.9125 | 0.9189 |
| TVD raw | 0.0848 | 0.0034 | 0.0811 | 0.0875 |
| TVD mitigada | 0.0168 | 0.0019 | 0.0147 | 0.0183 |
| Correlação mitigada | 0.9832 | 0.0019 | 0.9817 | 0.9853 |

## Score e reflexão

- Proxy: baseline 3.379e-02 · otimizado 5.985e-03 · vencedor **optimized**.
- Raw: vencedor **baseline** · mitigado: vencedor **baseline**.
- Proxy confirmado (raw): **False** · (mitigado): **False**.
- Lição: O proxy não confirmou o hardware; o baseline venceu após a mitigação. A calibração declarada não foi suficiente para prever o Bell.
- Próxima ação: usar o layout baseline como referência e testar um candidato alternativo na próxima iteração.
- Score (1 - TVD mitigada do otimizado): 0.9832.

## Limites

- Simulação não é hardware; o modelo depolarizante não prevê fidelidade.
- Uma execução por caso não é estudo estatístico.
- A calibração |11> usa `rx(pi)` e inclui preparação do |1>.
- A matriz 4x4 corrige 01/10, mas não state preparation, crosstalk ou deriva.
- Não há ZNE, PEC, DD ou correção quântica de erro.
- O loop registra lições; não promove confiança automaticamente.
