# SPEC-935-R648 — Federação opt-in de raízes externas (extensão R621)

**Ronda:** R648 (SPEC) / evolução R652
**Status:** em implementação
**Data:** 2026-10-03
**Autor:** marceloclaro (orquestrador central)
**Padrão:** M7 federado — extensão compatível da SPEC-935-R621

## Objetivo

Permitir que o `HarnessHarvester` (R621) varra raízes externas opt-in —
ex.: clones persistentes `~/claude-federation/claude-code-harness` (39 skills)
e `~/claude-federation/claude-plugins-official` (29 plugins Apache-2.0
federáveis + 13 externos sem licença, bloqueados) — sem alterar o
comportamento padrão e sem tocar no protocolo MCP.

## Mecânica

- Variável `HARNESS_FED_EXTRA_ROOTS`: entradas separadas por `os.pathsep`,
  cada uma `ecossistema|rotulo|origem|caminho`. Rótulos NÃO contêm `:`
  (é o separador). Malformadas ou inexistentes
  são ignoradas em silêncio (nunca fail).
- `ecossistema` restrito a `{claude, antigravity, codex, chatgpt}`; demais
  valores ignorados. `origem` padrão `third_party` quando vazia.
- Deduplicação existente (por caminho e por conteúdo) continua valendo:
  clones aninhados não inflam contagem.

## Critérios de aceitação

1. Sem a variável: `discover()` idêntico ao R621 (regressão zero).
2. Com raízes válidas: artefatos do clone aparecem com `source_root` e
   `origin` declarados.
3. Entradas malformadas, ecossistema inválido e caminho inexistente:
   ignorados, sem exceção.
4. Licença NÃO é inferida pelo harvester: plugins sem LICENSE seguem
   `license_undeclared`/degraded no relatório (auditoria em
   `~/claude-federation/auditoria-licencas.json`, fora do repo).
5. Gate TDD: `tests/test_r648_fed_extra_roots.py` 100% + suíte R621 verde.
6. Ciclo R652 registrado.

## Decisões registradas

- Opt-in por env (não config versionada): raízes são máquinas-específicas;
  nada de `/tmp` (efêmero) como raiz.
- Sem execução de binários de terceiros pelo harvester (só leitura).
- `bin/harness doctor` e `setup-opencode.sh` provados fora do repo
  (throwaway); `setup-opencode.sh` NÃO roda no Core (escreveria
  `.opencode/skills` + `AGENTS.md`).
