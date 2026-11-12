---
spec_id: SPEC-935-R1113
component: integrations.reap_adapter
title: Adaptador REAP para OpenCode com dry-run, manifesto e rollback
version: 1.0.0
status: implemented
test_file: tests/test_reap_adapter.py
---

# SPEC-935-R1113 — Adaptador REAP para OpenCode

## Objetivo

Implementar um instalador determinístico da biblioteca `REA-Prompts` com alvo OpenCode, `dry-run`, manifesto, hashes e rollback, sem instalar as 26 skills no topo do catálogo.

## Motivação

O `setup.sh` do `REA-Prompts` instala em Hermes, Claude Code, Codex e Antigravity, mas não em OpenCode. Ele também faz `rm -rf` do destino e cópia cega, sem dry-run, backup, manifesto ou verificação. O Core precisa de um adaptador auditável, compatível com o gate de skills e com o princípio de não executar código de terceiro.

## Escopo

### Em escopo
- `integrations/reap_adapter.py` com API Python e CLI `python3 -m integrations.reap_adapter`.
- Operações: `plan`, `install`, `validate`, `rollback`.
- Layouts: `skills` (uma pasta por pack) e `references` (um Markdown por pack em `references/packs/`).
- Raízes permitidas: `.opencode/skills`, `~/.config/opencode/skills`, `~/.local/share/opencode/skills`.
- Manifesto `.reap-manifest.json` com fonte, commit, licença, timestamp, layout, arquivos e SHA-256.
- Backup de destinos existentes em `.reap-backup/<timestamp>/`.
- Testes em `tests/test_reap_adapter.py`.

### Fora de escopo
- Executar `setup.sh` ou qualquer script do repositório de origem.
- Instalar dependências, rodar npm/pip ou baixar modelos.
- Instalar as 26 skills no topo do catálogo (ver SPEC-935-R1115).

## Requisitos

1. `plan` não escreve no disco.
2. `install --dry-run` não escreve no disco.
3. `install` só escreve dentro de uma raiz permitida e nunca segue symlink para fora dela.
4. Nome de pack com `..`, `/`, `\\` ou caminho absoluto é rejeitado.
5. Manifesto registra SHA-256 de cada arquivo e permite `validate`.
6. `rollback` restaura backup e remove apenas arquivos cujo hash ainda confere; arquivo modificado é preservado e reportado.
7. Instalação repetida é idempotente: arquivos idênticos são reportados como `identical`, não recopiados.
8. Nenhum arquivo é apagado fora da raiz de destino.

## Critérios de aceitação

- [ ] `plan` e `install --dry-run` deixam o destino inalterado.
- [ ] `install` cria arquivos e `.reap-manifest.json`.
- [ ] `validate` confirma todos os hashes.
- [ ] `rollback` remove os instalados e restaura o backup.
- [ ] Testes negativos de path traversal e raiz não permitida passam.
- [ ] `tests/test_reap_adapter.py` passa.

## Plano de testes

```bash
.venv/bin/python -m pytest tests/test_reap_adapter.py -q
```

Casos: descoberta, dry-run, instalação, idempotência, manifesto, rollback, path traversal, raiz proibida, layout `references`.

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Apagar arquivos do usuário | Backup antes da escrita; rollback por hash; nenhuma remoção fora do destino |
| Path traversal | Resolução canônica + verificação de prefixo; rejeição de `..` e absolutos |
| Manifesto mentir sobre o conteúdo | `validate` recomputa SHA-256 e falha em divergência |
| Instalação parcial | Escrita atômica por arquivo e manifesto escrito ao final; rollback disponível |

## Evidência

- Fonte analisada: `/tmp/opencode/REA-Prompts`, commit `9756618f25af1920c8965f8969820eed22247936`.
- Licença: MIT (© 2025 Joas Antonio dos Santos).
- 26 packs, 4.359 linhas Markdown.
