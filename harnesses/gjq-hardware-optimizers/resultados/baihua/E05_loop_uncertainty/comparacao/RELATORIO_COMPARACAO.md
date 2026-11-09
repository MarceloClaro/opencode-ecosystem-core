# Comparação baseline vs otimizado — GJQ / Baihua

Gerado em 2026-11-09T13:39:08-03:00 · 8192 shots por circuito · 3 repetições.

## Protocolo

- Mesmo circuito E05/Bell, mesmo target, mesma seed e mesmas portas base.
- Baseline: layout trivial-operacional, roteamento basic, nível 1.
- Otimizado: layout noise-aware, roteamento sabre, candidato escolhido.
- Submissão com `transpile=False`; nenhuma dupla transpilação.
- Calibração de leitura: |00>, |01>, |10> e |11> nos mesmos qubits físicos.

## Resultados

| Caso | Qubits | Erro proxy | Raw 00+11 | Raw TVD | Mitigado 00 | Mitigado 11 | TVD mitigada | Task ID |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| baseline | [0, 1] | 3.3793e-02 | 0.9268 | 0.0732 | 0.4909 | 0.5090 | 0.0091 | `b95a5e17-68da-4e17-b17f-7aaaa7cc506b` |
| optimized | [106, 107] | 5.9850e-03 | 0.9152 | 0.0848 | 0.4956 | 0.4876 | 0.0168 | `20ae794b-9a3c-4e61-b344-1956fd3fdeec` |

## Mitigação 4x4

| Caso | Estado | Raw | Mitigado |
|---|---:|---:|---:|
| baseline | `00` | 0.478027 | 0.490878 |
| baseline | `01` | 0.041626 | 0.000131 |
| baseline | `10` | 0.031535 | 0.000000 |
| baseline | `11` | 0.448812 | 0.508990 |
| optimized | `00` | 0.485555 | 0.495583 |
| optimized | `01` | 0.036092 | 0.000000 |
| optimized | `10` | 0.048747 | 0.016789 |
| optimized | `11` | 0.429606 | 0.487628 |

### Repetições — baseline

| Métrica | Média | Desvio | Mín. | Máx. |
|---|---:|---:|---:|---:|
| Raw 00/11 | 0.9268 | 0.0018 | 0.9248 | 0.9279 |
| TVD raw | 0.0732 | 0.0018 | 0.0721 | 0.0752 |
| TVD mitigada | 0.0092 | 0.0029 | 0.0058 | 0.0109 |
| Correlação mitigada | 0.9998 | 0.0003 | 0.9994 | 1.0000 |

### Repetições — optimized

| Métrica | Média | Desvio | Mín. | Máx. |
|---|---:|---:|---:|---:|
| Raw 00/11 | 0.9152 | 0.0034 | 0.9125 | 0.9189 |
| TVD raw | 0.0848 | 0.0034 | 0.0811 | 0.0875 |
| TVD mitigada | 0.0168 | 0.0019 | 0.0147 | 0.0183 |
| Correlação mitigada | 0.9832 | 0.0019 | 0.9817 | 0.9853 |


## Diferença (otimizado − baseline)

| Métrica | Δ |
|---|---:|
| Correlação raw 00/11 | -0.0117 |
| TVD raw vs ideal | +0.0117 |
| TVD mitigada | +0.0077 |

## Interpretação

- O proxy previa erro menor para **otimizado** (baseline 3.3793e-02; otimizado 5.9850e-03).
- No hardware, a correlação raw 00/11 foi 0.9268 no baseline e 0.9152 no otimizado.
- O ranking do proxy **não confirmou** o resultado observado; o caso com menor TVD raw foi **baseline**.
- Após a mitigação de leitura, a TVD foi 0.0091 no baseline e 0.0168 no otimizado; o caso com menor TVD mitigada foi **baseline**.
- 3 repetições de 8192 shots por caso; a incerteza é a dispersão entre repetições, não uma prova estatística definitiva.

## Calibração de leitura

### baseline

- Matriz de leitura: `[[0.9666748046875, 0.058349609375, 0.078125, 0.00390625], [0.015380859375, 0.9254150390625, 0.0008544921875, 0.06640625], [0.0177001953125, 0.0013427734375, 0.90771484375, 0.0513916015625], [0.000244140625, 0.014892578125, 0.0133056640625, 0.8782958984375]]`.
- Leakage por estado preparado: `{}`.
- Condição da matriz: 1.217.
- Massa negativa clipada: 0.003794.

### optimized

- Matriz de leitura: `[[0.9715576171875, 0.057861328125, 0.0718994140625, 0.00390625], [0.012451171875, 0.9273681640625, 0.00048828125, 0.0654296875], [0.0157470703125, 0.000732421875, 0.9183349609375, 0.0521240234375], [0.000244140625, 0.0140380859375, 0.00927734375, 0.8785400390625]]`.
- Leakage por estado preparado: `{}`.
- Condição da matriz: 1.210.
- Massa negativa clipada: 0.002240.

## Limites

- Repetições estimam dispersão; não são prova estatística definitiva.
- A matriz 4x4 corrige 01/10; |11> usa rx(pi) e inclui preparação do |1>, então não separa completamente readout de state preparation. Crosstalk e deriva não são capturados.
- A TVD mitigada é uma estimativa sobre os 4 estados; não é fidelidade de estado.
- O proxy de erro é um produto de `(1 - erro)` por porta e leitura; não é fidelidade.
- Custo, fila e calibração podem mudar.
