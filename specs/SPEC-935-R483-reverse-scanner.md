# SPEC-935-R483 — Scanner Reverso de Trajetórias Evolutivas

Status: **implementado** (R483)
Data: 2026-09-13
Autor: marceloclaro (orquestrador)
Requer: R482 (paisagem), CrossValidationEngine (R011), NoologicalScanner (R015)

## 1. Contexto e problema

O Core sabe avaliar o presente e priorizar ausências:

- Scanner Noológico (`scanners/noological_scanner.py`): responde **"o que está ausente?"** (indução sobre o presente).
- EpistemicPrioritizer (`scanners/epistemic_prioritizer.py`): responde **"quais ausências valem mais?"** (estima potencial no presente).

Falta a direção **regressiva/dedutiva**: dado um estado futuro desejado `F`, reconstruir os
pré-requisitos estruturais mínimos `R(F)` e o **gap evolutivo** `Δ = R(F) \ A`. Sem isso, todo
planejamento de futuro é intuição ou lista de desejos; com isso, o ecossistema passa de
avaliador do presente a **planejador estrutural do futuro** (grafo de dependências, não opinião).

Referências epistemológicas citadas no design (ver THIRD_PARTY_NOTICES da mesma revisão):

- **feynman-skill** (MIT, Huashu/花叔): o "deletion experiment" e o teste anti-cargo-cult
  inspiram o componente **ritual(g)** — distinguir lacuna genuína de lacuna ritual.
- **feynman** (MIT, Companion, Inc.): agente de pesquisa — executor futuro das trajetórias
  priorizadas (fora de escopo desta revisão).
- **bernstein** (Apache-2.0, sipyourdrink-ltd): orquestração determinística — executor futuro
  do roadmap (fora de escopo). Nenhum código desses repositórios foi copiado.

## 2. Objetivos funcionais

- **OF1** — Calcular o fecho regressivo `R(F)` no grafo de capacidades do `CrossValidationEngine`.
- **OF2** — Derivar o gap evolutivo `Δ = R(F) \ A` (A = capacidades observadas).
- **OF3** — Pontuar o potencial `p(g)` de cada `g ∈ Δ` com componentes
  `cascade`, `centrality`, `novelty`, `ritual`, normalizado em `[0, 1]`.
- **OF4** — Emitir relatório auditável com classificação qualitativa (tiers) e avisos.
- **OF5** — 100% stdlib, hermético (sem rede, sem credenciais, sem código de terceiros).

## 3. Não-objetivos (fora do escopo desta revisão)

- Integração CLI/orquestrador do pipeline `/diagnose` (planejada: R484).
- Mapa multi-rota de trajetórias e priorização por alavancas (planejada: R485).
- Convergência Polimática via `landscape/manifest.json` (planejada: R486).
- Qualquer modificação em `cross_validation_engine.py`, `noological_scanner.py` ou
  `epistemic_prioritizer.py`.

## 4. Modelo formal

Seja `G = (C, D)` o grafo do `CrossValidationEngine` (nós = capacidades, arestas dirigidas com `relation ∈ {requires, enables, co_occurs}`).

Semântica de pré-requisito (mesma do build_graph):

- `requires` — `edge(source=S, target=T)`: S requer T → **T é pré-requisito de S**.
- `enables` — `edge(source=S, target=T)`: S habilita T → **S é pré-requisito de T**.
- `co_occurs` — não participa da regressão.

Fecho regressivo (BFS/DFS com visita única, tolerante a ciclos):

```
prereqs(X) = { T : edge(source=X, target=T, relation="requires") }
           ∪ { S : edge(source=S, target=X, relation="enables") }
R(F) = fecho transitivo de prereqs sobre F, restrito a nós do grafo,
       visitando apenas chaves não observadas (parada em A).
```

A poda em `A` (parar de retroceder quando já se tem a capacidade) evita fecho infinito
e modela "não preciso planejar o que já tenho".

Gap evolutivo:

```
Δ = R(F) \ A      (ordenado lexicograficamente para determinismo)
```

Potencial de cada `g ∈ Δ` (todos os componentes em `[0, 1]`):

```
p(g) = α·cascade_norm(g) + β·centrality_norm(g) + γ·novelty(g) − δ·ritual(g)
α=0.40  β=0.25  γ=0.20  δ=0.15      (default; α+β+γ+δ = 1)
```

- `cascade_norm` — impacto em cascata do `CrossValidationEngine.cascade_impact(scan)` normalizado pelo máximo de Δ (0 se máximo = 0).
- `centrality_norm` — `influence_score` do nó (bottleneck do build_graph) normalizado pelo máximo de Δ.
- `novelty` — `1 − overlap(tokens(capacidade), corpus_terms)`; sem corpus → `1.0` (capacidade não indexada no corpus = máxima novidade; documentado, não oculto).
- `ritual` — fração de **exemplares bem-sucedidos** que NÃO possuem `g` (teste anti-cargo-cult à la feynman-skill); sem exemplares → `0.0` (neutro: sem dados não se pune).

Tiering qualitativo:

```
ritual ≥ 0.5      → "ritual"    (lacuna ritual — provável bambu de aeroporto)
p ≥ 0.70          → "alavanca"  (construir destrava o fecho inteiro)
0.40 ≤ p < 0.70   → "prioritaria"
p < 0.40          → "marginal"
```

## 5. Critérios de aceitação

| ID | Critério | Validação |
|---|---|---|
| CA1 | Fecho regressivo é transitivo (pré-requisitos de pré-requisitos) | test_reverse_closure_transitive_* |
| CA2 | Fecho para em capacidade observada (poda em A) | test_reverse_closure_stops_* |
| CA3 | `F` vazio ⇒ `R(F)` vazio; `F` com chaves fora do grafo ⇒ ignoradas + warning | test_reverse_closure_empty/unknown |
| CA4 | `Δ = R(F) \ A` correto e ordenado | test_evolution_gap_* |
| CA5 | Componentes `ritual`/`novelty` com comportamento determinístico e documentado | test_component_* |
| CA6 | `p(g)` decompõe-se pelos pesos default e permanece em `[0, 1]` | test_potential_* |
| CA7 | Integração real com `CrossValidationEngine.build_graph` em scan sintético | test_scan_integration_* |
| CA8 | Relatório tem campos `target_state, observed_capabilities, reverse_closure, evolution_gap, opportunities, params, warnings`; oportunidades com tier e `possibly_ritual` | test_scan_report_fields |
| CA9 | Anti-overclaim: módulo e relatório sem `superhuman`, `verificado(s)`, `qualis a1`, `superação` | test_report_no_anti_overclaim |
| CA10 | Robustez: formato legado de dimensões (sem `covered/absent`), determinismo entre execuções, sem exemplares | test_legacy_deterministic, test_ritual_default |

## 6. Entregáveis

- `specs/SPEC-935-R483-reverse-scanner.md` (este arquivo)
- `scanners/reverse_scanner.py` — `ReverseScanner`, `ReverseOpportunity`, `ReverseScanReport`
- `tests/test_r483_reverse_scanner.py` — suíte RED/GREEN
- `THIRD_PARTY_NOTICES.md` — registro de bernstein (Apache-2.0), feynman (MIT), feynman-skill (MIT)
- ciclo R483 no `evolution/cycles.json` + reflexão MetaBus

## 7. Verificação de prontidão

- `python3 -m marceloclaro.cli doctor` inalterado (18/20)
- `python3 -m marceloclaro.cli core-check` saudável
- suíte `tests/test_r483_reverse_scanner.py` verde
- regressões R482/R481/R480 verdes
- suíte completa sem novas falhas