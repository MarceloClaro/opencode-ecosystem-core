# Integração GJQ ↔ OpenCode Ecosystem Core

**Status:** provider e MCP integrados localmente; nenhum hardware executado.
**Provider:** `integrations/gjq_core_provider.py`
**MCP:** servidor `gjq-runtime` (`integrations/gjq_runtime_mcp.py`)

## 1. Arquitetura

```
Core / agentes
  ├─ MCP gjq-runtime
  │   ├─ tools legadas: gjq_sample, gjq_estimate, gjq_task_*
  │   └─ tools do provider: gjq_provider_status/submit/result/compilation
  ├─ gjq_core_provider
  │   ├─ credencial (env ou conta cacheada)
  │   ├─ backend registry + snapshot
  │   ├─ budget local (JSONL, 600)
  │   ├─ execution/submission_gate
  │   └─ compilation_audit
  └─ harnesses/gjq-hardware-optimizers
      └─ runner.py + provider
```

## 2. Ferramentas do provider

| Ferramenta | Efeito | Rede |
|---|---|---|
| `gjq_provider_status` | SDK, credencial, budget, registry | não |
| `gjq_provider_submit` | valida gates/budget e submete | sim |
| `gjq_provider_result` | status/resultado/auditoria | sim |
| `gjq_provider_compilation` | audita `initial_layout`/qubits ativos | sim (Target) |
| `gjq_research_status` | catálogo E01–E18, agentes e readiness | não |
| `gjq_research_plan` | fases/gates/roteamento de pesquisa | não |

`gjq_provider_submit` exige `confirm=True`; hardware exige
`allow_hardware=True` e `GJQ_HARDWARE_ENABLED=1`. A credencial pode vir de
`GJQ_API_KEY` ou de `use_cached_account=True`; a chave nunca aparece na saída.

## 3. Fluxo operacional

1. `gjq_provider_status` — não abre rede; mostra se há chave/conta cacheada,
   limites e hash do registry.
2. `gjq_provider_compilation` — lê o Target e audita se `initial_layout`
   preserva 106/107 e se o QASM mantém `qreg q[108]`.
3. `gjq_provider_submit` — aplica gates, orçamento, transpilação opcional
   (`initial_layout` explícito), aceita `compile=False`, submete e registra
   `task_id`, `qasm_sha256`, layout final e timestamp no ledger.
4. `gjq_provider_result` — consulta status; se final, lê counts e audita a soma.
5. Não reenviar o mesmo QASM; usar o `task_id`.

## 4. Orçamento e gates

- limites locais: `GJQ_DAILY_SUBMISSIONS`, `GJQ_DAILY_HARDWARE_SUBMISSIONS`,
  `GJQ_DAILY_SHOTS`, `GJQ_DAILY_HARDWARE_SHOTS`;
- ledger: `~/.gjq_client/core_budget_ledger.jsonl`, permissão 600;
- hardware: desabilitado por padrão; exige `GJQ_HARDWARE_ENABLED=1`;
- `confirm=True` e `allow_hardware=True` são gates independentes.

O orçamento é local; não representa preço oficial da Tiangong.

## 5. Proveniência

Cada submissão devolve:

- `task_id`, backend, shots, hardware;
- `qasm_sha256` do QASM efetivamente submetido;
- `cached_account` (bool), `transpile`, `optimization_level`;
- `budget_after` e timestamp.

O registry tem hash SHA-256 (`gjq_verified_snapshot.registry_sha256`). O
snapshot de backends é proveniência operacional, não prova de disponibilidade
futura.

## 6. REA e o SDK

- REA 6.8.0, 229 ferramentas; camada `native_offline_elf` pronta.
- `runtime.abi3.so` sha256
  `63ac97333a56701fe29a83ed3600c7ab4f7ccb96807b35d58cfd8a3862859a1a`;
  `inspect_binary_layout` entregou Evidence ELF
  `ev_01bb709fa90826e02ccf154b1caa14c1dbf69c018cbabb711eefaa7359ccf25d`
  (resposta `6742f02ca21135c002ed68148b466a30729ac75b804f33f15b9a317d0c1140f0`).
- A análise nativa via Ghidra não entregou Evidence utilizável; a leitura do
  SDK foi a evidência primária.
- Achados: o sampler envia `qasm2.dumps(circuit)`; `measure-position` é
  removido para não-MPS; o servidor compila e não devolve layout.
- `compilation_audit` audita localmente `initial_layout`, QASM e qubits ativos.
- Teste controlado `compile=False` (R1140): pré-registro de 1 job/4.096 shots;
  bloqueado antes da submissão por `APIError: Failed to fetch machine config
  for Baihua`; **nenhum task ID foi criado**. Ver
  `docs/TESTE_COMPILE_FALSE_R1140.md`.

## 7. Limites

- Nenhum job foi submetido nesta integração.
- O layout físico do servidor não é devolvido pelo SDK.
- A auditoria de compilação usa Target genérico nos testes; para o Baihua,
  passar o Target real.
- Um `task_id` não prova fidelidade, emaranhamento ou vantagem quântica.
- O provider não substitui SDD/TDD, revisão humana ou validação externa.

## 8. Reprodução

```bash
.venv-quantum/bin/python -m pytest tests/test_r1099_gjq_runtime_mcp.py \
  tests/test_r1139_gjq_core_provider.py tests/test_r1137_compilation_audit.py -q
```

Via MCP: `gjq_provider_status`, `gjq_provider_submit`, `gjq_provider_result`,
`gjq_provider_compilation`, `gjq_research_status`, `gjq_research_plan`.

Framework de pesquisa: `docs/GJQ_RESEARCH_FRAMEWORK.md`.
Domínios `classification` e `cooking`: `quantum_research/` e dossiê
`docs/LITERATURA_CLASSIFICACAO_COZIMENTO_R1142.md`.
