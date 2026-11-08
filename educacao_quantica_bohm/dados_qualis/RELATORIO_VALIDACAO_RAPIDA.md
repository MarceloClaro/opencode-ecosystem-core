# Validação rápida: 2 e 4 qubits, 5 folds

Modelo efetivo no qubit medido: phase damping preserva P(1);
depolarizing mistura com 1/2; amplitude damping multiplica por (1-γ).
A métrica é acurácia de teste; o IC95% é bootstrap sobre os folds.

| n | Configuração | Acurácia teste | Desvio | IC95 |
|---:|---|---:|---:|---|
| 2 | baseline | 0.586 | 0.117 | [0.486, 0.671] |
| 2 | phase_005 | 0.586 | 0.117 | [0.486, 0.671] |
| 2 | depol_005 | 0.586 | 0.117 | [0.486, 0.671] |
| 2 | amp_005 | 0.586 | 0.117 | [0.486, 0.671] |
| 2 | phase_050 | 0.586 | 0.117 | [0.486, 0.671] |
| 2 | depol_050 | 0.586 | 0.117 | [0.486, 0.671] |
| 2 | amp_050 | 0.571 | 0.143 | [0.443, 0.671] |
| 4 | baseline | 0.343 | 0.137 | [0.257, 0.471] |
| 4 | phase_005 | 0.343 | 0.137 | [0.257, 0.471] |
| 4 | depol_005 | 0.343 | 0.137 | [0.257, 0.471] |
| 4 | amp_005 | 0.343 | 0.137 | [0.257, 0.471] |
| 4 | phase_050 | 0.343 | 0.137 | [0.257, 0.471] |
| 4 | depol_050 | 0.343 | 0.137 | [0.257, 0.471] |
| 4 | amp_050 | 0.314 | 0.193 | [0.200, 0.486] |

## Leitura

- **Phase damping** tem a mesma acurácia do baseline: o canal preserva
  populações Z, então um classificador que lê P(1) não pode melhorar por
  esse mecanismo no forward pass.
- **Depolarizing** e **amplitude damping** mudam P(1); nesta réplica, não
  produziram ganho consistente sobre o baseline.
- O IC95% é largo com 5 folds e 70 amostras. Um ganho de 3,5 pp precisa
  ser comparado a esse intervalo antes de ser chamado de efeito.

> **Veredito:** o sweet spot de γ≈0,005 não foi validado como mecanismo
> de melhora em 4 qubits. A afirmação original permanece exploratória.