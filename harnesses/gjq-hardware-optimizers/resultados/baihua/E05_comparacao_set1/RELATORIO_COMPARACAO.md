# Comparação baseline vs otimizado — GJQ / Baihua

Gerado em 2026-11-09T18:57:34-03:00 · 4096 shots por circuito · 1 repetições.

## Protocolo

- Mesmo circuito E05/Bell, mesmo target, mesma seed e mesmas portas base.
- Baseline: layout trivial-operacional, roteamento basic, nível 1.
- Otimizado: layout noise-aware, roteamento sabre, candidato escolhido.
- Submissão com `transpile=False`; nenhuma dupla transpilação.
- Calibração de leitura: |00> e |11> nos mesmos qubits físicos.

## Resultados

| Caso | Qubits | Erro proxy | Raw 00+11 | Raw TVD | Mitigado 00 | Mitigado 11 | TVD mitigada | Task ID |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| baseline | [0, 1] | 3.3793e-02 | 0.9099 | 0.0901 | 0.5263 | 0.4737 | 0.0263 | `65c01d2b-2e64-406a-8f48-fd194d2d99bb` |
| otimizado | [106, 107] | 5.9850e-03 | 0.9236 | 0.0764 | 0.5153 | 0.4847 | 0.0153 | `61099ada-0562-4ace-8523-67f58f131a25` |

### Repetições — baseline

| Métrica | Média | Desvio | Mín. | Máx. |
|---|---:|---:|---:|---:|
| Raw 00/11 | 0.9099 | 0.0000 | 0.9099 | 0.9099 |
| TVD raw | 0.0901 | 0.0000 | 0.0901 | 0.0901 |
| TVD mitigada | 0.0263 | 0.0000 | 0.0263 | 0.0263 |
| Correlação mitigada | 1.0000 | 0.0000 | 1.0000 | 1.0000 |

### Repetições — otimizado

| Métrica | Média | Desvio | Mín. | Máx. |
|---|---:|---:|---:|---:|
| Raw 00/11 | 0.9236 | 0.0000 | 0.9236 | 0.9236 |
| TVD raw | 0.0764 | 0.0000 | 0.0764 | 0.0764 |
| TVD mitigada | 0.0153 | 0.0000 | 0.0153 | 0.0153 |
| Correlação mitigada | 1.0000 | 0.0000 | 1.0000 | 1.0000 |


## Diferença (otimizado − baseline)

| Métrica | Δ |
|---|---:|
| Correlação raw 00/11 | +0.0137 |
| TVD raw vs ideal | -0.0137 |
| TVD mitigada | -0.0110 |

## Interpretação

- O proxy previa erro menor para **otimizado** (baseline 3.3793e-02; otimizado 5.9850e-03).
- No hardware, a correlação raw 00/11 foi 0.9099 no baseline e 0.9236 no otimizado.
- O ranking do proxy **confirmou** o resultado observado; o caso com menor TVD raw foi **otimizado**.
- Após a mitigação de leitura, a TVD foi 0.0263 no baseline e 0.0153 no otimizado; o caso com menor TVD mitigada foi **otimizado**.
- Leakage de |11>: 16.1% no baseline e 12.7% no otimizado. A inversão 00/11 não corrige a população que sai para 01/10.
- 1 repetições de 4096 shots por caso; a incerteza é a dispersão entre repetições, não uma prova estatística definitiva.

## Calibração de leitura

### baseline

- Matriz de leitura: `[[1.0, 0.011641443538998836], [0.0, 0.9883585564610011]]`.
- Leakage por estado preparado: `{'00': 0.034912109375, '11': 0.1611328125}`.
- Condição da matriz: 1.017.
- Massa negativa clipada: -0.000000.

### otimizado

- Matriz de leitura: `[[0.999749498997996, 0.005591277606933185], [0.000250501002004008, 0.9944087223930668]]`.
- Leakage por estado preparado: `{'00': 0.025390625, '11': 0.126708984375}`.
- Condição da matriz: 1.008.
- Massa negativa clipada: -0.000000.

## Limites

- Repetições estimam dispersão; não são prova estatística definitiva.
- A calibração |00>/|11> não corrige 01/10; |11> usa rx(pi) e inclui preparação do |1>. Crosstalk e deriva não são capturados.
- A TVD mitigada é uma estimativa no subespaço 00/11; não é fidelidade de estado.
- O proxy de erro é um produto de `(1 - erro)` por porta e leitura; não é fidelidade.
- Custo, fila e calibração podem mudar.
