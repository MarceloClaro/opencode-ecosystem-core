---
spec_id: SPEC-935-R621
title: "Federação de Artefatos Multi-Harness (Claude / Codex / Antigravity / ChatGPT → OpenCode Core) com cabeça de atenção própria no Transformer do marceloclaro"
component: integrations/harness_federation + transformer/harness_head.py
test_file: tests/test_r621_harness_federation.py
status: green
---

# SPEC-935-R621 — Federação de Artefatos Multi-Harness
=====================================================

## 1. Visão Geral

O Core já *integra* CLIs externas (`integrations/gemini_cli.py`,
`integrations/antigravity/bridge.py`, `integrations/goose_cli.py`,
`integrations/plandex_cli.py`, `integrations/reasonix_cli.py`), mas não
**ingere os artefatos** que esses ecossistemas de agente já produzem: skills
(`SKILL.md`), subagentes (`agents/*.md`), comandos slash (`commands/*.md`),
hooks (`hooks.json`) e especificações (`AGENTS.md`, `CLAUDE.md`,
`.codex-plugin/plugin.json`, `SKILL_CHATGPT.md`).

`CliEcosystemBridge` (SPEC-935-R233) descreve os três CLIs a partir da mera
presença de arquivos (`CLAUDE.md`, `AGENTS.md`) e devolve listas fixas de
comandos slash. Isso é um relatório de *intenção*, não um inventário: ele não
lê nenhum artefato, não conta nenhum `SKILL.md` e não distingue um plugin
instalado de um plugin apenas cacheado.

Esta especificação entrega a **federação de artefatos**: descoberta real no
sistema de arquivos, normalização em um modelo canônico, portabilidade para o
formato nativo do OpenCode e — o ponto central — uma **cabeça de atenção
`harness`** no Transformer do orquestrador `marceloclaro`, para que um artefato
externo seja candidato de roteamento com o mesmo peso de rigor que um agente
do catálogo.

## 2. Escopo — Quatro ecossistemas

| Ecossistema | Raízes varridas | Artefatos |
|---|---|---|
| `claude` | `~/.claude/{skills,agents,commands}`, `~/.claude/plugins/cache/*/*/`, `~/.claude/plugins/marketplaces/*/`, `<repo>/.claude/` | skills, agents, commands, hooks, specs |
| `antigravity` | `~/.gemini/antigravity-cli/builtin/skills/`, `<repo>/.antigravity/` | skills, specs, binário `agy` |
| `codex` | `~/.codex/`, `<repo>/**/.codex-plugin/plugin.json` | prompts, plugins, specs |
| `chatgpt` | `<repo>/**/SKILL_CHATGPT.md`, `agents/openai.yaml`, `plugin.json#interface` | prompt packs, policies |

## 3. Requisitos Funcionais

### 3.1 `artifact.py` — `HarnessArtifact`
- Modelo canônico imutável com: `artifact_id`, `ecosystem`, `kind`, `name`,
  `description`, `source_path`, `source_root`, `origin`, `license`, `version`,
  `capabilities`, `tags`, `hook_events`, `hook_commands`, `metadata`,
  `duplicate_paths`, `degraded_reasons`, `status` (`ok` | `degraded`) e **dois
  hashes distintos**:
  - `content_sha256` — só o **corpo** (sem frontmatter). Sobrevive à reescrita
    de metadados no destino e é o que a deduplicação compara.
  - `source_file_sha256` — o **arquivo inteiro** de origem. Conferível com
    `sha256sum`, sem depender deste código.
- `parse_frontmatter(text) -> (dict, body)`: separa `---` YAML inicial do corpo.
- `parse_hook_manifest(text) -> (events, commands)`: lê `hooks/hooks.json`
  (formato Claude: evento → lista de matchers → lista de comandos), preservando
  a **ordem de declaração** dos eventos.
- `slugify` remove acentos por NFD antes de aplicar o regex, para que
  "Código" e "codigo" produzam o mesmo destino.
- **Fail-closed**: artefato sem `name` ou sem `description` (quando o formato
  de destino exige) nasce `degraded` com razão explícita; nunca é emitido como
  se estivesse íntegro.
- `blocking_reasons` separa degradação que **impede** o uso (ex.:
  `source_not_found`) de degradação que é apenas **aviso**
  (`license_undeclared`). Licença ausente rebaixa confiança, mas não torna o
  artefato `unavailable` — caso contrário quase todo artefato de terceiros
  seria descartado e a cabeça `harness` ficaria vazia.

### 3.2 `harvest.py` — `HarnessHarvester`
- `discover() -> List[HarnessArtifact]`: varredura real dos quatro ecossistemas.
- `inventory() -> Dict[str, Any]`: contagens por ecossistema × tipo, contagem
  `third_party`, raízes efetivamente varridas e as ausentes (declaradas, para
  que o relatório possa dizer "não achei" em vez de omitir), e o relatório
  **histograma por motivo** da degradação.
- O relatório separa dois veredictos que costumam ser confundidos:
  `synchronized` (nenhum aviso) e `synchronized_strict` (nenhum bloqueio).
  Uma lista de 286 itens com a mesma razão é ruído; o histograma
  `degraded_by_reason` diz "286: 1 aviso de licença" e o operador não precisa
  abrir a lista para saber o que fazer.
- `duplicates_collapsed` sai de `duplicate_paths`, não de `len(by_path) -
  len(unique)`: quando o canônico é preservado, o caminho duplicado é
  registrado no artefato mas não entra no dicionário de caminhos, e a
  subtração reportava zero duplicatas numa varredura que tinha uma.
- `origin` distingue `first_party` / `third_party` / `user` — cache de plugin
  de terceiro **não** é baseado como artefato de primeira parte. Arquivos
  diretamente sob `~/.claude` ou `~/.codex` são `user` por padrão, salvo
  marcador de terceiro: proveniência não é inferida só do nome do plugin.
- `artifact_id` inclui `kind` (`ecosystem:kind:origin:slug`), porque hooks e
  comandos podem legitimamente ter o mesmo slug em ecossistemas distintos.
- Deduplicação: mesma origem lógica em raízes espelhadas (cache + marketplace)
  colapsa em um artefato, com os caminhos duplicados preservados em
  `duplicate_paths`. Espelhos de `.claude`/`.codex` dentro de plugins
  instalados em `~/.claude` são ignorados para não recontar a mesma skill.
- Nenhum número é fixo no código: tudo vem do que existe no disco.

### 3.3 `emit.py` — `HarnessEmitter`
- `emit_skill(artifact) -> Dict[str, Any]`: grava
  `.opencode/skills/<slug>/SKILL.md` com frontmatter canônico
  (`name`, `description`) + bloco de proveniência (`source`, `license`,
  `content_sha256`, `upstream_path`).
- `emit_agent(artifact) -> Dict[str, Any]`: grava `.opencode/agents/<slug>.md`.
- `emit_hooks(artifact) -> Dict[str, Any]`: grava manifesto normalizado em
  `.opencode/hooks/manifests/<slug>.json` — **não** executa comando de terceiro.
- `export_codex_plugin(artifact) -> Dict[str, Any]`: emite
  `.codex-plugin/plugin.json` normalizado (formato Codex/ChatGPT).
- `export_chatgpt_instructions(artifact) -> Dict[str, Any]`: emite
  `SKILL_CHATGPT.md` normalizado.
- `dispatch(artifact) -> Dict[str, Any]`: única porta de entrada, escolhe o
  emissor pelo `kind`. Um `kind` desconhecido é erro explícito, não um `else`
  silencioso que grava no lugar errado.
- `emit_all(artifacts, kinds, require_license=False, execute=False) -> Dict`:
  relatório por tipo, com `selected`, `emitted`, `skipped`, `refused` e
  `synchronized`.
- **Recusa visível, não sumiço**: com `require_license=True` o artefato sem
  licença detectada permanece em `selected` e vai para `refused` com a razão
  `license_required_by_operator`. Filtrá-lo antes de `selected` faria o
  relatório parecer completo quando não é.
- **Dry-run por padrão**: sem `execute=True` nada é gravado; o relatório sai
  com `executed: false`, para que a emissão em massa no repositório seja sempre
  uma decisão consciente.
- **Idempotente**: reexecutar sobre o mesmo artefato não muda o conteúdo.
- **Anti-execução**: nenhum artefato de terceiro é executado; o manifesto de
  hooks é *dado* (`execution: blocked_pending_human_review`) e o relatório
  declara `hooks_executed: 0`, o comando upstream permanece inerte até decisão
  humana.

### 3.4 `transformer/harness_head.py` — cabeça `harness`
- `HarnessAttentionHead`: produz utilidade por artefato combinando
  (a) similaridade semântica com a tarefa, (b) cobertura de capacidades
  declaradas, (c) maturidade (`ok` > `degraded`) e (d) procedência
  (`first_party`/`user` > `third_party`).
- `harness_scores(task_description, required, cards) -> Dict[str, List[float]]`
  com saídas em `[0, 1]`, mesma forma das 4 cabeças existentes.
- **Tokenização bilíngue determinística**: normalização NFD com remoção
  explícita de combining marks, stopwords, stemming e um glossário
  PT-BR → inglês canônico. O glossário é aplicado **antes** do stemming e
  uma **segunda vez depois**, para que plurais e variações acertem
  ("análises" → "análise" → `analysis`); a forma canônica é sempre preservada,
  de modo que o stemming nunca cale um termo presente no glossário. Sem isso,
  "testes" não casa com `test-driven-development` e o ranking degenera em
  ordem alfabética.
- `HarnessRegistry`: indexa os artefatos descobertos e os expõe como
  *agent cards* (`agent_id`, `capabilities`, `status`, `confidence_score`,
  `blocking`, `blocking_reasons`, `load`) consumíveis pelo `AttentionRouter`.
- `attach_to_router(router)`: injeta a cabeça `harness` como **quinta cabeça**
  sem quebrar o contrato convexo de 4 cabeças do `AttentionRouter` — a
  extensão é opt-in e o router original continua íntegro por padrão. O estado
  (`mix`) é mantido em closure **mutável compartilhada**, para que um
  reattach com `mix=0` reverta de fato para o legado em vez de deixar
  uma lista morta de estados antigos.
- Hard gate: artefato com `blocking_reasons` é elegível, mas recebe confiança
  0 por defeito (fail-closed na utilidade, sem exclusão silenciosa). Aviso não
  bloqueante (licença não declarada) rebaixa a confiança, mas mantém o
  artefato roteável.

## 4. Integração com o Transformer do `marceloclaro`

- `MarceloClaroOrchestrator` ganha `harness_federation()` (lazy, sem I/O na
  construção), `route_to_harness(task, required)` e
  `emit_harness_artifacts(...)`, que devolvem ranking, explicação das 5 cabeças
  e relatório de emissão. O registry é construído sob demanda
  (`self._harness_registry is None`), nunca no `__init__`.
- `transformer/__init__.py` exporta `HarnessAttentionHead`, `HarnessRegistry`.
- A cabeça é determinística e auditável: `explain()` expõe cada componente do
  score, sem caixa-preta.
- `python3 -m marceloclaro.cli harness inventory|route|emit` é a superfície de
  linha de comando. O subcomando é resolvido **antes** de construir o
  orquestrador, para que um relatório de inventário não pague o custo de
  carregar o catálogo inteiro. O código de saída de `inventory` reflete
  `ecosystems_missing`, e não o mero sucesso do processo.

## 5. Invariantes (fail-closed)

- **INV-R621.1** — Todo artefato emitido carrega `source_path`, `license`,
  `content_sha256` e `source_file_sha256`; artefato sem licença detectada é
  marcado `license_undeclared`, que é **aviso**, e não pode ser silenciosamente
  tratado como sinalizado.
- **INV-R621.2** — Descoberta é verificável: `inventory()` declara as raízes
  varridas **e as ausentes**, e um artefato só é contado se o arquivo existir no
  disco.
- **INV-R621.3** — Portabilidade é fiel: `content_sha256` do destino é igual ao
  do corpo de origem, sem mutação silenciosa; `source_file_sha256` confere
  contra o arquivo original.
- **INV-R621.4** — Nenhum comando de terceiro é executado pelo emissor; o
  relatório declara `hooks_executed: 0`.
- **INV-R621.5** — Pesos da cabeça `harness` somam 1 e são convexa positiva.
- **INV-R621.6** — Anti-overclaim: `inventory()` distingue
  `discovered` de `emitted`; nenhum relatório afirma sincronização completa
  quando há ecosystems ausentes, artefatos degradados ou recusas.
- **INV-R621.7** — Isolamento: os testes R621 não escrevem em
  `agents/catalog/`, `livro-core/` ou no worktree do operador, e não
  reaproveitam o `EVOLUTION_*` de outro ciclo.

## 6. Fora de escopo

- Não executa hooks de terceiros.
- Não instala binários (`codex`, `reasonix` ausentes permanecem ausentes; o
  relatório diz `available: false`).
- Não altera `opencode.json` — a regeneração continua sendo
  `python3 -m integrations.opencode_cli`.
- Não emite em massa dentro do repositório: a CLI exige `--execute`, e a
  emissão efetiva no worktree do operador continua sendo decisão humana.

## 7. Evidência de validação

Executado em 2026-09-29, com deriva não relacionada no worktree (catálogo e
`livro-core`, ciclos R380/R617/R619/R620), que não toca nenhum arquivo desta
especificação.

- `.venv/bin/python -m pytest tests/test_r621_harness_federation.py -q` →
  **39 passed**.
- `ruff check --select F,E9` limpo em `integrations/harness_federation/`,
  `transformer/harness_head.py` e `tests/test_r621_harness_federation.py`. Os
  avisos restantes do repositório (inclusive `F821` em `marceloclaro/cli.py`)
  foram confirmados por `git stash` como pré-existentes, não introduzidos aqui.
- Suíte completa, excluindo apenas os 4 arquivos de teste do trabalho
  paralelo: **4423 passed, 81 skipped** em 876 s.
- Inventário real: `320` artefatos descobertos, `19` duplicatas colapsadas
  (auditáveis por `duplicate_paths`), `247` cards roteáveis, `0` bloqueantes.
  As `286` degradações são **todas** `license_undeclared`, ou seja, aviso:
  `synchronized: false` (estrito) com `synchronized_strict: true`.
- `harness emit --kinds skill,hook --require-license` em dry-run:
  `selected=193`, `emitted=32`, `refused=161`, `synchronized: false` — o
  relatório **recusa** em vez de omitir. Saída `1`, porque o comando está
  dizendo "há recusas" e não "quebrou".
- Ranking observado: `test-driven-development` no topo para tarefas de TDD;
  skills de code review no topo para revisão de código.
- Nenhuma emissão em massa foi feita no repositório: `--execute` só é testado
  contra `tmp_path`.
