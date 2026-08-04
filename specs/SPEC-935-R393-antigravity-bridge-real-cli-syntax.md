---
spec_id: SPEC-935-R393
title: Bridge do Antigravity CLI passa a usar a sintaxe real do agy (e para de reportar sucesso silencioso)
component: integrations/antigravity/bridge.py, integrations/cli_ecosystem_bridge.py
status: verified
test_file: tests/test_r393_antigravity_bridge_delegate_fix.py
---

# SPEC-935-R393 — Bridge do Antigravity CLI Corrigido

**Data:** 2026-08-03
**Motivação:** o usuário perguntou se os três CLIs (OpenCode, Antigravity,
Claude Code) estão todos funcionais. Testando cada um com os binários
reais instalados neste ambiente (`opencode` v1.18.11, `agy` v1.1.8,
`claude`), o OpenCode CLI carregou de verdade os 205+ agentes do
catálogo (confirmada inclusive a propagação da correção de permissão do
`contextscout` feita no R391). O Antigravity CLI, porém, revelou dois
bugs reais quando testado de ponta a ponta.

## 1. Sintaxe de comando inválida

`integrations/antigravity/bridge.py::AntigravityBridge.delegate()`
montava:

```python
[self.cli_command, "run", "--agent", agent, "--prompt", prompt]
```

O binário real `agy` **não tem** subcomando `run` nem flag `--prompt`
nesse formato — confirmado rodando `agy --help`. A sintaxe real de modo
não-interativo é `--print`/`-p` combinada com `--agent` e
`--output-format`. Rodar o comando antigo faz o `agy` tentar abrir uma
sessão de TUI interativa, que falha:
`bubbletea: error opening TTY: could not open TTY: open /dev/tty: no
such device or address`.

## 2. Falha silenciosa (achado mais grave)

O erro acima sai com `returncode == 0`. `delegate()` só checava
`proc.returncode == 0` para decidir `"status": "completed"` — ou seja,
toda delegação, sempre, reportava sucesso mesmo não tendo feito nada de
útil. Confirmado ao vivo rodando o bridge Python real antes da correção:

```
{'status': 'completed', 'stdout': 'CLI error: bubbletea: error opening
TTY...', 'returncode': 0}
```

## 3. Correções

- `delegate()` agora monta
  `[cli_command, "--agent", agent, "--print", prompt, "--output-format", "text"]`.
- Mesmo com `returncode == 0`, se `stdout` começar com `"CLI error:"` ou
  `"Error:"` (prefixos reais observados nas duas classes de erro
  testadas — TTY e modelo inválido), o status é `"failed"`, não
  `"completed"`.
- `integrations/cli_ecosystem_bridge.py::discover_cli_capabilities()`:
  `antigravity_cli.active` checava a existência de `AGENTS.md` —
  documentação do **OpenCode CLI** (conforme sua própria primeira linha),
  sem relação com o Antigravity. Trocado por `shutil.which("agy")`, o
  sinal real.
- `get_unified_status()`: `"unified_status"` era uma **string fixa**
  (`"fully_synchronized"`), reportada independentemente de qualquer
  verificação real. Passa a ser computada a partir de
  `discover_cli_capabilities()` — só `"fully_synchronized"` quando os
  três ecossistemas estão de fato ativos; caso contrário,
  `"partially_synchronized"` com a lista real de ausentes em `"missing"`.

## 4. Verificação

- TDD: `tests/test_r393_antigravity_bridge_delegate_fix.py` (5 testes: 4
  com mock determinístico da sintaxe/detecção de falha, 1 de integração
  real contra o binário `agy`, pulado automaticamente se ausente).
- `tests/test_r233_cli_ecosystem_unification.py`: 2 testes novos + os 2
  existentes que dependiam da string fixa corrigidos para computar o
  resultado esperado a partir do mock de `shutil.which`, não mais
  hardcoded.
- Verificação end-to-end real (não só mock): `AntigravityBridge().
  delegate("responda apenas: bridge corrigido", ...)` retornou
  `{"status": "completed", "stdout": "bridge corrigido\n"}` — delegação
  real, resposta real de modelo via `agy`.
- Suíte completa: **2682 aprovados (+8), 0 falhas, 55 pulados** — zero
  regressão.

## 5. O que continua sem solução (não escondido)

`agy agents` continua retornando zero agentes — nenhum dos 205+ agentes
do catálogo deste ecossistema está registrado/descobrível pelo
Antigravity CLI como um "agente" selecionável via `--agent <nome>`.
Corrigir a sintaxe de delegação não resolve essa lacuna mais ampla —
delegar via `agy` hoje só invoca o comportamento padrão do próprio
Antigravity, não um dos agentes especializados deste catálogo. Da mesma
forma, o Claude Code CLI continua sem `.claude/agents/` — seu mecanismo
nativo de subagentes não enxerga o catálogo. Este ciclo corrigiu a
sintaxe de invocação e a detecção de falha do bridge Antigravity — não
implementou a integração profunda do catálogo com nenhum dos dois CLIs
externos, que permanece como trabalho futuro caso solicitado.

## 6. Critérios de aceitação

1. `delegate()` usa a sintaxe real do `agy` (`--agent`/`--print`/
   `--output-format`), nunca o subcomando `run`/flag `--prompt`
   inexistentes.
2. Uma saída de erro conhecida do `agy` com `returncode == 0` é
   reportada como `"failed"`, nunca `"completed"`.
3. `antigravity_cli.active` reflete o binário real (`shutil.which`), não
   um arquivo de documentação de outro CLI.
4. `unified_status` é sempre computado, nunca uma constante.
5. Verificação real (não só mockada) confirmando que uma delegação
   genuína completa com sucesso via `agy`.
6. Zero regressão na suíte completa.
7. Lacunas remanescentes (catálogo não descoberto por `agy`/Claude Code)
   documentadas explicitamente, não escondidas nem fabricadas como
   resolvidas.
