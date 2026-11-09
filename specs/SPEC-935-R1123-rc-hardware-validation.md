# SPEC-935-R1123 — Validação de RC em hardware: baseline vs twirlado

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** R1119 (Pauli-frame), R1120 (pré-registro)

## 1. Contexto

O passe de Pauli-frame existe e foi verificado. Falta a validação em hardware:
comparar o mesmo circuito lógico com e sem twirl de Pauli.

## 2. Desenho

- Circuito base de 2 qubits: `h(0)`, `h(1)`, `cz(0,1)`, `h(0)`, medição.
- Braço baseline: 4 jobs idênticos por conjunto.
- Braço twirlado: 4 seeds diferentes por conjunto.
- 2 conjuntos × 4 circuitos por braço = 16 jobs.
- Shots por job: 9.600 (meia-largura 0,01; p=0,5; 95%).
- Ordem intercalada baseline/twirlado para reduzir viés de drift.
- Métrica: TVD contra a distribuição ideal de 4 resultados.
- Análise: média por braço, Δ = twirlado − baseline, bootstrap aninhado
  (shots + jobs), IC 95%.

## 3. Critérios de decisão

- **Twirlado melhor:** Δ < 0 e limite superior do IC < 0.
- **Sem efeito detectável:** IC inclui 0.
- **Twirlado pior:** Δ > 0 e limite inferior do IC > 0.

## 4. Requisitos

- **R1.** Verificar equivalência up to fase para cada circuito twirlado.
- **R2.** Submeter sem retranspilar; usar portas padrão X/Y/Z no twirl.
- **R3.** TDD antes de hardware; simulação antes de submissão.
- **R4.** `confirm=True` e `allow_hardware=True`.
- **R5.** Não declarar melhora sem IC excluindo zero.
- **R6.** Reportar n, seeds, task IDs e limites.
- **R7.** Nenhuma chave em arquivo/log.
- **R8.** O resultado negativo também é válido e deve ser reportado.

## 5. Não objetivos

- Provar RC universal.
- Separar todos os erros coerentes.
- Declarar vantagem quântica.
- Comparar layouts.
