---
id: gemini-notebooklm-bridge
name: gemini-notebooklm-bridge
type: integration
round: R601
spec: SPEC-935-R601-gemini-notebooklm-bridge.md
trust: 0.8
---

# gemini-notebooklm-bridge — Ponte Gemini CLI ↔ Gemini Notebook (ex-NotebookLM)

Habilita o Gemini CLI a operar o Gemini Notebook (notebooklm.google.com) como
agente: notebooks, fontes (URL/PDF/texto/Drive), chats, export — usando cookies
da sessão do navegador (APIs internas, NÃO oficiais).

## Estado (piloto)

- `nlm` instalado no .venv; auth validada (`nlm login --check` → 222 notebooks).
- MCP do Gemini configurado em `~/.gemini/settings.json` (comando absoluto).
- Handshake MCP OK: `gemini-notebook-mcp v4.0.5`.
- Faltante (operador): modelo do Gemini — API key, `gemini login` ou Gemma local.

## Operação

```bash
nlm login --check                       # validar sessão (cookies)
nlm notebook list                       # notebooks disponíveis
nlm source add <notebook> --url "https://..."   # adicionar fonte
gemini -p "resuma o notebook X" --skip-trust --approval-mode yolo   # via MCP
```

## Limites

- APIs internas não documentadas (podem quebrar); cookies expiram.
- `trust: true` concedido ao server (imperativo do Gemini CLI).
- Não substitui API oficial (inexistente); automação sujeita a termos/uso razoável.