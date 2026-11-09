# Comparação baseline vs otimizado — GJQ / Baihua

Gerado em 2026-11-09T12:26:18-03:00 · 2048 shots por circuito.

## Protocolo

- Mesmo circuito E05/Bell, mesmo target, mesma seed e mesmas portas base.
- Baseline: layout trivial-operacional, roteamento basic, nível 1.
- Otimizado: layout noise-aware, roteamento sabre, candidato escolhido.
- Submissão com `transpile=False`; nenhuma dupla transpilação.
- Calibração de leitura: |00> e |11> nos mesmos qubits físicos.

## Resultados

| Caso | Qubits | Erro proxy | Raw 00+11 | Raw TVD | Mitigado 00 | Mitigado 11 | TVD mitigada | Task ID |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| baseline | [0, 1] | 3.3793e-02 | 0.9365 | 0.0635 | 0.5150 | 0.4850 | 0.0150 | `f36d0036-1994-4281-a42e-e7fcbf332bc0` |
| otimizado | [106, 107] | 5.9850e-03 | 0.9253 | 0.0747 | 0.5141 | 0.4859 | 0.0141 | `25fab68e-27d6-4ca2-9bb2-71908fc07d4c` |

## Diferença (otimizado − baseline)

| Métrica | Δ |
|---|---:|
| Correlação raw 00/11 | -0.0112 |
| TVD raw vs ideal | +0.0112 |
| TVD mitigada | -0.0009 |

## Interpretação

- O proxy previa erro menor para **otimizado** (baseline 3.3793e-02; otimizado 5.9850e-03).
- No hardware, a correlação raw 00/11 foi 0.9365 no baseline e 0.9253 no otimizado.
- O ranking do proxy **não confirmou** o resultado observado; o caso com menor TVD raw foi **baseline**.
- Após a mitigação de leitura, a TVD foi 0.0150 no baseline e 0.0141 no otimizado; o caso com menor TVD mitigada foi **otimizado**.
- Leakage de |11>: 11.2% no baseline e 13.4% no otimizado. A inversão 00/11 não corrige a população que sai para 01/10.
- Uma execução por caso, com 4096 shots, não é estudo estatístico; diferenças pequenas não sustentam vantagem.

## Calibração de leitura

### baseline

- Matriz de leitura: `[[1.0, 0.008796041781198461], [0.0, 0.9912039582188016]]`.
- Leakage por estado preparado: `{'00': 0.02685546875, '11': 0.11181640625}`.
- Condição da matriz: 1.013.
- Massa negativa clipada: -0.000000.

### otimizado

- Matriz de leitura: `[[1.0, 0.0062006764374295375], [0.0, 0.9937993235625705]]`.
- Leakage por estado preparado: `{'00': 0.02734375, '11': 0.1337890625}`.
- Condição da matriz: 1.009.
- Massa negativa clipada: -0.000000.

## Limites

- Uma execução por caso não é estudo estatístico nem prova de vantagem.
- A calibração de leitura mede |00> e |11> nos mesmos qubits; |11> usa rx(pi) e inclui preparação do |1>, então não separa completamente readout de state preparation. Crosstalk, deriva e leakage fora do subespaço também não são capturados.
- A TVD mitigada é uma estimativa dentro do subespaço 00/11; não é fidelidade de estado.
- O proxy de erro é um produto de `(1 - erro)` por porta e leitura; não é fidelidade.
- Custo, fila e calibração podem mudar.
