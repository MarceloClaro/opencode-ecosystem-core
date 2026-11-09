# Comparação baseline vs otimizado — GJQ / Baihua

Gerado em 2026-11-09T19:01:21-03:00 · 4096 shots por circuito · 1 repetições.

## Protocolo

- Mesmo circuito E05/Bell, mesmo target, mesma seed e mesmas portas base.
- Baseline: layout trivial-operacional, roteamento basic, nível 1.
- Otimizado: layout noise-aware, roteamento sabre, candidato escolhido.
- Submissão com `transpile=False`; nenhuma dupla transpilação.
- Calibração de leitura: |00> e |11> nos mesmos qubits físicos.

## Resultados

| Caso | Qubits | Erro proxy | Raw 00+11 | Raw TVD | Mitigado 00 | Mitigado 11 | TVD mitigada | Task ID |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| baseline | [0, 1] | 3.3793e-02 | 0.9062 | 0.0938 | 0.5228 | 0.4772 | 0.0228 | `892898a5-e089-43a1-ae74-5194cfb00d49` |
| otimizado | [106, 107] | 5.9850e-03 | 0.9236 | 0.0764 | 0.5079 | 0.4921 | 0.0079 | `042e43b5-88e9-4d82-a8cc-20c99e8a7635` |

### Repetições — baseline

| Métrica | Média | Desvio | Mín. | Máx. |
|---|---:|---:|---:|---:|
| Raw 00/11 | 0.9062 | 0.0000 | 0.9062 | 0.9062 |
| TVD raw | 0.0938 | 0.0000 | 0.0938 | 0.0938 |
| TVD mitigada | 0.0228 | 0.0000 | 0.0228 | 0.0228 |
| Correlação mitigada | 1.0000 | 0.0000 | 1.0000 | 1.0000 |

### Repetições — otimizado

| Métrica | Média | Desvio | Mín. | Máx. |
|---|---:|---:|---:|---:|
| Raw 00/11 | 0.9236 | 0.0000 | 0.9236 | 0.9236 |
| TVD raw | 0.0764 | 0.0000 | 0.0764 | 0.0764 |
| TVD mitigada | 0.0079 | 0.0000 | 0.0079 | 0.0079 |
| Correlação mitigada | 1.0000 | 0.0000 | 1.0000 | 1.0000 |


## Diferença (otimizado − baseline)

| Métrica | Δ |
|---|---:|
| Correlação raw 00/11 | +0.0173 |
| TVD raw vs ideal | -0.0173 |
| TVD mitigada | -0.0149 |

## Interpretação

- O proxy previa erro menor para **otimizado** (baseline 3.3793e-02; otimizado 5.9850e-03).
- No hardware, a correlação raw 00/11 foi 0.9062 no baseline e 0.9236 no otimizado.
- O ranking do proxy **confirmou** o resultado observado; o caso com menor TVD raw foi **otimizado**.
- Após a mitigação de leitura, a TVD foi 0.0228 no baseline e 0.0079 no otimizado; o caso com menor TVD mitigada foi **otimizado**.
- Leakage de |11>: 12.2% no baseline e 15.8% no otimizado. A inversão 00/11 não corrige a população que sai para 01/10.
- 1 repetições de 4096 shots por caso; a incerteza é a dispersão entre repetições, não uma prova estatística definitiva.

## Calibração de leitura

### baseline

- Matriz de leitura: `[[1.0, 0.006397774687065368], [0.0, 0.9936022253129346]]`.
- Leakage por estado preparado: `{'00': 0.026611328125, '11': 0.122314453125}`.
- Condição da matriz: 1.009.
- Massa negativa clipada: -0.000000.

### otimizado

- Matriz de leitura: `[[1.0, 0.00899332753118654], [0.0, 0.9910066724688135]]`.
- Leakage por estado preparado: `{'00': 0.01953125, '11': 0.158447265625}`.
- Condição da matriz: 1.013.
- Massa negativa clipada: -0.000000.

## Limites

- Repetições estimam dispersão; não são prova estatística definitiva.
- A calibração |00>/|11> não corrige 01/10; |11> usa rx(pi) e inclui preparação do |1>. Crosstalk e deriva não são capturados.
- A TVD mitigada é uma estimativa no subespaço 00/11; não é fidelidade de estado.
- O proxy de erro é um produto de `(1 - erro)` por porta e leitura; não é fidelidade.
- Custo, fila e calibração podem mudar.
