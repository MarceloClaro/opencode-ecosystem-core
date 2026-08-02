# PROGRESS — Checkpoint de trabalho resumível

> Arquivo vivo (R129). Serve para **retomar o trabalho de onde parou** se
> uma sessão terminar no meio. Atualize-o e commite a cada passo concluído.

## Estado atual

- **Branch:** `main` · última entrega: **R373** (validação fim-a-fim com manuscrito real + fixes)
- **R373 (2026-08-02):** validação real (não sintética) dos gates R369-R372 sobre
  manuscrito USP construído a partir de dossiê existente (53 refs, 7 correlações
  reais) — `academic/papers/manuscrito_educacao_armadilha_renda_media_usp.md`.
  Achados e correções:
  - BUG REAL: R369 tinha falso positivo ("primeiro/primeira" bruto disparava em
    "primeiras diferenças", termo econométrico) — corrigido para exigir fraseado
    de prioridade autoral explícito.
  - GAP REAL: R370 exige dados brutos, manuscritos publicados só têm r/p/n — 
    fechado com `pearson_naive_significance()` (t-Student em Python puro,
    validado contra scipy a 1e-15) + `crosscheck_reported_correlation()`
    (ASSIMÉTRICA: só sinaliza p reportado mais forte que o ingênuo, nunca mais
    conservador — evita falso positivo contra correções legítimas de cointegração).
  - R371 e R372 funcionaram corretamente de primeira sobre o caso real.
  - Achado sem correção (fidelidade à fonte): 2/7 correlações do artigo-fonte não
    declaram `n` na Tabela 2 apesar da legenda definir n — documentado como
    recomendação no relatório de validação, não alterado no manuscrito.
  Relatório completo: `validacao_externa/manuscrito_armadilha_renda_media/relatorio_validacao_pipeline.md`.
  50 testes TDD novos; 194 regressão verdes; 2501 testes coletados sem erro.
- **R372 (2026-08-02):** BUG REAL CORRIGIDO em `mci/experiment_designer.py`:
  `"pre_registered": context.get("pre_registered", True)` dava o selo de graça
  sem verificação alguma — confirmado reproduzindo o bug antes de corrigir.
  `mci/preregistration_protocol.py` novo: `register_protocol`/`verify_protocol`
  (comparação textual exata, protege contra HARKing). `pre_registered` agora
  `False` por padrão; só `True` com protocolo registrado E honrado. Gate real
  no R103 (`verify_preregistered_claim`, mesmo padrão de R370/R371). 17 testes
  TDD verdes; 193 testes de regressão verdes; 2473 testes coletados sem erro
  em toda a suíte (checagem rápida de import-time em todo o repo).
  **Com R370+R371+R372, a trinca "estatística severa + validação cruzada +
  contraprovas + multidisciplinar + pré-registro" está completa na camada de
  infraestrutura/gate.** Doctor: 9/12 pass, 3 warn (ambiente: loop_specs vazio,
  scihub-cli ausente, litert-lm daemon parado — nenhum é bug de código).
- **R371 (2026-08-02):** `mci/multidisciplinary_triangulation.py` — segunda metade
  do pedido "estatística severa + cruzar informações multidisciplinares" fechado.
  `triangulated=True` só com >=2 domínios independentes concordantes E zero
  contestadores; contestação de qualquer domínio bloqueia (nunca maioria de
  votos). Design aditivo — não toca EvidenceGraph (R102) nem DataKnowledgeHub
  (R52/R55). Gate real no R103: `verify_multidisciplinary_claim()`, mesmo padrão
  do `verify_statistical_claim` do R370. 16 testes TDD verdes; zero regressão
  (115 testes combinados R102+R103+R370 verdes).
  **Com R370+R371, o pedido do usuário ("estatística severa, validação cruzada,
  contraprovas, cruzar informações multidisciplinares") está coberto no nível
  de infraestrutura de gate — falta ainda: uso real em produção (rodar o
  pipeline R101-R105 fim-a-fim com esses gates ativos num caso real) e o
  pré-registro de protocolo (opção descartada no brainstorming do R370, fica
  como R372+ se o usuário quiser).
- **R370 (2026-08-02):** `mci/rigorous_validation.py` — estatística COMPUTADA de dados
  brutos (não só validação de números já dados): contraprova por permutação
  (centrada pela própria distribuição nula — corrige viés para estatísticas
  assimétricas como Mann-Whitney U), Welch-t + Mann-Whitney + Cohen's d com IC
  bootstrap, k-fold CV genérico (partição exaustiva/disjunta, guarda contra
  denominador ~zero), `convergent_validity_report` (reaproveita
  `validate_statistics()` existente). Gate real no R103:
  `OrchestratorReviewer.verify_statistical_claim()` só verifica claim quando
  convergente. 23 testes TDD verdes; zero regressão (R103: 51 verdes,
  scientific_superhuman: 45 verdes). Bug real pego em TDD e documentado na
  spec: comparar `|observado|` vs `|permutado|` direto assume distribuição
  nula centrada em zero — falso para U de Mann-Whitney.
  Triangulação multidisciplinar (então pendente) foi feita no ciclo R371,
  logo acima.
- **R369 (2026-08-02):** `reasoning/production_scaffolds.py` — ponte entre os motores de
  raciocínio (SPEC-917/ARCHE) e a produção editorial: 8 movimentos científicos auditáveis
  com engine_hints; auditoria de novidade (`UNSUPPORTED_NOVELTY_CLAIM` quando "inédito/
  inovador" não tem citação/comparação na mesma frase); plano literário contratual
  (voz/conflito/símbolos/estranhamento); relatório medido de distintividade (léxico de
  22 clichês pt); `select_scaffold` via episteme da tarefa. 21 testes TDD verdes.
- **R368 (2026-08-02):** cobertura epistêmica do catálogo 32%→**65%** (léxico pt/en em 2
  rodadas curadas; invariante de sinais disjuntos; `catalog_episteme_coverage()`;
  12º check do doctor `episteme_coverage` com números medidos). Higiene SDD: 6 specs
  (R264–R279) apontavam para validações fantasmas → testes de regressão reais criados,
  `test_sdd_tdd` 12/12; 15 dirs `mci_test_state_*` removidos/ignorados.
  **Pendência documentada (frente literária):** falhas R272–R276 (~17) existem também
  no HEAD (verificado com stash do catálogo) — cards `literary-*` fora de contrato
  (ex.: `literary-ethics-trauma-phd` sem termo obrigatório "limites") e relatório R276
  ausente; corrigir na frente literária, não misturar aqui.
- **R364–R367 (2026-08-02):** implementados os três agentes que eram só interface no R359 +
  benchmark medido: TerminologyGraphAgent (`translation/terminology_graph.py`),
  AuthorVoiceGuardian (`translation/author_voice.py`), BackTranslationVerifier
  (`translation/back_translation.py`) — todos fail-closed, com gate humano, agent cards
  com `episteme:` explícita — e benchmark cultural medido
  (`scripts/benchmark_r367_cultural.py`: precisão micro 1.00, recall 0.86 em corpus
  interno de 18 casos; substitui o "98%" não medido do plano). 62 testes novos verdes.
  Pendências honestas: API/white label segue inexistente (só CLI local); validação
  externa do agente cultural continua não feita; opencode.json regenerado mas não
  commitado (mistura pendências de outra frente).
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
