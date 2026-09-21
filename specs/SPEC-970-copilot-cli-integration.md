# SPEC-970: Integração da CLI GitHub Copilot (`@github/copilot`) no doctor

**Round**: R547 (evolution registry)
**Data**: 2026-09-21
**Status**: Implementado — 7 testes TDD verdes
**Score**: 1.0 (gate SDD pass; regressão 103 passed / 2 skipped)

## Objetivo

Integrar a CLI oficial do GitHub Copilot ao monitoramento de CLIs externas
de primeira classe do ecossistema (`EXTERNAL_CLIS` do `doctor.py`), de modo
que:

1. O `doctor` reconheça a presença/ausência do binário `copilot` no PATH
   (mesmo tratamento `warn`-nunca-`fail` das demais CLIs opcionais).
2. A sugestão de instalação exata (`npm install -g @github/copilot`)
   apareça no detalhe do check e no helpdesk quando o binário estiver ausente.
3. Nenhum teste de regressão existente quebre (contagem dinâmica via
   `len(EXTERNAL_CLIS)` — lição R473).

## Contexto

- O pacote legado `@github/copilot-cli` não existe mais no registry npm
  (E404). O nome canônico atual é `@github/copilot`, binário `copilot`,
  versão 1.0.87 (latest), dependência única `detect-libc` (loader que
  baixa binário nativo), sem restrição de `engines`.
- Node v22.23.1 / npm 10.9.8 disponíveis; prefix global
  `/home/marceloclaro/.npm-global` já no PATH.
- A instalação foi feita com sucesso:
  `npm install -g @github/copilot` → `added 3 packages`.
- O ecossistema já monitora 7 CLIs externas; esta spec adiciona a 8ª.

## Critérios de aceitação

- CA1: `copilot` presente em `marceloclaro.doctor.EXTERNAL_CLIS` com comando
  exato `npm install -g @github/copilot`.
- CA2: `_check_external_clis()` retorna `warn` (nunca `fail`) com sugestão do
  copilot quando o binário está ausente; `pass` citando o copilot quando
  presente.
- CA3: ausência isolada do copilot produz detail `1/N` com apenas a sugestão
  do copilot.
- CA4: `helpdesk` inclui o copilot na sugestão de CLIs ausentes.
- CA5: regressão completa das suítes que tocam o doctor (r116, r120, r473,
  r212, runai) permanece verde.

## Arquivos tocados

- `marceloclaro/doctor.py` — entrada em `EXTERNAL_CLIS` + docstring.
- `marceloclaro/helpdesk.py` — mensagem de sugestão citando GitHub Copilot.
- `tests/test_r547_copilot_cli.py` — 7 testes RED/GREEN herméticos.

## Verificação

- `python3 -m pytest tests/test_r547_copilot_cli.py` → 7 passed.
- `python3 -m pytest tests/test_r116... tests/test_r120... tests/test_r473...
  tests/test_r212... tests/test_runai_integration.py` → 103 passed, 2 skipped.
- `copilot --version` → `GitHub Copilot CLI 1.0.87`.