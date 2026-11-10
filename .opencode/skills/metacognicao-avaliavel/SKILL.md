---
name: metacognicao-avaliavel
description: Torna a metacognição do Core avaliável em cinco camadas — EMA com psicometria, N-of-1/SCED, grafo de claims com prova/contraprova, trust warrant com Brier/ECE e contrato de runtime com hooks e circuit breaker. Use para medir subjetividade, ligar evidência real/complexa/irreal, exigir abstenção e bloquear ações de risco; não executa hardware, não substitui ética/clínica e não declara verdade.
---

# Metacognição avaliável (SPEC-935-R1148)

## Quando acionar

- há autorrelato, EMA, diário ou medida subjetiva;
- o desenho é N-of-1, caso único ou série temporal curta;
- é preciso ligar claims a fontes, trechos, testes, provas e contraprovas;
- o agente precisa separar “entregou” de “está calibrado”;
- uma ação irreversível ou de alto risco precisa de hooks e escalada.

Não acionar para diagnóstico clínico, prescrição, hardware ou promessa de
eficácia.

## Contrato mínimo

1. **EMA**: agenda, compliance, faltantes sem imputação, metadados
   psicométricos (instrumento, versão, escala, reliabilidade, validade, fonte,
   licença).
2. **N-of-1**: fases, randomização, seed, lock SHA-256, adesão, eventos
   adversos, plano de análise e critério de parada.
3. **Claims**: claim, fonte, trecho, teste, evidência real/complexa/irreal,
   arestas e proveniência.
4. **Trust**: histórico de previsão/outcome; sem histórico, abstenção.
5. **Runtime**: classe da ação, aprovação explícita, token e hooks.

Sem contrato: protocolo, nunca veredito.

## Comandos

```bash
# testes das cinco camadas
.venv-quantum/bin/python -m pytest tests/test_r1148_*.py -q

# relatório integrado (dados sintéticos)
.venv-quantum/bin/python -m json.tool \
  harnesses/metacognition/r1148/summary.json
```

## Regras fail-closed

| Situação | Saída |
|---|---|
| psicometria ausente | `blocked` / `insufficient_psychometric` |
| compliance < 0,7 | `insufficient_compliance` |
| lock N-of-1 divergente | `lock_mismatch` |
| evento adverso grave | `halted_adverse_event` |
| claim formal sem contraprova | `insufficient_formal` |
| evidência só irreal | `simulation_only`, abstenção |
| histórico < mínimo | `calibration_insufficient_data` |
| ECE acima do limite | `abstain=True` |
| ação irreversível sem aprovação | `escalated` |
| breaker aberto | `blocked` |

## Interpretação

- **coordenação** mede entrega; **warrant** mede calibração. Não confundir.
- correlação positiva pode aumentar `P(0 erro)` e `P(2 erros)` e diminuir
  `P(≥1 erro)`; reportar o estatístico.
- prova formal cobre o enunciado formal, não a eficácia empírica.
- evidência irreal é sintética/contrafactual: informa hipótese, não observação.
- abstenção é resultado válido, não falha.

## Limites

EMA e N-of-1 não substituem ética, consentimento, participante ou supervisão
clínica. Brier/ECE não provam verdade. O grafo liga evidência; não a inventa.
O contrato de runtime reduz repetição de falhas; não elimina risco. Nenhuma
vantagem quântica ou clínica é declarada.
