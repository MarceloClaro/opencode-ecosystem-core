# Resultado real — Baihua / E05 (Bell)

| Campo | Valor |
|---|---|
| Task ID | `1aeb1d6b-4d5b-4ecf-a434-789c579635d1` |
| Backend | Baihua (hardware supercondutor, 156 qubits) |
| Shots | 1024 |
| Submissão local | 2026-11-09T11:25:17-03:00 |
| Carimbo do backend | 2026-11-09T22:25:18Z (offset de 8 h consistente com CST) |
| Status | DONE |

## Counts observados

| Bitstring | Contagem | Probabilidade | Erro padrão |
|---|---:|---:|---:|
| `00` | 489 | 0.477539 | 0.015609 |
| `11` | 449 | 0.438477 | 0.015506 |
| `10` | 48 | 0.046875 | 0.006605 |
| `01` | 38 | 0.037109 | 0.005907 |
| **Total** | **1024** | **1.000000** | — |

## Métricas descritivas

- Fração de outcomes correlacionados `00`/`11`: **0.9160** (± 0.0087, 1σ).
- TVD observada vs distribuição ideal de Bell (`00=0,5`, `11=0,5`): **0.0840**.
- Erro proxy do otimizador no ponto escolhido: **0.0060**.
- O proxy de erro é um produto de `(1 - erro)` por porta e leitura; ele não modela state preparation, crosstalk, deriva, leakage ou correlação. Nesta execução, o proxy foi otimista em relação à TVD observada.

## Circuito e calibração

- Layout lógico → físico: `108 qubits no QASM; qubits físicos usados: 106 e 107`.
- Portas: `{'h': 3, 'measure': 2, 'cz': 1}`.
- Fingerprint do perfil: `f79a19730b1c5cc025e344a5dacbb0ae0d67227f3a6cd936ad99f8cabed543de`.
- Calibração registrada: 2026-11-09 17:24:32-03:00.
- Erro 1q de `h` em q106/q107: 1.000e-03 / 1.000e-03.
- Erro 1q de `rx` em q106/q107: 1.000e-03 / 1.000e-03.
- Erro 2q de `cz(106,107)`: 1.000e-03.
- Erro de leitura q106/q107: 1.000e-03 / 1.000e-03.
- QASM2 SHA-256: `b1451f60e7ed649253f7fca96774ea0adebbc0d4168f007b2bc5b17671c2bde8`.

## Limites

- Uma execução de 1024 shots não prova fidelidade, emaranhamento, vantagem quântica ou interpretação de Bohm.
- A fração `00`/`11` é uma taxa de outcomes correlacionados, não é fidelidade de estado.
- A calibração muda; o resultado vale para a janela e o perfil registrados.
- Não reenvie o mesmo circuito sem necessidade; reutilize o task ID.
