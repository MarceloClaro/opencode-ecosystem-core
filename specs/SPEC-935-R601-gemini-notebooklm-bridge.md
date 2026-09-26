# SPEC-935-R601 — Ponte Gemini ↔ Gemini Notebook (ex-NotebookLM) via MCP + navegador

**Ronda:** R601
**Status:** piloto — elo MCP conectado; modelo pendente (GEMINI_API_KEY | login | Gemma local)
**Data:** 2026-09-25
**Autor:** marceloclaro (orquestrador central)
**Padrão:** Integração externa bridge (Gemini CLI + notebooklm-mcp + navegador)

## Objetivo

Permitir que o Gemini CLI aja como agente do **Gemini Notebook** (ex-Google
NotebookLM): criar notebooks, adicionar fontes (URL/PDF/texto/Drive), consultar
chats e exportar, usando **cookies da sessão do navegador** do usuário.

## Arquitetura verificada (2026-09-25)

```
gemini -p "tarefa" --skip-trust --approval-mode yolo
   │
   ▼  cliente MCP (Gemini CLI 0.61.0)
~/.gemini/settings.json → mcpServers.gemini-notebook-mcp (stdio, trust:true)
   │  command: /home/.../.venv/bin/notebooklm-mcp (ABSOLUTO — o binário não
   │  está no PATH global; era "notebooklm-mcp" e FALHARIA sem correção)
   ▼
notebooklm-mcp v4.0.5 (pacote notebooklm-mcp-cli, MIT, jacob-bd)
   │  usa APIs INTERNAS (não documentadas) do Gemini Notebook com cookies
   ▼
~/.notebooklm-mcp-cli/profiles/default/auth.json (43 cookies, CSRF ok)
   │  conta marceloclaro@gmail.com | 222 notebooks
   ▼
notebooklm.google.com (browser session do usuário; WSL2 + Chrome Windows)
```

## Fatos verificados (anti-overclaim)

- `nlm login --check` → `✓ Authentication valid!` (222 notebooks; conta pessoal).
- `nlm doctor` → cookies presentes, CSRF sim, Chrome (WSL2) encontrado.
- `nlm setup add gemini` → adicionou server ao Gemini CLI (com `trust: true`).
- `gemini mcp list` → server `gemini-notebook-mcp (stdio)` configurado;
  **desabilitado por padrão em pasta untrusted** → usar `--skip-trust` por
  sessão (ou confiar interativamente no primeiro uso).
- Handshake MCP real: `initialize` → `serverInfo: gemini-notebook-mcp v4.0.5`,
  tools disponíveis (source_add, notebook_*, chat_*, export…).
- Limitações conhecidas (do README do projeto): APIs internas não documentadas
  (podem mudar sem aviso); cookies expiram → `nlm login` de novo; contas
  Enterprise = experimental; autenticação via navegador (Auto Mode) ou File Mode.

## Critérios de aceitação

1. `nlm` instalado no .venv do Core (>= 0.11.6) e `nlm login --check` válido.
2. `~/.gemini/settings.json` aponta para caminho ABSOLUTO do `notebooklm-mcp`.
3. `gemini mcp list` mostra o server; handshake `initialize` responde v4.0.5+.
4. Modelo do Gemini CLI configurado por UMA das rotas: (a) `GEMINI_API_KEY`,
   (b) `gemini login` (OAuth navegador), (c) `gemini gemma setup` (local).
5. Prova funcional: 1 notebook criado + 1 fonte adicionada via `nlm` (CLI) e/ou
   via Gemini (`gemini -p` com ferramenta MCP).
6. Ciclo R601 registrado no EvolutionRegistry em formato canônico (timestamp +
   objective) — sem perda silenciosa (lição R581/R110).

## Não escopo / limites

- Não é API oficial do NotebookLM (não existe pública) — é bridge sobre APIs
  não documentadas com cookies; pode quebrar sem aviso.
- Segurança: o server requer `trust: true` no Gemini (executa comandos/arquivos
  sem prompts) — decisão explícita do operador, documentada aqui.
- A etapa de modelo (API key/login/Gemma) é do operador (envolve conta Google).