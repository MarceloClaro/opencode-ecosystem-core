# PROGRESS — Checkpoint de trabalho resumível

> Arquivo vivo (R129). Serve para **retomar o trabalho de onde parou** se
> uma sessão terminar no meio. Atualize-o e commite a cada passo concluído.

## Estado atual

- **Branch:** `main` · última entrega: **R363** (Camada Epistêmica de Roteamento)
- **R363 (2026-08-02):** SPEC-935-R363 verified; `transformer/episteme.py` (6 regimes,
  inferência determinística), peso brando ±10% no `SkillHandbook.match` (fail-open),
  frontmatter opcional `episteme:` no catalog_loader; 27 testes TDD verdes.
  Suíte completa: 2200 pass / 58 falhas **pré-existentes de outras frentes**
  (literárias R272-R276, sépia R351, SPEC-R264 no test_sdd_tdd) — ver §6 da spec.
- **Working tree:** ⚠️ ainda há muito trabalho pendente de outras frentes
  (agents/catalog/*.md, Molambudos, etc.) — não misturar em commits do R363.
- **Trabalho avulso (sem ciclo):** capa trilíngue Molambudos corrigida
  (PT/EN/ZH recompostos em fonte vetorial sobre a arte, 4x upscale) —
  entregue em `~/Downloads/Molambudos_capa_trilingue_4x_TEXTO_CORRIGIDO.png`;
  script reprodutível no scratchpad da sessão (`recompose.py`).
- **Últimos commits (6):**

| Commit | Descrição |
|---|---|
| `d6fd391` | .gitignore: padrão *:Zone.Identifier |
| `6c5c39d` | .gitignore: scripts/cloud/ (pendente revisão) |
| `ee12dfa` | tests: ciclos R51-R53, R143-R145 |
| `4e1602d` | .gitignore + deploy/, publishing/templates/, geradores |
| `f0f0410` | **R229**: Catálogo, CLI, opencode.json, Academic Pipeline |
| `456821f` | **R223-R227**: Core Infra — Scanners, MCP, Trust, Transformer |
| `3938216` | **R210-R214**: LiteRT-LM supervisor + provider + plugin TS |
| `19c697e` | **R220-R222**: LLM Reduction Layer — engines, agent cards |
| `64544e1` | **R228**: Colibri + OLMoE — runtime MoE on-device |

## Ciclos completos (R47 → R229)

| Ciclo | O quê | Score |
|---|---|---|
| **R228** | Colibri + OLMoE: bridge, MCP, provider, doctor, agente | 0.95 |
| **R229** | Catálogo 187 agentes, CLI, opencode.json, Academic Pipeline | — |
| **R223-R227** | Core Infra: scanners, MCP, trust, transformer, observabilidade | — |
| **R220-R222** | LLM Reduction, DataKnowledgeHub, Observabilidade (3 gaps) | 0.94 |
| **R210-R214** | LiteRT-LM supervisor, provider, plugin TS, MCP reconciliation | 0.88 |
| **R208** | Médico Virtual Supremo + MetaBus + Scanner CLI | — |
| **R143** | Reconciliação de overlay stale | — |
| **R142** | Honest Evaluation Engine antioverclaim | — |
| **R141** | OCR-Vision para documentos antigos (SPEC-1001) | — |
| **R139** | pdf2latex multi-engine (SPEC-1000) | — |
| **R138** | OpenCode Go + Zen + Model Router | — |
| **R129** | Fluxo resumível (checkpoints) | — |
| **R128** | Encanamento seguro de chaves LLM (OpenAI + Ollama) | — |
| **R127** | Documentação minuciosa da arquitetura | — |
| **R126** | Agente-executor MIRA delegável | — |
| **R125** | MIRA como cidadão de primeira classe | — |
| **R124** | Capa/contracapa TikZ de livros | — |
| **R123** | Pipeline MIRA de apresentações | — |
| **R120** | CLI de pesquisa + fallback Sci-Hub | — |
| **R117** | Mapa 3D interativo da arquitetura | — |
| **R116** | Instalação multiplataforma + manual/helpdesk | — |
| **R53** | Nano-Orquestração LiteRT-LM (500 laudas) | 10.0 |
| **R52** | LiteRT-LM Skill + Provider OpenAI-compatível | — |
| **R51** | Jinja2 Templates engine | — |
| **R50** | DataKnowledgeHub | — |
| **R49** | GameTheoryLocal | — |
| **R48** | LLM Reduction Layer | — |

## Saúde do ecossistema

```json
{
  "checks_passed": 8,
  "checks_warned": 3,
  "checks_failed": 0,
  "warnings": [
    "CLI externa faltando: scihub-cli (pip install scihub-cli)",
    "LiteRT-LM daemon sem readiness (cold-start)",
    "Pendente revisão: scripts/cloud/ (324 scripts externos)"
  ],
  "agent_count": 187,
  "last_suite": "pendente de execução"
}
```

## Pendências conhecidas

1. **scripts/cloud/** — 324 scripts cloud externos. Pendente revisão de licença antes de versionar.
2. **LiteRT-LM daemon** — sem readiness (warm start pendente). Não afeta o funcionamento do ecossistema (fallback para Ollama + OpenAI).
3. **Colibri/OLMoE** — bridge e MCP implementados. Runtime C nativo precisa ser compilado (`make -C colibri/c olmoe`). Não versionado como submodule (embedded git repo).
4. **PROGRESS.md** — manter atualizado conforme novos ciclos.

## Como retomar

1. `git log --oneline -5` — ver onde parou
2. `git status --short` — confirmar working tree limpa
3. `python3 -m marceloclaro.cli doctor` — saúde do ecossistema
4. `python3 -m pytest tests/ -q` — suíte de testes
5. Ler as pendências acima e seguir o próximo item

## Disciplina de checkpoint

Trabalho longo é quebrado em **passos pequenos, cada um commitável e verificável**.
Se a sessão acabar, a próxima retoma sem re-derivar contexto — a perda máxima é o passo em andamento, não o trabalho inteiro.
