---
spec_id: SPEC-935-R394
title: Auditoria real do OpenCode CLI — 2 bugs reais corrigidos, 2 limitações operacionais documentadas
component: scanners/pipeline.py, integrations/opencode_cli.py
status: verified
test_file: tests/test_r394_opencode_cli_commands_real_execution.py
---

# SPEC-935-R394 — Auditoria Real do OpenCode CLI

**Data:** 2026-08-03
**Motivação:** o usuário pediu para revisar o OpenCode CLI a fundo, no
mesmo espírito da auditoria já feita para o Antigravity CLI (R393) —
testando o binário real, não só relendo código.

## 1. Testado e confirmado funcional

- `opencode agent list`: carrega **216 agentes reais** (209 do catálogo +
  built-ins), incluindo os cartões deste ecossistema com suas permissões
  corretas.
- `opencode mcp list`: **6/6 MCP servers conectam** de verdade
  (`litert-lm`, `metacognitive-interconnect`, `antigravity-bridge`,
  `pypi-search`, `colibri-mcp`, `scanners-mcp`).
- `opencode providers list`: 5 credenciais reais configuradas (OpenCode
  Go, GitHub Copilot, OpenAI, OpenCode Zen, Anthropic).
- `opencode models`: lista modelos reais válidos (confirma, por exemplo,
  que `opencode/deepseek-v4-pro`, usado nos cartões `kdp-*-phd` do R391,
  é um identificador real).
- `opencode run --agent X --model opencode/claude-sonnet-5 "..."`:
  pipeline de invocação funciona ponta a ponta — retornou um erro real e
  específico (`Insufficient balance`), não um travamento nem uma exceção
  Python. Prova que a integração é genuína até a fronteira da chamada de
  API; o bloqueio é de saldo da conta, não de código.

## 2. Bug real #1 — `/diagnose` sempre reportava um NameError disfarçado

`scanners/pipeline.py::DiagnosticPipeline` usa `ReversaScanner` (anotação
de tipo + instanciação) sem importá-lo — mesma classe de bug do
`EpistemicPrioritizer` já corrigida no R391. Toda execução de
`diagnostic_pipeline.run(...)` — inclusive o comando real `/diagnose`
gerado em `opencode.json` — produzia
`report["reversa"] = {"error": "name 'ReversaScanner' is not defined"}`
silenciosamente, sem lançar exceção visível ao chamador.

**Correção:** `from scanners.reversa_scanner import ReversaScanner`
adicionado aos imports de `scanners/pipeline.py`.

## 3. Bug real #2 — `/pypi` sem argumento sempre retornava zero resultados

O template do comando `/pypi` em `integrations/opencode_cli.py` chamava
`search('*', limit=5)` como fallback para `$ARGUMENTS` vazio. A função
`skills/tooling/pypi_search.py::search()` não trata `'*'` como coringa —
é busca literal por substring/prefixo contra o índice local — então
`/pypi` sem argumento (a invocação mais simples e comum) sempre
retornava `"0 encontrados, 0 exibidos"`, sem erro nem aviso.

**Correção:** o fallback de argumento vazio agora imprime uma mensagem
de uso clara (`"Uso: /pypi <termo de busca> [--json] ..."`) em vez de
executar uma busca que sabidamente não retorna nada. Não foi
implementado um modo "pacotes populares/tendência" — funcionalidade que
não existia e que o usuário não pediu; a correção fica estritamente no
que estava quebrado.

## 4. Limitações operacionais reais, documentadas (não bugs de código)

1. **Modelo padrão do `opencode.json` aponta para o daemon LiteRT-LM
   offline** (`litert-lm/litert-community/gemma-4-E2B-it-litert-lm`) —
   já documentado como pendência conhecida (`doctor`, `PROGRESS.md`,
   `state.json` do circuit breaker com 37 falhas reais). Consequência
   concreta confirmada nesta auditoria: **qualquer `opencode run` sem
   `--model` explícito trava** neste ambiente, porque tenta alcançar um
   daemon que não está rodando. Fora do escopo deste ciclo trocar o
   modelo padrão do projeto — decisão editorial, não bug.
2. **Subagentes do catálogo não são invocáveis diretamente via
   `opencode run --agent <nome>`**: `opencode run --agent contextscout
   ...` imprime um aviso (`"agent 'contextscout' is a subagent, not a
   primary agent. Falling back to default agent"`) e usa o agente
   primário `build` em vez do subagente pedido. Isso é comportamento do
   binário real do OpenCode CLI (não é algo que este repositório
   controla) — significa que, na prática, os 205+ agentes especializados
   do catálogo só são alcançáveis através do orquestrador `marceloclaro`
   delegando para eles internamente, não por invocação direta via CLI
   externa com `--agent`.

## 5. Verificação

- Novo teste genérico `tests/test_r394_opencode_cli_commands_real_execution.py`:
  executa o comando shell **real** de cada uma das 9 entradas de
  `build_config()["command"]` (não só importa o módulo Python) e falha
  se aparecer `Traceback`/`NameError`/`ImportError`/`ModuleNotFoundError`/
  `AttributeError` na saída combinada, ou se o código de saída não for 0.
  Esse teste teria pego os dois bugs reais desta auditoria automaticamente.
- 2 testes de regressão direta para os bugs específicos encontrados.
- `tests/test_deep_diagnose.py::test_reversa_scanner_runs_without_nameerror`
  novo, mesmo padrão do `test_prioritizer` já existente.
- `opencode.json` regenerado após a correção do template `/pypi`.
- Suíte completa: **2693 aprovados (+11), 0 falhas, 56 pulados** — zero
  regressão.

## 6. Critérios de aceitação

1. `/diagnose` não reporta mais `NameError` disfarçado na seção
   `reversa`.
2. `/pypi` sem argumento imprime instrução de uso, nunca mais uma busca
   que sabidamente retorna zero resultados.
3. Teste genérico cobre as 9 entradas de comando reais do
   `opencode.json`, executando o comando shell de verdade.
4. Limitações operacionais reais (modelo padrão offline, subagentes não
   invocáveis via `--agent`) documentadas explicitamente, não escondidas
   nem apresentadas como resolvidas.
5. Zero regressão na suíte completa.
