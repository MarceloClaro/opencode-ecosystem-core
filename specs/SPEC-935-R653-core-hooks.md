# SPEC-935-R653 — Hooks do Core (engine + política fail-closed)

**Ronda:** R653 (SPEC)
**Status:** em implementação
**Data:** 2026-10-04
**Autor:** marceloclaro (orquestrador central)
**Padrão:** M7 — subsistema nativo (espelha semântica Claude `PreToolUse`, sem copiar código)

## Objetivo

Dar ao Core hooks próprios e auditáveis: `hooks/engine.py` (roteamento por
matcher + decisão) e `hooks/policy.py` (deny-list destrutiva + auditoria
append-only), fiados ao `opencode_agent_sdk` — sem depender do Claude,
sem rede e sem segredos.

## Semântica (compatível por desenho, não por cópia)

- Eventos: `PreToolUse`, `PostToolUse`, `SessionStart`, `SessionEnd`.
- `HookMatcher(matcher, hooks=[fn])`: `matcher` casa por igualdade,
  prefixo `Bash` (qualquer comando bash) ou regex `re:…`.
- Veredito: `allow` padrão; `deny` via `False`, `{"deny": True}` ou
  `{"permissionDecision": "deny"}` (vocabulário Claude aceito).
- **Fail-closed**: hook que lança exceção nega (lição R650 registrada).

## Política padrão (deny-list, documentada e testada)

Bash nega: `rm -rf /|~|$HOME`, `mkfs`, fork-bomb, pipes `curl|wget → sh|bash`,
escritas em `/dev/sd*|/dev/nvme*`, `chmod -R 777 /`, e comandos contendo
nome de segredo (`*_TOKEN`, `*_SECRET`, `*_KEY`) combinado com `curl|wget|nc`.
Todo o resto passa (allowlist seria paralisante; deny-list é auditável).

## Auditoria

`audit_log(evento, registro)` → JSONL append-only em
`~/.cache/opencode-hooks/audit.jsonl` (fora do repo; override por
`OPENCODE_HOOKS_AUDIT`). Nunca falha o chamador (best-effort com silêncio).

## Critérios de aceitação

1. Roteamento: match exato, prefixo e regex; sem match = allow.
2. Cada padrão da deny-list negado; comandos seguros passam (tabela no teste).
3. Hook que lança → deny com motivo.
4. Auditoria grava JSONL válido; falha de disco não lança.
5. `opencode_agent_sdk` aceita `hooks={"matchers": [...]}` além de lambdas.
6. Gate TDD 100% + skill/card + ciclo de evolução. Sem mudança em
   `opencode.json`/doctor (blast radius mínimo).
