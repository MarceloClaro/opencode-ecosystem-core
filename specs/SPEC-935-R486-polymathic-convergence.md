# SPEC-935-R486 — Convergência Polimática

Status: **implementado** (R486)
Data: 2026-09-13
Requer: R482 (landscape/manifest.json), R483 (ReverseScanner), R485 (TrajectoryMapper)

## 1. Contexto

A progressão completa do usuário:
ERRO → AUSÊNCIA (R011/R015) → OPORTUNIDADE (R020) → REVERSO (R483) → TRAJETÓRIAS (R485)
→ **CONVERGÊNCIA POLIMÁTICA** (este R486).

O R485 entrega as rotas e alavancas para construir cada `g ∈ Δ`. O R486 pergunta:
**"quem, fora do domínio atual, já resolveu parte disso?"** — cruzando cada lacuna
com a paisagem externa curada no R482 (`landscape/manifest.json`, 20 agentes MIT
auto-contidos), por sobreposição léxica ponderada (tokens + campos).

## 2. Objetivos

- **OF1** — Para cada `g ∈ Δ`, buscar no manifest externo os agentes cujo
  `title|industry|framework|dependencies|swift` sobrepõem tokens da lacuna.
- **OF2** — Score de afinidade em `[0,1]` por ponderação de campos
  (title/industry peso 2; framework 1.5; dependencies/swift 1.0).
- **OF3** — `top_k` por lacuna (default 3); relatório por lacuna e plano.
- **OF4** — Fallback: manifesto ausente → warning e relatório vazio (fail-soft).
- **OF5** — 100% stdlib, hermético, determinístico; não modifica R482/R483/R485.

## 3. Não-objetivos

- Não baixa nem executa código externo (referência de metadados apenas). Uso:
  consultar o `reference_url` do agente para importar/explicar o padrão.
- Não adiciona integração de runtime (futuro — exemplo: adaptador de agente).
- Não cruza com o catálogo Core (196 cards) nesta revisão.

## 4. Modelo formal

```
tokens(t)  = {palavras alfanuméricas de t (lowercase)}
score(a, g) = Σ_campo peso(campo) · I(∃ tok ∈ tokens(g): tok ∈ campo_do_agente)
              ─────────────────────────────────────────────────────────
              Σ_campo peso(campo)
```

Campos e pesos: title=2.0, industry=2.0, framework=1.5, dependencies=1.0, swift=1.0.
Overlap_terms = tokens de g presentes em pelo menos um campo do agente.
Por lacuna g, top_k agentes ordenados por score desc (desempate: agent_id asc).

## 5. Critérios de aceitação

| ID | Critério |
|---|---|
| CA1 | Match por sobreposição de tokens (fixture controlada) encontra o agente correto |
| CA2 | Score normalizado em [0,1]; peso de campos influencia (title pesa mais que swift) |
| CA3 | `top_k` respeitado; desempate determinístico (agent_id asc) |
| CA4 | Integração com ReverseScanner: convergências por cada g ∈ Δ |
| CA5 | Manifest real do R482 carrega (20 agentes) e é cruzado sem erro |
| CA6 | Manifest ausente/inexistente → warning + relatório vazio (fail-soft) |
| CA7 | Determinismo entre execuções |
| CA8 | Anti-overclaim: módulo e relatório sem `superhuman`, `verificado(s)`, `qualis a1`, `superação` |
| CA9 | Sem alvos → relatório vazio sem erro |
| CA10 | Algoritmo documentado no docstring |

## 6. Entregáveis

- `scanners/polymathic_convergence.py` — `PolymathicConvergence`, `PolymathicMatch`, `ConvergenceReport`
- `tests/test_r486_polymathic_convergence.py`
- spec (este arquivo); ciclo R486 + reflexão + commit

## 7. Prontidão

- `pytest tests/test_r486_polymathic_convergence.py` verde; regressões R483-R485 verdes
- suíte completa sem novas falhas