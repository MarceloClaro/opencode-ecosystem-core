# Comparação baseline vs otimizado — GJQ / Baihua

Gerado em 2026-11-09T11:43:02-03:00 · 4096 shots por circuito.

## Protocolo

- Mesmo circuito E05/Bell, mesmo target, mesma seed e mesmas portas base.
- Baseline: layout trivial-operacional, roteamento basic, nível 1.
- Otimizado: layout noise-aware, roteamento sabre, candidato escolhido.
- Submissão com `transpile=False`; nenhuma dupla transpilação.
- Calibração de leitura: |00> e |11> nos mesmos qubits físicos.

## Resultados

| Caso | Qubits | Erro proxy | Raw 00+11 | Raw TVD | Mitigado 00 | Mitigado 11 | TVD mitigada | Task ID |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| baseline | [0, 1] | 3.3793e-02 | 0.9329 | 0.0671 | 0.5249 | 0.4751 | 0.0249 | `ff6e6d03-5bdc-4a6c-ae58-7f222c38833e` |
| otimizado | [106, 107] | 5.9850e-03 | 0.8982 | 0.1018 | 0.5277 | 0.4723 | 0.0277 | `96cfb671-678f-40f6-b01b-02358f20478a` |

## Diferença (otimizado − baseline)

| Métrica | Δ |
|---|---:|
| Correlação raw 00/11 | -0.0347 |
| TVD raw vs ideal | +0.0347 |
| TVD mitigada | 0.0028 |

## Interpretação

- O proxy previa erro menor para **otimizado** (baseline 3.3793e-02; otimizado 5.9850e-03).
- No hardware, a correlação raw 00/11 foi 0.9329 no baseline e 0.8982 no otimizado.
- O ranking do proxy **não confirmou** o resultado observado; o caso com menor TVD raw foi **baseline**.
- Após a mitigação de leitura, a TVD foi 0.0249 no baseline e 0.0277 no otimizado; o caso com menor TVD mitigada foi **baseline**.
- Leakage de |11>: 14.1% no baseline e 15.0% no otimizado. A inversão 00/11 não corrige a população que sai para 01/10.
- Uma execução por caso, com 4096 shots, não é estudo estatístico; diferenças pequenas não sustentam vantagem.

## Calibração de leitura

### baseline

- Matriz de leitura: `[[0.9992445227902291, 0.007670454545454545], [0.0007554772097708386, 0.9923295454545454]]`.
- Leakage por estado preparado: `{'00': 0.030517578125, '11': 0.140625}`.
- Condição da matriz: 1.011.
- Massa negativa clipada: -0.000000.

### otimizado

- Matriz de leitura: `[[0.9997496871088861, 0.011490950876185005], [0.00025031289111389235, 0.988509049123815]]`.
- Leakage por estado preparado: `{'00': 0.024658203125, '11': 0.150146484375}`.
- Condição da matriz: 1.016.
- Massa negativa clipada: -0.000000.

## Limites

- Uma execução por caso não é estudo estatístico nem prova de vantagem.
- A calibração de leitura mede |00> e |11> nos mesmos qubits; |11> usa rx(pi) e inclui preparação do |1>, então não separa completamente readout de state preparation. Crosstalk, deriva e leakage fora do subespaço também não são capturados.
- A TVD mitigada é uma estimativa dentro do subespaço 00/11; não é fidelidade de estado.
- O proxy de erro é um produto de `(1 - erro)` por porta e leitura; não é fidelidade.
- Custo, fila e calibração podem mudar.
