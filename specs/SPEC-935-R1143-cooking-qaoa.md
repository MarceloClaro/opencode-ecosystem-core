# SPEC-935-R1143 — QAOA para QUBO de processo culinário

**Status:** implementação local, sem hardware
**Depende de:** R1142
**Fonte de método:** QAOA/VQE; baseline clássico de cozimento 2026.

## 1. Objetivo

Formalizar um QUBO de quatro decisões de processo (temperatura, tempo,
cobertura, pré-aquecimento), resolver por brute force e QAOA p=1 simulada, e
comparar com baseline aleatório.

## 2. Requisitos

- **R1.** `energy(bits)` para o QUBO.
- **R2.** `brute_force()` exato.
- **R3.** `cost_operator()` e `QAOAAnsatz` p=1.
- **R4.** `qaoa_audit()` com energia, bits, probabilidade, ratio e baseline.
- **R5.** Nenhum hardware, dados sensoriais ou alegação de vantagem.
- **R6.** Testes.

## 3. Critérios

- brute force retorna energia negativa e bits válidos;
- QAOA ≥ ótimo (tol. 1e-9);
- ratio em [0,1];
- `synthetic=True`, `hardware_executed=False`;
- limites citam ausência de ciência de alimentos.

## 4. Limites

QUBO sintético de 4 variáveis; QAOA p=1 não escala. Qualquer aplicação real
exige dados, restrições, baseline clássico e validação sensorial.
