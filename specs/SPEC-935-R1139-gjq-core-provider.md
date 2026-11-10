# SPEC-935-R1139 — Provider GJQ de primeira classe

**Status:** implementação local; nenhum hardware executado
**Data:** 2026-11-10
**Componente:** `integrations/gjq_core_provider.py`

## 1. Objetivo

Unificar a integração GJQ ↔ Core em um provider com:

- credencial por `GJQ_API_KEY` ou conta cacheada;
- gates `confirm`/`allow_hardware`;
- orçamento local e ledger;
- execução via `gjq-client`;
- hash do QASM, task ID e timestamp;
- status/resultado/auditoria;
- auditoria local de compilação/layout.

## 2. MCP

Ferramentas em `gjq-runtime`:

- `gjq_provider_status` (local);
- `gjq_provider_submit` (rede, gates);
- `gjq_provider_result` (rede);
- `gjq_provider_compilation` (rede, sem submissão).

As ferramentas legadas permanecem para compatibilidade.

## 3. Requisitos

- **R1.** `status` sem rede e sem chave na saída.
- **R2.** `submit` bloqueia sem confirmação/credencial/hardware/Orçamento.
- **R3.** `submit` registra `task_id`, `qasm_sha256`, budget e timestamp.
- **R4.** `result` não reenvia job e audita counts.
- **R5.** `compilation_audit` verifica layout/qubits ativos/QASM.
- **R6.** Testes com mocks, sem rede/hardware.
- **R7.** Documentação, skill e harness atualizados.

## 4. Critérios

- `status` reporta SDK, credencial, budget, registry e `network_access=False`;
- submissão sem `confirm=True` bloqueia;
- hardware sem `allow_hardware=True` bloqueia;
- orçamento bloqueado retorna antes da rede;
- caminho de sucesso mockado devolve `task_id` e hash de 64 hex;
- MCP registra as quatro ferramentas;
- `compilation_audit` preserva 106/107 e detecta troca;
- nenhum segredo em arquivo/log.

## 5. Limites

O servidor não devolve layout; `compile=False` não foi testado. O orçamento é
local, não preço oficial. Uma submissão não prova fidelidade ou vantagem.
