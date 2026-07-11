# R137 — Reconciliação do gerador opencode.json + versionamento seguro da frente cloud

## Objetivo

Fechar e versionar a frente de integração cloud (R135–R136) de forma
honesta, corrigindo os defeitos estruturais reais que a reavaliação
encontrou — sem overclaim, sem perda de dados, sem arrastar 324 arquivos
externos não revisados.

## Contexto

A reavaliação do relatório final da integração cloud (que alegava "94
ciclos, 173 agentes, 49/49 testes, zero regressões, 56/56 Apache 2.0")
confirmou parte das entregas mas expôs três problemas concretos que um
"pronto" apressado teria escondido.

## Mudanças Entregues

1. **Gerador reproduzível (`integrations/opencode_cli.py`)**: `_catalog_agents`
   passa a chavear cada agente pelo **slug do nome do arquivo** (`basename`
   sem `.md`), não pelo frontmatter `name:`. Antes, `adr-manager.md`
   (`name: ADRManager`) virava a chave `ADRManager` e `cloud-alloydb-specialist.md`
   (`name: Cloud AlloyDB Specialist`) virava `Cloud AlloyDB Specialist` — mas
   o `opencode.json` em disco fora montado à mão com os cloud por slug. O
   comando documentado de regeneração divergia do arquivo e quebraria os
   testes cloud. Agora `python3 -m integrations.opencode_cli` reproduz
   exatamente o commitado (173 agentes, todos por slug).

2. **Skip guards nos testes cloud** (`test_r130`, `test_r131`): os 6 testes
   que inspecionam `scripts/cloud/` no disco ganham `@skipif` — pulam em
   checkout limpo, validam quando o backup externo está presente. Sem isso,
   excluir os 324 scripts quebraria a suíte num clone limpo.

3. **`scripts/cloud/` no `.gitignore`**: 324 arquivos de terceiros com
   procedência/licença não verificadas ficam fora do versionamento até
   revisão. Decisão explícita do usuário ("só o código do ecossistema").

4. **Bug de perda de dados corrigido (`evolution/cycles.json`)**: o trabalho
   cloud reescrevera o ledger via `EvolutionRegistry.save()` apagando
   `conclusion`/`results` de R81–R84. Reconstruído por append: HEAD
   (R47–R129 intactos) + R130–R136; diff 100% aditivo.

5. **Novo teste TDD** (`tests/test_r137_opencode_config_reproducible.py`):
   trava chaveamento por slug + determinismo + reprodução exata do
   `opencode.json` commitado.

6. **Fontes cloud versionados**: catálogo (`cloud-*.md`,
   `skills-cloud-antigravity.md`), `academic/maswos.py`, `academic/__init__.py`,
   `integrations/antigravity/antigravity-bridge.ts`, `specs/SPEC-935-R130.md`.

## Verificação

- TDD: teste de reprodutibilidade escrito antes → vermelho (2 falhas) →
  verde após corrigir o gerador.
- `python3 -m pytest tests/ -q` completo.
- `git diff --numstat evolution/cycles.json` puramente aditivo.

## Lições

1. **Reavaliar antes de "fechar" evitou dois defeitos silenciosos.** O
   relatório cloud alegava sucesso, mas o `opencode.json` não era
   reproduzível pelo próprio gerador e o `cycles.json` já tinha perdido
   dados. "Verificado" não é o que o relatório afirma — é o que a
   regeneração determinística e o `git diff --numstat` mostram.
2. **Artefato gerado deve ser reproduzível pelo gerador, senão é dívida.**
   Um `opencode.json` montado à mão que nenhum comando reproduz apodrece na
   primeira regeneração. Chavear por slug de arquivo (estável) em vez de por
   nome de exibição (mutável) é a diferença entre determinístico e frágil.
3. **Procedência importa.** 324 scripts externos com licença não auditada
   não entram no repositório só porque "passam nos testes" — gitignore +
   pendência registrada é mais honesto que um commit cego.

## Score

**8.6/10**

- Fecha a frente cloud de forma reproduzível e sem perda de dados, com
  diagnóstico honesto do que não foi confirmado (Apache 2.0, numeração).
- A re-chaveagem por slug reconcilia ~90 chaves de agente de uma vez —
  correção estrutural real, não cosmética.
- Fica dívida assumida: numeração de ciclos inconsistente (R130–R134
  Molambudos vs R135–R136 cloud), colisão do nome `SPEC-935-R130.md`, e a
  auditoria de licença dos scripts externos.
