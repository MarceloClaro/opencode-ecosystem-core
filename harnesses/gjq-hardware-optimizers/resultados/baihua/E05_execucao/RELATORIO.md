# Otimização para hardware GJQ — resultado

Perfil **Baihua** · tipo `gjq_live_target` · fingerprint `f79a19730b1c5cc0…`.

## Protocolo

- Baseline: layout trivial, roteamento basic, nível 1.
- Candidatos: layout noise-aware, Sabre e Dense; níveis e seeds declarados.
- Seleção: erro proxy, profundidade, 2q e tamanho, conforme a estratégia.
- Gate de correção: o circuito escolhido usa apenas portas base e arestas do perfil.
- Nenhum job foi submetido por este relatório.

## Perfil

- Qubits: **156** · arestas: **256**.
- Portas 1q: h, rx, ry, rz.
- Portas 2q: cz.
- Erro 1q médio: 1.994e-03 · máximo: 2.100e-02.
- Erro 2q médio: 2.373e-02 · máximo: 1.100e-01.
- Erro de leitura médio: 1.994e-03 · máximo: 2.100e-02.
- Calibração: `backend.target + backend.properties (live)` · atualização: 2026-11-09 17:24:32-03:00.

## Layout

- Método: `exact`.
- Layout lógico → físico: `[106, 107]`.
- Região física conectada: `[106, 107]`.
- Custo do layout: 3.750e-03 · custo trivial: 3.150e-02.

## Baseline vs escolhido

| Métrica | Baseline | Escolhido | Δ |
|---|---:|---:|---:|
| Erro proxy | 3.379e-02 | 5.985e-03 | +2.781e-02 |
| Sucesso proxy | 9.662e-01 | 9.940e-01 | 1.029× |
| 2q | 1 | 1 | +0 |
| Profundidade | 4 | 4 | +0 |
| Size | 6 | 6 | +0 |

Estratégia: `balanced` · candidato escolhido: `noise_aware` nível 1, seed 42.

## Candidatos

| Candidato | Nível | Seed | Layout | Roteamento | 2q | Depth | Size | Erro proxy | Sucesso | Status |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---|
| noise_aware **escolhido** | 1 | 42 | initial_layout | sabre | 1 | 4 | 6 | 5.985e-03 | 9.940e-01 | pass |
| noise_aware | 3 | 42 | initial_layout | sabre | 1 | 4 | 6 | 5.985e-03 | 9.940e-01 | pass |
| sabre | 1 | 42 | sabre | sabre | 1 | 4 | 6 | 3.840e-02 | 9.616e-01 | pass |
| dense | 1 | 42 | dense | sabre | 1 | 4 | 6 | 8.970e-03 | 9.910e-01 | pass |
| sabre | 3 | 42 | sabre | sabre | 1 | 4 | 6 | 3.840e-02 | 9.616e-01 | pass |
| dense | 3 | 42 | dense | sabre | 1 | 4 | 6 | 8.970e-03 | 9.910e-01 | pass |

## Limites

- Métricas de compilação e proxy de erro; não é execução física.
- O proxy não mede fidelidade de estado, crosstalk, leakage ou deriva.
- A calibração muda; releia `backend.properties` antes de comparar execuções.
- Redução de portas ou de erro proxy não é vantagem quântica.
- Nenhum job foi submetido por este relatório.
