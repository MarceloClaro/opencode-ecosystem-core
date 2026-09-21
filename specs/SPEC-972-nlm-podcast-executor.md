# SPEC-972: Executor de Podcast Gemini Notebook (`nlm`) — Fase 1 (operador)

**Round**: R549 (evolution registry)
**Data**: 2026-09-21
**Status**: Implementado — testes TDD verdes
**Score**: 1.0 (gate SDD pass; regressão completa verde)

## Objetivo

Entregar ao operador um executor auditável de podcast via Gemini Notebook
(pacote `notebooklm-mcp-cli`, CLI `nlm`) como **ferramenta explícita on-demand**
— sem acoplar o pipeline automático de pesquisa. Veredito da avaliação de
produto (R548): **ADOTAR-opt-in**; upstream usa APIs internas não documentadas
+ cookies (risco de instabilidade), portanto:

1. `agent_runners/nlm_executor.py`: executor primitivo com runner injetável,
   `shell=False`, fail-closed (binário ausente / notebook fora da allowlist /
   task vazia / operação desconhecida), recibo auditável e anti-overclaim.
2. `MarceloClaroOrchestrator.podcast(folder)`: compõe as operações primitivas
   (criar notebook → adicionar fonte de `manuscrito.md` → gerar áudio →
   baixar para `folder/audio/`), retornando relatório estruturado.
3. `cli.py`: subcomando `podcast` espelhando o padrão `apresentacao`
   (pasta → JSON).

## Critérios de aceitação

- CA1: `NlmPodcastExecutor` expõe `available()`, `status()` e as operações
  `create_notebook`, `add_source_text`, `create_audio`, `download_audio`;
  chamadas usam `shell=False` e argumentos em lista.
- CA2: fail-closed — binário ausente, notebook fora da allowlist, notebook_id
  vazio e operação desconhecida NEGAM sem invocar o runner.
- CA3: erros reais (exit != 0, timeout, exceção) produzem recibo `success=False`
  com motivo; sucesso parseia `notebook_id`/`artifact_id` do JSON de saída.
- CA4: recibo é anti-overclaim (apenas exit/success/motivo/ids; nenhum mérito
  de conteúdo ou qualidade).
- CA5: `orchestrator.podcast(folder)` com executor fake injetado produz
  relatório `{ok, steps, notebook_id, artifact_id, audio}` e salva o áudio em
  `folder/audio/`.
- CA6: CLI `podcast <pasta>` chama `orchestrator.podcast` e imprime JSON;
  sem pasta imprime uso e sai.
- CA7: higiene estática — módulo executor não contém `shell=True`, nem
  `api_key`/`password`/`token`/cookie literal; nenhuma rede direta no fonte.
- CA8: regressão completa do ecossistema permanece verde.

## Validação real (R549, pós-implementação)

Teste E2E real com sessão autenticada revelou 2 bugs não capturados pelos
testes herméticos; corrigidos via TDD (4 novos testes) e revalidados:

1. **Sintaxe do download**: em `nlm` 0.11.6, `download audio` exige `-o
   <arquivo>` e **não aceita** `--profile`/`-d`. Executor corrigido; validação
   real baixou artefato existente com `md5` idêntico ao download manual
   (`ac16b28e0c207ee91ee741964899b350`, 24.681.398 bytes).
2. **Geração assíncrona**: `audio create` retorna imediatamente com o artefato
   ainda "processing" (download responde 404 por ~5-10 min). `download_audio`
   agora repete com espera (retries/wait, padrão 8×20s), fail-closed mantido
   para notebook_id vazio.

Artefatos de validação: `/tmp/opencode/producao_teste/audio/podcast_producao_teste.m4a`
(24,7 MB, deep_dive/long/pt-BR), `/tmp/opencode/download_verificado/podcast_verificado.m4a`.

## Arquivos

- `agent_runners/nlm_executor.py` (novo)
- `marceloclaro/orchestrator.py` (método `podcast`)
- `marceloclaro/cli.py` (bloco `podcast`)
- `tests/test_r549_nlm_podcast.py` (novo, hermético)
- `specs/SPEC-972-nlm-podcast-executor.md` (este)

## Fora de escopo (Fase 2+)

- Etapa automática/`--podcast` no `research/hub.py` — somente após validação
  de uso pelo operador e estabilidade do upstream.
- Re-login automático quando a sessão expira (ação humana permanece).
- Integração ao `MANIFEST.json` de publishing.