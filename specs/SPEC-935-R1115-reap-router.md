# SPEC-935-R1115 — Roteador REAP (uma skill índice, não 26)

## Objetivo

Publicar a biblioteca `REA-Prompts` como **uma** skill índice `reap-prompts`, com os 26 packs preservados como referências sob demanda e manifesto de hashes — sem instalar 26 skills no topo de `.opencode/skills`.

## Motivação

Instalar as 26 skills como entradas independentes diluiria o roteamento semântico do OpenCode e competiria com a skill oficial `reverse-engineer-anything`. O valor do REAP está nas receitas e na disciplina de evidência, não em 26 descrições concorrentes. Uma skill índice com tabela de capacidades e carregamento sob demanda preserva o valor e reduz o ruído.

## Escopo

### Em escopo
- `.opencode/skills/reap-prompts/SKILL.md` com frontmatter, tabela dos 26 packs, tiers de risco e política de uso.
- `.opencode/skills/reap-prompts/references/packs/<pack>.md` com os 26 packs copiados.
- `.opencode/skills/reap-prompts/.reap-manifest.json` com fonte, commit, licença e SHA-256 por pack.
- Teste `tests/test_reap_router.py`.

### Fora de escopo
- Instalar as 26 skills como diretórios independentes.
- Executar prompts, alvos ou scripts do repositório.
- Substituir a skill oficial `reverse-engineer-anything`.

## Requisitos

1. O frontmatter declara `name: reap-prompts` e descreve o uso.
2. A tabela lista os 26 packs com tema e tier de risco (`baixo`, `médio`, `alto`).
3. Cada pack listado existe em `references/packs/`.
4. O manifesto contém 26 entradas com SHA-256 verificável.
5. Packs de risco alto exigem alvo autorizado e proíbem execução do alvo.
6. Nenhum diretório `reap-*` adicional existe no topo de `.opencode/skills`.
7. O teste falha se um pack listado faltar ou se um hash divergir.

## Critérios de aceitação

- [ ] `find .opencode/skills -maxdepth 1 -type d -name 'reap-*'` retorna apenas `reap-prompts`.
- [ ] 26 arquivos em `references/packs/`.
- [ ] Manifesto com 26 hashes válidos.
- [ ] Tabela cobre `reap-00` a `reap-22`, `reap-prompts`, `reap-wildcard`, `reap-prompt-writing-tips`.
- [ ] `tests/test_reap_router.py` passa.

## Plano de testes

```bash
.venv/bin/python -m pytest tests/test_reap_router.py -q
```

Casos: contagem de packs, presença de cada arquivo, hash do manifesto, ausência de skills top-level extras, presença de tiers de risco.

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Conteúdo dual-use (malware, anti-cheat, DMA, cracking) | Tiers de risco e política explícita; alvo autorizado; sem execução |
| Diluição do catálogo | Uma única skill índice; packs como referências |
| Fork tratado como obra original | Licença MIT e crédito a Joas Antonio dos Santos preservados no índice e no manifesto |
| Deriva entre índice e packs | Teste verifica lista e hashes |

## Evidência

- Fonte: `/tmp/opencode/REA-Prompts`, commit `9756618f25af1920c8965f8969820eed22247936`.
- 26 packs, 104 blocos de prompt, 4.359 linhas Markdown.
- Licença MIT (© 2025 Joas Antonio dos Santos).
