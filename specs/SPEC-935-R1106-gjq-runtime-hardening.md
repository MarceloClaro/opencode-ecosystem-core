# SPEC-935-R1106 — Endurecimento do runtime GJQ

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** SPEC-935-R1104, SPEC-935-R1105

## 1. Contexto

A camada R1105 tem catálogo, orientação, drift e templates, mas quatro lacunas
permanecem:

1. `gjq_backend_config`, `gjq_backend_properties`, `gjq_list_backends` e
   `gjq_least_busy` consultam a nuvem em toda chamada, sem cache com validade.
2. Não há orçamento diário por operador, nem um gate global de hardware
   separado do `allow_hardware` por chamada.
3. O drift detecta divergência, mas não grava um snapshot verificado com data,
   hash e comparação.
4. Nenhum job real foi executado; falta um teste de fumaça *gated*, capaz de
   provar a execução quando o operador autorizar, sem rodar por acidente.

## 2. Fontes consultadas

- IBM Quantum, `SamplerOptions`: `max_execution_time`, `default_shots` e opções
  de execução — <https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/options-sampler-options>
- IBM Quantum, opções de V2 primitives — <https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/options>
- Qiskit, fake providers para testes sem hardware —
  <https://github.com/Qiskit/qiskit/tree/main/qiskit/providers/fake_provider>
- cachetools, `TTLCache` — <https://cachetools.readthedocs.io/en/latest/>
- `gjq-client` 0.2.1 e README do MCP oficial —
  <https://pypi.org/project/gjq-client/>,
  <https://github.com/guoji-quantum/gjq-runtime-mcp-server>
- MCP Python SDK/FastMCP: cliente em memória e `_tool_manager` já usados nos
  testes R1099/R1104/R1105.

A busca web do ambiente retornou HTTP 402; as fontes acima foram consultadas
diretamente por GitHub/raw e documentação oficial.

## 3. Requisitos

### R1 — Cache TTL

- `TTLCache` local, thread-safe, com `maxsize`, TTL por chave e relógio
  injetável.
- `gjq_list_backends`: TTL 30 s.
- `gjq_least_busy`: TTL 15 s.
- `gjq_backend_config`: TTL 3600 s.
- `gjq_backend_properties`: TTL 300 s.
- `GJQ_CACHE_TTL_SECONDS` ajusta o TTL padrão.
- `force_refresh=True` ignora o cache.
- A resposta inclui `cache: {hit, age_seconds, ttl_seconds, expires_in}`.
- Não cachear `gjq_task_status`, `gjq_task_result`, `gjq_task_detail` nem
  `gjq_backend_drift`.
- O cache não armazena API key, QASM, counts ou resultado de job.

### R2 — Orçamento e gate de hardware

- `GJQ_HARDWARE_ENABLED` default `false`; hardware/emulação exige o valor
  `1/true/yes` **e** `allow_hardware=True`.
- Limites diários por operador:
  - `GJQ_DAILY_SUBMISSIONS` (default 20);
  - `GJQ_DAILY_HARDWARE_SUBMISSIONS` (default 1);
  - `GJQ_DAILY_SHOTS` (default 100000);
  - `GJQ_DAILY_HARDWARE_SHOTS` (default 4096).
- Ledger local JSONL em `GJQ_BUDGET_LEDGER` ou
  `~/.gjq_client/core_budget_ledger.jsonl`, com permissão 600.
- `gjq_budget_status` informa data, limites, uso, restante, gate de hardware e
  caminho do ledger.
- `gjq_sample`/`gjq_estimate` checam o orçamento antes de chamar o serviço e
  registram a submissão bem-sucedida. Se o registro falhar, o `task_id` é
  preservado e a resposta avisa.
- Não inventar preço em moeda: o orçamento é em submissões e shots.

### R3 — Snapshot verificado

- `build_verified_snapshot(live_backends)` produz:
  - `generated_at`, `source`, `registry_sha256`, `snapshot_sha256`;
  - `entries` com `registry_id`, `live_name`, `api_name`,
    `api_name_verified`;
  - `missing_in_registry`, `missing_live`, `ambiguous`.
- `scripts/gjq_verified_snapshot.py`:
  - `--from-json` monta snapshot offline;
  - `--write` grava com escrita atômica;
  - `--check` compara o snapshot gravado com a lista atual e sai com código 1
    em drift;
  - sem chave e sem `--from-json`, retorna bloqueado, sem imprimir segredo.
- `compare_snapshot` detecta added/removed/renamed e mudança de API name.
- O snapshot não promove confiança científica; é proveniência operacional.

### R4 — Teste de execução real

- Teste `tests/test_r1106_gjq_runtime_hardening.py` com bloco *gated*:
  - só roda com `GJQ_REAL_EXECUTION=1` **e** `GJQ_API_KEY`;
  - backend padrão `FAS-CPU`; hardware é recusado pelo teste;
  - Bell, 128 shots (máximo 1024), `confirm=True`, `allow_hardware=False`;
  - captura `task_id`, faz polling limitado e audita counts;
  - se ficar `RUNNING` além do prazo, `skip` com o `task_id`, não `fail`;
  - não grava chave nem resultado bruto com dado pessoal.
- Um teste unitário sempre roda e prova que o gate exige as duas variáveis.

## 4. Aceitação

- cache: hit/miss/expiração/force_refresh testados com relógio falso;
- orçamento: ledger temporário, limites, hardware desabilitado, shots e
  submissões testados;
- snapshot: build/write/read/compare e hash determinístico testados;
- execução real: teste gated presente e pulado sem as duas variáveis;
- R1099/R1104/R1105 continuam passando;
- `opencode.json` e docs atualizados;
- nenhum segredo no diff.

## 5. Não objetivos

- Não executar hardware nesta rodada.
- Não definir preço monetário da GJQ.
- Não substituir a política de custo do provedor.
- Não elevar confiança por um teste local.
