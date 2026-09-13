# SPEC-935-R485 — Mapa de Trajetórias Evolutivas

Status: **implementado** (R485)
Data: 2026-09-13
Requer: R483 (ReverseScanner), R482 (paisagem), CrossValidationEngine

## 1. Contexto

O R483 fornece o fecho regressivo `R(F)` e o gap `Δ`, mas apenas de forma
**conjunta**: não mostra *por quais rotas* cada lacuna pode ser construída,
nem quais capacidades são **alavancas estruturais** (nós que destravam várias
rotas ao mesmo tempo). O mapa de trajetórias resolve isso enumerando
**múltiplos caminhos** no grafo de pré-requisitos e agregando **contagem de
caminhos** por capacidade.

Progressão completa do usuário:
ERRO → AUSÊNCIA → OPORTUNIDADE → **TRAJETÓRIAS** (este módulo) → convergência (R486)

## 2. Objetivos

- **OF1** — Enumerar todas as rotas de construção de cada `g ∈ Δ` até `F`
  (caminhos no grafo de pré-requisitos), com limites de profundidade e
  quantidade (anti-explosão), sem ciclos, determinístico.
- **OF2** — Calcular **lever score** de cada capacidade: fração normalizada
  dos caminhos que passam por ela (betweenness aproximado).
- **OF3** — Produzir ranking de **alavancas estruturais** (nós com maior
  presença em caminhos — construir primeiro destrava múltiplas rotas).
- **OF4** — Enriquecer as oportunidades do R483 com `lever_score` e tier
  combinado (`alavanca estrutural` quando p alto E lever alto).
- **OF5** — 100% stdlib, hermético, sem modificar R483/R482.

## 3. Não-objetivos

- Não calcula caminho ótimo (custo/viabilidade por aresta) — futuro.
- Não lista caminhos infinitos; limites explícitos em `params`.
- Não altera o ReverseScanner (usa sua API pública).

## 4. Modelo formal

Grafo de pré-requisitos com a mesma semântica do R483:

```
prereqs(X) = { T : edge(source=X, target=T, relation="requires") }
           ∪ { S : edge(source=S, target=X, relation="enables") }
```

Um **caminho** é uma sequência `[v1, v2, ..., vk]` com `v1 ∈ Δ`, `vk ∈ F`,
`vi` pré-requisito de `v(i+1)` (v1 construído primeiro). DFS determinística,
sem revisitá-lo dentro de um caminho, com `max_depth` (default 6) e
`max_paths` por par (start, target) (default 50).

Lever count e score:

```
count(c) = número de caminhos (de todos os pares g∈Δ × f∈F) que contêm c
lever_score(c) = count(c) / max_count    (0 se max_count = 0)
```

Oportunidade enriquecida (para cada g ∈ Δ):

```
p_original = ReverseScanner.potential(g)
combined(p, lever) = 0.70·p + 0.30·lever          (default)
tier_struct = "alavanca estrutural" se combined ≥ 0.7 e lever ≥ 0.6
            | "alavanca"       se combined ≥ 0.7
            | "prioritaria"    se combined ≥ 0.4
            | "marginal"       caso contrário
            (ritual herdado do R483 mantém precedência ao rebaixar)
```

## 5. Critérios de aceitação

| ID | Critério |
|---|---|
| CA1 | Caminhos lineares corretos (A→B→C) e múltiplas rotas enumeradas |
| CA2 | Limites anti-explosão (`max_depth`, `max_paths`) respeitados e expostos em `params` |
| CA3 | Sem caminho (grafo desconexo) → lista vazia, sem erro |
| CA4 | Determinismo: duas execuções produzem o mesmo mapa (ordem estável) |
| CA5 | Lever score normalizado em [0,1]; top lever correto em grafo controlado |
| CA6 | Integração com ReverseScanner em scan sintético: Δ vira entradas dos caminhos; Probabilístico é alavanca |
| CA7 | Oportunidades enriquecidas com `lever_score`, `potential` e tier combinado; `ritual` herdado |
| CA8 | Anti-overclaim: módulo e relatório sem `superhuman`, `verificado(s)`, `qualis a1`, `superação` |
| CA9 | Robustez: sem alvos, domínio vazio, formato legado de dimensões |
| CA10 | Algoritmo documentado (fórmulas no docstring) |

## 6. Entregáveis

- `scanners/trajectory_mapper.py` — `TrajectoryMapper`, `Lever`, `TrajectoryOpportunity`, `TrajectoryMapReport`
- `tests/test_r485_trajectory_mapper.py`
- `specs/SPEC-935-R485-trajectory-mapper.md` (este arquivo)
- ciclo R485 + reflexão + commit

## 7. Prontidão

- `pytest tests/test_r485_trajectory_mapper.py` verde; regressões R483/R484 verdes
- suíte completa sem novas falhas (executada no fechamento da sequência R484-R486)