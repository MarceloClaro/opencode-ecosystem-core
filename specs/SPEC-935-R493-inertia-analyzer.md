# SPEC-935-R493 — Inércia Vetorial Analyzer (IVA)

Status: **implementado** (R493)
Data: 2026-09-13
Requer: R491 (PotentialityScanner), R492 (SuccessorGenerator); proposta do usuário
"Camada: Inércia Vetorial Analyzer (IVA)".

## 1. Contexto (proposta do usuário)

Mesmo com elevado potencial, uma capacidade pode não emergir: toda evolução
compete contra mecanismos de estabilidade do próprio sistema. O ecossistema já
responde "quão próximo isso está de emergir?" (Potentiality/Latent Potential);
falta responder **"o que está impedindo isso de emergir?"**.

## 2. Objetivos

- **OF1** — `InertiaVectorAnalyzer` computa resistência estrutural (inércia)
  em 4 componentes: complexidade arquitetural, dependências faltantes, custo
  de implementação, acoplamentos estruturais.
- **OF2** — Índice de Inércia Vetorial (QIV) = potencial − inércia, em [0,1].
- **OF3** — Classificação por faixas do usuário: Quebra Imediata (QIV > 0.70),
  Quebra Moderada (0.40 ≤ QIV ≤ 0.70), Inércia Dominante (QIV < 0.40).
- **OF4** — Relatório: obstáculos estruturais, dependências críticas, ranking
  de barreiras evolutivas, previsão de reorganização.

## 3. Modelo formal (heurística determinística documentada)

```
dependencias = 1 − coverage                 (fração de requires ausentes do DNA)
complexidade = min(1, n_requires / 5.0)     (mais componentes = mais mudança)
acoplamentos = média sobre requires de      (presentes em muitos módulos → alto)
               (módulos_contendo(c) − 1) / (n_total_modulos − 1 ou 1)
custo        = 0.5·dependencias + 0.3·complexidade + 0.2·0.4

inercia = 0.30·complexidade + 0.30·dependencias + 0.20·custo + 0.20·acoplamentos
QIV     = clamp(potencial − inercia, 0, 1)
barreira = soma das 4 forças (ranking: maior inercia = maior barreira)
```

Previsão de reorganização (hipóteses, não fatos): alta (quebra imediata),
moderada (quebra moderada), baixa (inércia dominante).

## 4. Critérios de aceitação

| ID | Critério |
|---|---|
| CA1 | Exemplo conceitual do usuário: potencial 0.82, inércia 0.27 → QIV = 0.55 (Quebra Moderada) |
| CA2 | Faixas: QIV > 0.70 → quebra-imediata; 0.40 ≤ QIV ≤ 0.70 → moderada; < 0.40 → dominante |
| CA3 | Componentes da inércia em [0,1]; inércia = soma ponderada 0.30/0.30/0.20/0.20 |
| CA4 | Dependências faltantes = fração de requires ausentes do DNA (1 − coverage) |
| CA5 | QIV ∈ [0,1] (clamp) |
| CA6 | Determinismo; ranking de barreiras por inércia desc |
| CA7 | Anti-overclaim: sem `superhuman`, `verificad[oa]s?`, `qualis a1`, `superação` |
| CA8 | Documentação do algoritmo (pesos e modelo) |
| CA9 | Previsão de reorganização: alta/moderada/baixa mapeada às faixas |
| CA10 | Candidata sem requires → inércia/documento explícito |
| CA11 | Integração: `analyze(potentiality_report)` consome `Potentiality` (R491) |
| CA12 | Caso sem candidatas → relatório vazio sem erro |

## 5. Entregáveis

- `scanners/inertia_analyzer.py` — `InertiaAssessment`, `InertiaReport`,
  `InertiaVectorAnalyzer`
- `tests/test_r493_inertia_analyzer.py`
- ciclo R493 + commit

## 6. Prontidão

- `pytest tests/test_r493_inertia_analyzer.py` verde; regressões R483-R492
  verdes