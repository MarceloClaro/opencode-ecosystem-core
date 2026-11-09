# Resiliência quântica híbrida — R1116

**Status:** implementação local
**Spec:** `specs/SPEC-935-R1116-quantum-resilience-scorecard.md`
**Módulo:** `quantum_mitigation/resilience.py`
**Comando:** `harnesses/quantum-error-mitigation/runner.py resilience`

## 1. O que o scorecard faz

Lê evidências de técnicas diferentes e responde:

- qual técnica está bloqueada e por quê;
- qual qubit/etapa é o gargalo;
- qual próximo passo é efetivo;
- qual técnica não deve ser usada como se fosse equivalente.

Ele **não** soma créditos de técnicas diferentes e **não** declara vantagem.

## 2. Entradas

| Evidência | O que fornece |
|---|---|
| Readout 4×4 | TVD mitigada baseline/otimizado |
| Tomografia q0 | fidelidade de preparação e r0/r1 |
| Tomografia q1 | fidelidade de preparação e r0/r1, com bootstrap |
| ZNE | monotonicidade e extrapolação |
| PEC | gamma e amostras necessárias |
| Bootstrap | largura dos ICs |
| Superfície/pulse DD | flags de planejamento |

## 3. Resultado atual com os artefatos reais

Com os dados de q0/q1/ZNE/readout/PEC:

- **Status:** `partial`.
- **Readout 4×4:** baseline venceu o layout otimizado.
- **q0 (2 conjuntos):** prep mínima 0,9235; prep coerente 0,9850; r0=0,0161; r1=0,0765.
- **q1 (2 conjuntos):** prep mínima 0,9163; prep coerente 0,9823; r0=0,0159; r1=0,0837.
- **Δ q1−q0:** r1 +0,0072, mas ICs se sobrepõem e o Δ é menor que o spread
  entre conjuntos; a diferença **não é conclusiva**.
- **Redundância:** prep |0>/|1> = 1 − r0/r1; não são duas evidências.
- **ZNE:** bloqueado por não monotonicidade.
- **PEC:** gamma≈1,006; amostras≈10.121 (orçamento baixo, mas 15 taxas não caracterizadas).
- **Incerteza:** maior largura de IC 0,0121.
- **Superfície:** bloqueada por falta de decodificador em tempo real.
- **DD pulse-level:** bloqueado por falta de acesso de pulso.

Recomendações:

1. Não promover o layout otimizado; usar baseline como referência.
2. Medir mais conjuntos para leitura em q1 antes de atribuir a diferença de r1 a q1.
3. Aplicar/expandir mitigação de leitura em q0 e q1 (r1 > 0,05).
4. Não comparar layouts antes de preparação coerente ≥ 0,99 em ambos os qubits.
5. Aumentar repetições antes de concluir.

## 4. Comando

```bash
.venv-quantum/bin/python harnesses/quantum-error-mitigation/runner.py resilience \
  --readout comparacao.json \
  --zne zne.json \
  --tomography-q0 tomography.json \
  --tomography-q1 comparison.json \
  --comparison comparison_q0_q1.json \
  --pec pec.json \
  --surface --pulse-dd \
  --out resultados/resilience
```

## 5. Limites

- Scorecard heurístico; não é certificado.
- As técnicas têm hipóteses diferentes; a comparação é local.
- Não executa hardware.
- Não declara vantagem quântica, threshold ou fidelidade.
- q0 e q1 têm dois conjuntos cada; a comparação é descritiva.
- Prep |0>/|1> e r0/r1 são a mesma contagem Z; não são evidências independentes.
