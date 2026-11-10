# R1142–R1143 — Piloto de classificação quântica e cozimento como otimização

**Status:** simulação local; nenhum hardware executado.
**Artefatos:** `harnesses/quantum-error-mitigation/resultados/r1142_research/`.

## 1. Classificação quântica

O primeiro piloto (16/16, ZZ fixo) deu kernel quântico **0,625** vs RBF
**0,875**. A busca melhorada usa **treino/validação/teste** (48/16/16), feature
maps ZZ/angle/reupload, escalas, repetições e regularização; a escolha é feita
**na validação** e o teste não participa.

Resultado multi-seed (3 seeds), teste de 16 pontos:

| Ruído | Quântico (média ± dp) | Projetado | RBF clássico |
|---|---:|---:|---:|
| 0,15 | 0,854 ± 0,072 | 0,792 ± 0,072 | **0,896 ± 0,072** |
| 0,20 | **0,833 ± 0,036** | 0,833 ± 0,130 | 0,771 ± 0,036 |

Não há vantagem robusta: o clássico vence no ruído 0,15; o quântico vence no
ruído 0,20, mas o teste tem só 16 pontos e alta variância. O resultado é
registrado como dependente do regime, não como vantagem quântica.

## 2. Cozimento como otimização

“Cozimento quântico” não é um campo estabelecido na literatura consultada. O
piloto trata quatro decisões de processo como QUBO sintético:

- temperatura alta;
- tempo longo;
- coberto;
- pré-aquecido.

| Método | Energia | Razão |
|---|---:|---:|
| Brute force | **−2,6000** | 1,000 |
| QAOA p=1 | −2,1298 | 0,742 |
| QAOA p=2 | −2,3443 | 0,860 |
| QAOA p=3 | **−2,4623** | **0,925** |
| Baseline aleatório | 0,8750 (média) | — |

A profundidade p=3 melhorou a razão de 0,742 para **0,925**, mas ainda não
alcança o ótimo exato. O resultado é sintético e não tem interpretação
culinária.

## 3. O que o framework entrega

- `quantum_research.classification`: dataset, feature map, kernel, kernel
  ridge, RBF, leakage e métricas.
- `quantum_research.cooking`: QUBO, brute force, QAOA e baseline.
- `gjq_research_framework.plan(domain="classification"|"cooking")`: fases,
  gates e agentes.
- MCP `gjq_research_status` e `gjq_research_plan`.

## 4. Gaps e próximos passos

1. **Kernel quântico abaixo do clássico:** testar feature maps, bandwidth,
   normalização, regularização e curvas de aprendizado; não ajustar no teste.
2. **Amostra pequena:** aumentar n e pré-registrar; reportar IC.
3. **Sem ruído:** simular ruído/shots e medir degradação.
4. **Cozimento sem literatura quântica:** manter QUBO sintético, baseline
   clássico e validação sensorial antes de qualquer alegação.
5. **QAOA p=1:** aumentar profundidade só com orçamento e comparação clássica;
   não declarar vantagem.

## 5. Limites

- Dataset e QUBO sintéticos; nenhum dado real.
- Sem hardware, sem ruído real, sem validação sensorial.
- Nenhum resultado demonstra vantagem quântica.
- Fontes: Havlíček 2019; Schuld & Killoran 2019; Huang 2021; Caro 2022;
  Cerezo 2021; artigo clássico de cozimento 2026.
