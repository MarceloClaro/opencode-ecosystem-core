# PROGRESS — Checkpoint de trabalho resumível

> Arquivo vivo (R129). Serve para **retomar o trabalho de onde parou** se
> uma sessão do Claude Code terminar no meio (limite de sessão/tokens do
> plano). Atualize-o e commite a cada passo concluído. Complementa o
> registro formal em `evolution/cycles.json` (histórico) — aqui fica o
> **estado atual e o próximo passo**, não o histórico completo.

## Estado atual

- **Branch:** `main` · última entrega: **R142** (Honest Evaluation Engine —
  disciplina antioverclaim como capacidade testável; `evaluation/honest_reviewer.py`).
- **Suíte:** verde no estado do commit R142 — **1427 passed, 11 skipped**,
  validado em worktree isolado sobre HEAD (baseline HEAD = 1411 passed, 0 falhas).
- **Todas as frentes abertas foram fechadas e versionadas** (R137–R142).

### ⚠️ ATENÇÃO — WIP não commitado de outras frentes na árvore de trabalho
Ao entregar o R142 descobri que a árvore de trabalho tem mudanças **não
commitadas** de outra frente (SPEC-108, WIP) que **regridem testes já
commitados**:
- `integrations/opencode_cli.py` — reverteu o fix do slug-keying (R137) e
  removeu o bloco `provider`/comandos → `test_r137` fica vermelho e o
  `opencode.json` regenera com chaves por nome de exibição.
- `marceloclaro/catalog_loader.py` — removeu `_strip_leading_html_comment`
  e a preferência por `description:` → 75 descrições viram `<!--`.
- Com esse WIP restaurado, a suíte na árvore principal dá **~90 falhas**
  (test_r131/r137/r125/etc.). **NENHUMA é do R142** — o baseline HEAD e o
  estado do commit R142 são verdes. Essas falhas são pendência da frente
  SPEC-108 reconciliar. **Não commitei esses dois arquivos.**
- `evolution/cycles.json` estava **corrompido** na árvore (outra frente o
  sobrescreveu para 3 ciclos Molambudos via `EvolutionRegistry.save()`,
  perdendo R47–R141). **Restaurado do HEAD** antes de anexar o R142 → 100 ciclos.

### R142 — Honest Evaluation Engine (entregue)
- `evaluation/honest_reviewer.py` + `evaluation/__init__.py`: `classify_claim`,
  `detect_inflation`, `honest_score_band`, `review` (reusa
  `classify_metacognitive_tier`). Princípio: **cobertura ≠ qualidade**; nota
  de topo exige validação externa (teto interno 8.5/10).
- `agents/catalog/honest-critic-agent.md` (slug no `opencode.json`, 174 agentes).
- `tests/test_r142_honest_reviewer.py` (16 casos, TDD RED→GREEN).
- `specs/SPEC-935-R142.md`, `evolution/evo-44-r142-*.md`.
- **Ciclos recentes concluídos e commitados:**
  - R123 — Pipeline MIRA de apresentações (`illustrations/mira_deck.py`).
  - R124 — Capa/contracapa TikZ (`publishing/cover_designer.py`) + refino.
  - R125 — MIRA no CLI (`apresentacao`/menu `[10]`) + docs.
  - R126 — Agente-executor `mira-presenter` delegável no Blackboard.
  - R127 — Documentação minuciosa (legendas + processos, dupla-registro).
  - R128 — Encanamento seguro de chaves LLM: `.env` (gitignored),
    `env_loader.py`, check no `doctor`; Ollama `llama3.2` + OpenAI ativos.
- **Configuração de ambiente (local, NÃO versionada):** `.env` com
  `OPENAI_API_KEY` (600, gitignored) + `~/.bashrc` carregando o `.env`;
  Ollama local funcional (`llama3.2`, `nomic-embed-text`).

## ✅ CONCLUÍDO: frentes abertas fechadas e versionadas (R137–R140)

Objetivo do usuário: avaliar cada frente, fechar e versionar, refinar.

**Resumo do fechamento (uma frente por commit, suíte verde a cada passo):**
- **R137** — Frente cloud: gerador `opencode.json` reconciliado (slug),
  skip guards, `scripts/cloud/` gitignored, bug de perda de dados corrigido.
- **R138** — SPEC-108 (OpenCode Go/Zen + ModelRouter): providers/comandos.
- **R139** — SPEC-1000 (pdf2latex multi-engine): 15 testes de aceitação.
- **R140** — Molambudos + conteúdo de usuário EXCLUÍDOS via `.gitignore`
  (decisão do usuário: "só o código do ecossistema"; o trabalho Molambudos
  permanece registrado no ledger via R130–R134, mas o livro/PDFs/pesquisa
  ficam fora do ecosystem-core).

**Dívida assumida (documentada, não escondida):**
- Numeração de ciclos inconsistente: R130–R134 = Molambudos, R135–R136 =
  cloud; colisão do nome `SPEC-935-R130.md`; `cycle: R108` no frontmatter da
  SPEC-108 colide com o R108 do ledger. Não reescritos retroativamente.
- Auditoria de licença dos 324 scripts em `scripts/cloud/` pendente.
- Cobertura do pdf2latex é de contrato/CLI, não E2E de conversão real.

### Histórico da avaliação (abaixo) — mantido para rastreabilidade

### Frente A — Integração Cloud — ✅ VERSIONADA (R137)
- Fechada pelo ciclo **R137**: gerador `opencode.json` reconciliado
  (chaveamento por slug, reprodutível), skip guards nos testes cloud,
  `scripts/cloud/` gitignored, bug de perda de dados do `cycles.json`
  corrigido, fontes cloud commitados. Suíte 1390 passed.
- **Dívida assumida:** numeração inconsistente (R130–R134 Molambudos vs
  R135–R136 cloud), colisão do nome `SPEC-935-R130.md`, auditoria de
  licença dos 324 scripts externos pendente.

### Frente A (histórico da reavaliação) — Integração Cloud (R130–R136)
- Estado: 25 testes cloud passam (test_r130 + test_r131); 173 agentes no
  opencode.json, 169 no catálogo — batem com o relatório.
- **BUG ENCONTRADO E CORRIGIDO:** o trabalho cloud reescreveu
  `cycles.json` e apagou os campos `conclusion`/`results` de R81–R84
  (bug do `EvolutionRegistry.save()` que o CLAUDE.md alerta). Restaurado:
  cycles.json = HEAD (R47–R129 intactos) + R130–R136; diff 100% aditivo.
- **Alegação NÃO confirmada:** "56/56 skills Apache 2.0" — 0 arquivos
  LICENSE em scripts/cloud/. Rever antes de afirmar.
- Arquivos: academic/maswos.py, academic/__init__.py,
  integrations/antigravity/antigravity-bridge.ts,
  agents/catalog/cloud-*.md (8) + skills-cloud-antigravity.md,
  scripts/cloud/ (324), tests/test_r130*, tests/test_r131*,
  specs/SPEC-935-R130.md, opencode.json (parte cloud).

### Frente B — SPEC-108 (OpenCode go/zen) — a avaliar
- integrations/opencode_cli.py, model_router.py, opencode_go.py,
  opencode_zen.py, agents/catalog/opencode-{go,zen}-agent.md,
  specs/SPEC-108-*.md, tests/test_opencode_go_zen.py, opencode.json (parte
  providers). Tem teste. Compartilha opencode.json com a frente cloud.

### Frente C — SPEC-1000 (pdf2latex) — a avaliar
- pdf2latex/* (engines/, renderers/, engine_registry.py, pandoc-templates/),
  specs/SPEC-1000, templates/abntex2/*.bst. **SEM TESTES** — precisa de
  testes TDD antes de versionar (disciplina do projeto).

### NÃO COMMITAR (lixo/artefatos/nao-relacionado)
`PROJETO 1/`, `REVISAO_MOLAMBUDOS.md`, `artigos_dl_odontologia.json`,
`livro-odontologia-ia/`, `pesquisa/`, `projetos/`, PDFs em `templates/**`,
`integrations/.evolve/*` (estado/log de runtime), `.env` (segredo).

### DESCOBERTA (reavaliação): numeração inconsistente + 4ª frente
- Ciclos R130–R134 são **Molambudos** (livro de ficção), NÃO cloud.
- Cloud é só **R135–R136** (+ arquivo `SPEC-935-R130.md`, colisão de nome).
- R131–R136 **sem spec formal nem nota evo** (lacuna de disciplina).
- `scripts/cloud/` = **324 arquivos externos não revisados**; alegação
  "56/56 Apache 2.0" NÃO confirmada (0 LICENSE). Não commitar sem revisão.

### Estado seguro atual
- Suíte: **1387 passed, 5 skipped** — zero regressões reais confirmadas.
- `cycles.json` **corrigido no working tree** (R81–R84 restaurados; aditivo).
  Ainda NÃO commitado (ledger à frente dos artefatos das frentes).

### Ordem de execução (aguardando decisão do usuário sobre os itens de risco)
1. [x] Suíte verde + bug de dados do cycles.json corrigido.
2. [ ] DECISÃO do usuário: commitar os 324 scripts cloud externos? revisar antes?
3. [ ] Molambudos (R130–R134): frente separada — versionar os artefatos do livro?
4. [ ] SPEC-108 (código go/zen) — avaliar e commitar.
5. [ ] SPEC-1000 (pdf2latex) — escrever testes TDD antes de versionar.

## Como retomar

1. `git log --oneline -5` e `git status --short` — ver onde parou e se há
   trabalho não commitado.
2. `python3 -m marceloclaro.cli doctor` — confirmar saúde (specs, evolução,
   CLIs externas, provedores LLM).
3. `python3 -m pytest tests/ -q` — confirmar suíte verde antes de seguir.
4. Ler a `## Próximos passos` acima e retomar o primeiro item pendente,
   seguindo a disciplina SDD/TDD (spec → testes → implementação → ciclo →
   commit escopado).

## Disciplina de checkpoint (por que isto existe)

Trabalho longo é quebrado em **passos pequenos, cada um commitável e
verificável**. Tarefas demoradas (suíte completa, downloads) rodam em
**background**; o estado é persistido em commits + neste arquivo. Assim,
se a sessão acabar, a próxima retoma sem re-derivar contexto — a perda
máxima é o passo em andamento, não o trabalho inteiro.

## Frentes paralelas — NÃO misturar nos commits

`opencode.json`, `integrations/opencode_cli.py`, `integrations/model_router.py`,
`integrations/opencode_go.py`, `integrations/opencode_zen.py` (SPEC-108) e a
árvore `pdf2latex/*` (SPEC-1000) estão em andamento por outras frentes —
não commitar junto de ciclos não relacionados. O `.env` **nunca** é
versionado (segredo).
