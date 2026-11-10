---
name: correlacoes-arranjos-contraprovas
description: Audita correlações de erro de leitura, otimiza arranjos de qubits e exige contraprovas para inovações de mitigação. Use para estimar phi/p_ij, comparar layout ciente de correlação com layout só de marginais, encontrar contraexemplos de greedy e de reversão de regime, e formalizar a não-identificabilidade em Lean; não executa hardware, não prevê fidelidade real e não declara vantagem.
---

# Correlações, arranjos e contraprovas (SPEC-935-R1147)

## Quando acionar

- há counts de calibração e suspeita de erro de leitura correlacionado;
- é preciso escolher/rotar qubits considerando porta, leitura, crosstalk e
  correlação;
- uma “inovação” de mitigação precisa de contraprova antes de ser adotada;
- é preciso mostrar que marginais iguais podem esconder juntas diferentes.

Não acionar para hardware real, calibração oficial, crosstalk medido ou
alegação de vantagem.

## Contrato mínimo

1. counts com bit order declarado (Qiskit: caractere à direita = qubit 0);
2. qubits explícitos e shots;
3. marginais **e** co-ocorrências `p_ij`/`phi`;
4. cotas de união e delta contra o modelo independente;
5. dispositivo, interações, pesos de medição e modelo de custo;
6. contraprova: caso que falsifique ou limite a inovação;
7. hash do certificado Lean, quando houver.

Sem isso: protocolo, nunca veredito.

## Leitura correta do `phi`

Correlação positiva **aumenta** `P(0 erro)` e `P(2 erros)`, mas **diminui**
`P(exatamente 1 erro)` e pode **diminuir** `P(≥1 erro)`. Portanto:

- não dizer “correlação sempre piora”;
- não usar só marginais para decidir layout;
- reportar o estatístico usado (fidelidade, erro duplo, união).

## Fluxo

```bash
# correlação + arranjos
.venv-quantum/bin/python -m pytest tests/test_r1147_correlation_layout.py -q

# contraprova formal + certificado
.venv-quantum/bin/python -m quantum_mitigation.correlation_gate

# teste pesado dedicado
RUN_LEAN_CORRELATION=1 .venv-quantum/bin/python \
  -m pytest tests/test_r1147_correlation_gate.py -q
```

## Contraprovas obrigatórias

| Pergunta | Contraprova |
|---|---|
| marginais bastam? | duas tabelas com mesma marginal e junta diferente |
| greedy é ótimo? | `find_greedy_counterexample` com gap > 0 |
| o arranjo é universal? | `find_regime_reversal` com gap > 0 |
| correlação pode ser ignorada? | `correlation_blind_counterexample` |
| o modelo independente acerta? | comparar `delta_any_error` e cotas |

## Limites

Counts sintéticos; correlação de pares; custo proxy; sem agendamento ou
calibração real. O gate aceitar não promove confiança nem autoriza execução.
Nunca usar “provado” para afirmar vantagem quântica ou fidelidade real.
