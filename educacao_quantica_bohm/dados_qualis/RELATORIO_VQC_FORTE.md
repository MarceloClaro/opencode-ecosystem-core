# Validação forte do VQC: baseline, 2/4 qubits e ruído

3 camadas strongly entangling, COBYLA 120, 5 seeds, split 50/20.
A acurácia é de teste; o ruído é aplicado ao observable Z.

| n | Ruído | γ=0 | 0,005 | 0,01 | 0,05 | 0,10 |
|---:|---|---:|---:|---:|---:|---:|
| 2 | phase | 0.970 | 0.970 | 0.970 | 0.970 | 0.970 | 0.970 | 0.970 |
| 2 | depolarizing | 0.970 | 0.970 | 0.970 | 0.970 | 0.970 | 0.970 | 0.970 |
| 2 | amplitude | 0.970 | 0.970 | 0.970 | 0.970 | 0.970 | 0.970 | 0.960 |
| 2 | **baseline** | **0.970** | — | — | — | — |
| 4 | phase | 0.950 | 0.950 | 0.950 | 0.950 | 0.950 | 0.950 | 0.950 |
| 4 | depolarizing | 0.950 | 0.950 | 0.950 | 0.950 | 0.950 | 0.950 | 0.950 |
| 4 | amplitude | 0.950 | 0.950 | 0.950 | 0.950 | 0.940 | 0.940 | 0.930 |
| 4 | **baseline** | **0.950** | — | — | — | — |

## Leitura

- O baseline agora é **reproduzível** (ansatz de 3 camadas + COBYLA).
- Phase damping é **idêntico** ao baseline em todos os γ: preserva P(1).
- Depolarizing e amplitude damping não melhoram; em γ≥0,05 degradam.
- Com baseline próximo do teto, não há espaço para um ganho de +3,5 pp.

> **Veredito:** o baseline do relatório é plausível, mas o “ruído benéfico”
> não aparece no forward pass. A afirmação continua exploratória.