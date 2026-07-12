# Evo-44 — R142: Honest Evaluation Engine

## Contexto

A disciplina antioverclaim já existia **implícita no julgamento**
(`classify_metacognitive_tier`, `CORRIGENDUM.md`), mas não como função
reutilizável. A prática recente reforçou a lição central: é fácil ler a
saída de um *scanner* ("100% dos eixos", "M4") como se fosse uma **nota de
qualidade** — exatamente o erro que a política proíbe.

## O que mudou

- **`evaluation/honest_reviewer.py`** (novo) — codifica a política:
  - `classify_claim` — cobertura / qualidade / mista / neutra.
  - `detect_inflation` — best-seller, obra-prima, Qualis A1, verified,
    superhuman, 9.5–10/10, 100%, perfeito. Termos que exigem validação
    externa somem com `external_validation=True`; perfeição absoluta
    permanece suspeita.
  - `honest_score_band` — faixa piso–teto; teto limitado a 8.5/10 sem
    validação externa (cobertura não eleva o teto de qualidade).
  - `review` — pipeline completo, **reusa** `classify_metacognitive_tier`.
- **`agents/catalog/honest-critic-agent.md`** (novo) — agente-crítico
  antioverclaim, chaveado por slug no `opencode.json` (174 agentes).
- **`tests/test_r142_honest_reviewer.py`** (novo, TDD) — 16 casos, RED→GREEN.
- **`specs/SPEC-935-R142.md`** (novo).

## Princípio central

> **Cobertura ≠ qualidade.** Métrica de processo não é veredito de mérito.
> Nota de topo exige validação externa.

## Achado colateral (registrado, não escondido)

Ao regenerar o `opencode.json`, descobri que outra frente (WIP **não
commitado**) havia revertido, na árvore de trabalho, o fix do R137 em
`integrations/opencode_cli.py` (voltou a chavear por nome de exibição) e a
extração de descrição em `marceloclaro/catalog_loader.py` (75 descrições
viravam `<!--`), deixando `test_r137` vermelho. Preservei essas mudanças via
`git stash` isolado (não-destrutivo) e regenerei o `opencode.json` contra as
versões HEAD dos geradores — commit aditivo e reprodutível. A reconciliação
dessa frente SPEC-108 fica como pendência dela, registrada no `PROGRESS.md`.

Também restaurei `evolution/cycles.json` (outra frente o havia sobrescrito
para 3 ciclos do projeto Molambudos via `EvolutionRegistry.save()`,
perdendo R47–R141); recuperado do HEAD antes de anexar o R142 → 100 ciclos.
