---
name: gemini-notebooklm-bridge
description: >
  Ponte entre o Gemini CLI e o Gemini Notebook (ex-Google NotebookLM) via MCP
  + navegador (SPEC-935-R601). Use para operar notebooks do usuário pelo
  Gemini: listar/criar notebooks, adicionar fontes (URL/PDF/texto/Drive),
  consultar chats, exportar. Requer `nlm` no .venv, sessão válida
  (`nlm login --check`) e modelo do Gemini configurado (GEMINI_API_KEY,
  `gemini login` ou Gemma local). NÃO é API oficial — usa APIs internas não
  documentadas via cookies do navegador; pode quebrar sem aviso.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R601
spec: SPEC-935-R601-gemini-notebooklm-bridge.md
---

# Skill: Ponte Gemini CLI ↔ Gemini Notebook (SPEC-935-R601)

## Pré-requisitos

1. `notebooklm-mcp-cli` instalado no .venv (`pip install notebooklm-mcp-cli`).
2. Sessão válida: `.venv/bin/nlm login --check` → `✓ Authentication valid!`.
3. `~/.gemini/settings.json` com `gemini-notebook-mcp` apontando para o caminho
   ABSOLUTO de `.venv/bin/notebooklm-mcp`.
4. Modelo do Gemini pronto (uma das rotas abaixo).

## Fluxo

```bash
# 1. Sanidade
nlm doctor                                # diagnóstico completo (storage/auth/browser)
nlm login --check                         # cookies válidos?

# 2. Operação direta (CLI nlm)
nlm notebook list                         # ver notebooks
nlm source add <notebook> --url "https://..." # adicionar fonte
nlm chats list/get/export <notebook>      # conversas

# 3. Via Gemini (MCP)
gemini -p "liste os notebooks e resuma o mais recente" --skip-trust --approval-mode yolo
```

## Rota do modelo (escolher UMA)

| Rota | Comando |
|---|---|
| API key (free tier) | `export GEMINI_API_KEY="..."` (aistudio.google.com/apikey) |
| OAuth navegador | `gemini login` (abre o browser; confirme na conta Google) |
| Local (offline) | `gemini gemma setup` (baixa LiteRT + modelo; pesado) |

## Atenção

- Pasta untrusted suprime MCP user-level → use `--skip-trust` (sessão) ou
  confie no primeiro uso interativo.
- Após trocar PATH/npx, valide: `gemini mcp list` e handshake `initialize`.
- NUNCA declare resultado como "verificado" sem validação (anti-overclaim R110).