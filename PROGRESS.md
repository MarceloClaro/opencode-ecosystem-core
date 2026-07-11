# PROGRESS — Checkpoint de trabalho resumível

> Arquivo vivo (R129). Serve para **retomar o trabalho de onde parou** se
> uma sessão do Claude Code terminar no meio (limite de sessão/tokens do
> plano). Atualize-o e commite a cada passo concluído. Complementa o
> registro formal em `evolution/cycles.json` (histórico) — aqui fica o
> **estado atual e o próximo passo**, não o histórico completo.

## Estado atual

- **Branch:** `main` · última entrega: **R129** (este mecanismo de retomada).
- **Suíte:** verde (última execução completa: 1359 passed, 5 skipped).
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

## Próximos passos (independentes e resumíveis)

Nenhum trabalho em aberto no momento. Candidatos para quando houver pedido:

- [ ] Seletor direto/delegado da apresentação MIRA no CLI (`present` vs
      `present_task`) — hoje o CLI usa a via direta.
- [ ] Gerador automático das "contagens vivas" (testes/ciclos/specs) a
      partir da fonte, encerrando a dívida recorrente de R122/R125/R127.
- [ ] Bloco `openai` no `opencode.json` — pertence à frente **SPEC-108**
      (não commitar por aqui; é do dono daquela frente).

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
