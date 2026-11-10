# SPEC-935-R1142 — Classificação quântica e cozimento como otimização

**Status:** implementação local, sem hardware
**Data:** 2026-11-10
**Depende de:** R1141
**Fontes:** Havlíček 2019; Schuld & Killoran 2019; Huang 2021; Caro 2022;
Cerezo 2021; artigo clássico de cozimento 2026.

## 1. Objetivo

Adicionar ao framework de pesquisa do Core duas capacidades:

- **classificação quântica** com feature map, kernel, baseline clássico e
  auditoria de vazamento;
- **cozimento** como otimização de processo em QUBO sintético, com brute force
  e QAOA.

## 2. Requisitos

- **R1.** `quantum_research.classification`: dados, feature map ZZ, kernel,
  kernel ridge, RBF, acurácia, confusão e leakage.
- **R2.** `quantum_research.cooking`: QUBO, brute force, QAOA e baseline.
- **R3.** `domain` no plano do framework, com fases/gates/agentes.
- **R4.** Nenhum hardware, ruído real ou dados sensoriais.
- **R5.** Declarar que “cozimento quântico” não é campo estabelecido.
- **R6.** Testes e documentação.

## 3. Critérios

- kernel próprio = 1 e simétrico;
- split sem vazamento;
- acurácias entre 0 e 1;
- brute force do QUBO < 0;
- QAOA ≥ ótimo e ratio em [0,1];
- `domain="classification"` roteia agente e fases;
- `domain="cooking"` inclui validação sensorial;
- nenhuma string de hardware nos módulos.

## 4. Limites

Dataset e QUBO são sintéticos. Não há prova de vantagem quântica, qualidade
culinária, generalização real ou superioridade sobre baselines clássicos.
