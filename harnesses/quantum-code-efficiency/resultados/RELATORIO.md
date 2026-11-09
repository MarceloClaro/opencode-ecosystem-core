# Eficiência de código quântico — relatório

Gerado em 2026-11-09T08:57:15-03:00 · seed 42.

## Protocolo

- Baseline: `transpile(..., optimization_level=0)`.
- Otimizado: `transpile(..., optimization_level=3)`.
- Portas base: `u`, `cx`; roteamento quando o benchmark tem coupling map.
- Gate de correção: TVD ≤ 1e-09 entre as distribuições ideais.
- Sem hardware e sem rede.

## Resumo

- Benchmarks: **7**
- Pass: **7** · Fail: **0**
- TVD médio: **9.021e-17**
- Redução média de 2q: **31.3%**
- Redução média de profundidade: **25.6%**

## Benchmarks

| Benchmark | 2q base | 2q opt | Δ2q | depth base | depth opt | Δdepth | TVD | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| bell | 1 | 1 | 0.0% | 3 | 3 | 0.0% | 0.00e+00 | pass |
| ghz4 | 3 | 3 | 0.0% | 5 | 5 | 0.0% | 0.00e+00 | pass |
| qft4 | 18 | 12 | 33.3% | 28 | 22 | 21.4% | 1.53e-16 | pass |
| vqe2 | 1 | 1 | 0.0% | 4 | 4 | 0.0% | 0.00e+00 | pass |
| layered4 | 9 | 9 | 0.0% | 14 | 11 | 21.4% | 2.29e-16 | pass |
| redundant | 2 | 0 | 100.0% | 6 | 2 | 66.7% | 1.93e-33 | pass |
| nonadjacent | 7 | 1 | 85.7% | 10 | 3 | 70.0% | 2.50e-16 | pass |

## Limites

- Métricas de transpilação e distribuição ideal; não é hardware.
- Não mede fidelidade de estado, calibração ou tempo de parede em backend.
- O resultado depende da versão do Qiskit, do seed e do conjunto de portas.
- Redução de portas não é, por si só, vantagem quântica.
