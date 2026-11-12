---
spec_id: SPEC-935-R1112
component: .opencode.skills.reverse-engineer-anything
title: Alinhamento da skill REA v37 para v49
version: 1.0.0
status: implemented
test_file: tests/test_rea_skill_alignment.py
---

# SPEC-935-R1112 — Alinhamento da skill REA v37 → v49

## Objetivo

Substituir a skill instalada `.opencode/skills/reverse-engineer-anything` (versão 37, 170 ferramentas) pela versão oficial 49 (229 ferramentas) distribuída com o pacote `rea-agents` 6.8.0, preservando licença, procedência e rollback.

## Motivação

A sessão REA 6.8.0 declarou `skill.expected_version = 49`, enquanto a skill instalada declarava `37`. O servidor respondeu `alignment.state = "unknown"` por falta de identidade comparável. A defasagem é uma dívida mensurável: a skill antiga não descreve as 59 ferramentas novas nem a referência `environments.md` (AgentEnv bundles).

## Escopo

### Em escopo
- Backup integral da v37 em `.opencode/skills/.archive/reverse-engineer-anything-v37/`.
- Cópia da v49 de `/home/marceloclaro/.local/share/opencode-core/rea-6.8.0/skills/reverse-engineer-anything/`.
- Remoção da referência obsoleta `search-before-reconstruction.md` (não citada pela v49).
- Atualização de `origin.json` com pacote, versão, commit, versão da skill, contagem de ferramentas e hashes.
- Teste de contrato em `tests/test_rea_skill_alignment.py`.

### Fora de escopo
- Instalar Ghidra, IDA, Hopper, Kuna ou qualquer provider nativo.
- Alterar o servidor REA ou o pacote `rea-agents`.
- Promover confiança ou validar externamente o conteúdo da skill.

## Requisitos

1. O frontmatter da skill deve declarar `metadata.version: "49"` e `metadata.tool_count: 229`.
2. Todas as referências citadas no `SKILL.md` devem existir em `references/`.
3. `origin.json` deve registrar `version: "6.8.0"`, `skill_version: "49"`, `tool_count: 229`, `source_directory`, `license` e `skill_sha256`.
4. O hash em `origin.json` deve ser o SHA-256 real do `SKILL.md` instalado.
5. O backup da v37 deve permanecer legível e com hash registrado.
6. Nenhum arquivo fora de `.opencode/skills/reverse-engineer-anything/` e `.opencode/skills/.archive/` pode ser alterado.

## Critérios de aceitação

- [ ] `sed -n '1,10p' SKILL.md` mostra `version: "49"`.
- [ ] `find references -name '*.md' | wc -l` = 7.
- [ ] `grep -c 'search-before-reconstruction' SKILL.md` = 0.
- [ ] `origin.json` valida em JSON e o hash confere.
- [ ] `tests/test_rea_skill_alignment.py` passa.
- [ ] Backup v37 existe com `SKILL.md` e 7 referências.

## Plano de testes

```bash
.venv/bin/python -m pytest tests/test_rea_skill_alignment.py -q
```

Casos:
1. Frontmatter v49 e tool_count 229.
2. Referências citadas existem.
3. `origin.json` com versão e hash corretos.
4. Ausência de referência obsoleta.
5. Comparação opcional com o pacote instalado (skip se ausente).

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Sobrescrever customização local | Backup versionado antes da cópia; hash do backup |
| Skill nova citar ferramenta ausente no servidor | Teste compara `tool_count` com o catálogo quando disponível |
| Sessão em execução continuar com a skill antiga | Reinício explícito documentado; o teste lê o disco, não a sessão |
| Confundir atualização de instrução com validação de execução | `verification: installation_only`; nenhuma promoção de confiança |

## Evidência

- Skill v49: `/home/marceloclaro/.local/share/opencode-core/rea-6.8.0/skills/reverse-engineer-anything/`
- SHA-256 v49: `8818b645c9fd348399a50a8678b91cff20215690adad484e70282ff9f2ef91ee`
- SHA-256 v37: `6715cfb03512db108e0151e5429fb2c305ae17ea75266dbf2b1454285ea37b4e`
- Servidor: `rea-agents` 6.8.0, 229 ferramentas, skill esperada 49.
