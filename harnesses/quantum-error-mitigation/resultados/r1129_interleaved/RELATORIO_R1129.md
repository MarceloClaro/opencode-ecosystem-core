# R1129 — CB intercalado com 13 funções

Simulação exata, sem hardware. Fonte: Chen et al., Nat. Commun. 14, 52 (2023), DOI 10.1038/s41467-022-35759-4.

## Desenho

- Funções: **13** (7 individuais + 6 pares).
- Matriz: 13×15; posto **13**; nulidade **2**.
- Resíduo de incidência: 0.00e+00.
- Funções de corte não medidas: **2**.

## Recuperação exata

- Funções recuperadas: **13/13**.
- Erro absoluto máximo: **3.33e-16**.

| Ciclo | f estimado | f verdadeiro | erro |
|---|---:|---:|---:|
| IZ | 0.968506582 | 0.968506582 | 1.11e-16 |
| ZI | 0.968506582 | 0.968506582 | 1.11e-16 |
| XX | 0.968506582 | 0.968506582 | 1.11e-16 |
| XY | 0.968506582 | 0.968506582 | 1.11e-16 |
| YX | 0.968506582 | 0.968506582 | 1.11e-16 |
| YY | 0.968506582 | 0.968506582 | 1.11e-16 |
| ZZ | 0.968506582 | 0.968506582 | 1.11e-16 |
| IX·ZX | 0.938005000 | 0.938005000 | 2.22e-16 |
| IX·ZY | 0.938005000 | 0.938005000 | 2.22e-16 |
| IY·ZX | 0.938005000 | 0.938005000 | 2.22e-16 |
| XI·XZ | 0.938005000 | 0.938005000 | 3.33e-16 |
| XI·YZ | 0.938005000 | 0.938005000 | 3.33e-16 |
| YI·XZ | 0.938005000 | 0.938005000 | 3.33e-16 |

## Limites

13 funções aprendíveis; 2 funções de corte não são medidas. Ruído de Pauli antes do CZ, correções de 1 qubit ideais e profundidades pares. A hipótese de correções suficientemente menos ruidosas não foi validada no Baihua; nenhuma taxa foi medida e PEC 2q permanece bloqueado.

## Artefatos

- `interleaved_audit.json` — auditoria completa.
- `quantum_mitigation/interleaved_cb.py` — implementação.
- `tests/test_r1129_interleaved_cb.py` — contraprovas.
