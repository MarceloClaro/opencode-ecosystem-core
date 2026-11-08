---
name: gjq-pesquisa-quantica
description: Conduz pesquisa quântica na plataforma GJQ/CETC-ICQ com gjq-client 0.2.1, Qiskit 2.3, sampling, estimativa, MPS, sessões, task IDs e auditoria de counts. Use para circuitos de pesquisa; exige confirm=True, bloqueia hardware sem allow_hardware=True e nunca expõe API key.
metadata:
  version: "1"
  origem: "R1099 — integração GJQ para pesquisa quântica"
---

# Pesquisa quântica na GJQ

## Quando usar

- Circuitos de pesquisa que não são E01–E18.
- Descoberta de backends e escolha de simulador ou hardware.
- Sampling, estimativa de valor esperado, MPS e sessões.
- Recuperação de task ID, status, resultado e proveniência.

Para E01–E18, use a skill `gjq-experimentos-quanticos` e o MCP
`gjq-experiments`, que exigem simulação local antes do hardware.

## Pré-requisitos

- Python 3.12 ou superior.
- `gjq-client==0.2.1`.
- Qiskit 2.3.0.
- `GJQ_API_KEY` no ambiente, nunca no prompt.

```bash
python3 -m venv .venv-quantum
.venv-quantum/bin/pip install 'gjq-client==0.2.1' 'qiskit==2.3.0'
export GJQ_API_KEY="sua-chave"
.venv-quantum/bin/python -c "import gjq_client; print(gjq_client.__version__)"
```

A chave é cacheada pelo SDK em `~/.gjq_client/gjq_client_account.json`.
Proteja o arquivo com `chmod 600` e nunca o versione.

## Backends documentados

| Backend | Tipo | Qubits | Uso |
|---|---|---:|---|
| `FAS-CPU` | simulador full-amplitude CPU | 20 | validação rápida |
| `FAS-GPU` | simulador full-amplitude GPU | 32 | circuitos maiores |
| `SAS-CPU` | simulador single-amplitude CPU | 200 | uma amplitude; exige `amplitude_index` |
| `SAS-GPU` | simulador single-amplitude GPU | 32 | uma amplitude; exige `amplitude_index` |
| `MPS` | tensor network GPU | 1000 | escala; exige `simulator_config` |
| `Baihua` | hardware supercondutor | 156 | hardware; custo e fila |
| `Guoji08` | hardware supercondutor | 20 | hardware; sessões |

A disponibilidade e a fila mudam. Sempre consulte `gjq_list_backends` antes de
escolher. `gjq_least_busy` pode retornar simulador.

## Fluxo

1. `gjq_runtime_status` — confirme SDK, chave e limites.
2. `gjq_list_backends` — escolha o backend pelo tipo e pelo tamanho.
3. `gjq_backend_config` e `gjq_backend_properties` — portas, acoplamentos e calibração.
4. Monte o OpenQASM 2.0 com medições para sampling.
5. `gjq_sample` ou `gjq_estimate` com `confirm=True`.
6. Guarde o `task_id`.
7. `gjq_task_status` até `DONE`, `ERROR` ou `CANCELLED`.
8. `gjq_task_result` — counts ou valores esperados.
9. `gjq_task_detail` — backend, shots e horário.
10. `gjq_audit_counts` — confira a soma e o erro padrão.

Não faça polling apertado. Consulte a cada poucos segundos e reutilize o
`task_id`; não reenvie o mesmo circuito.

## Ferramentas do MCP `gjq-runtime`

| Ferramenta | Efeito |
|---|---|
| `gjq_runtime_status` | local; versão, chave e limites |
| `gjq_list_backends` | rede; lista dispositivos |
| `gjq_least_busy` | rede; menor fila |
| `gjq_backend_config` | rede; configuração estática |
| `gjq_backend_properties` | rede; calibração |
| `gjq_sample` | submete sampling; `confirm=True` |
| `gjq_estimate` | submete estimativa; `confirm=True` |
| `gjq_task_status` | status não bloqueante |
| `gjq_task_result` | resultado e auditoria de counts |
| `gjq_task_detail` | detalhes da tarefa |
| `gjq_list_tasks` | tarefas ativas |
| `gjq_audit_counts` | local; soma, probabilidades e erro padrão |

## Gates de segurança

- `confirm=True` é obrigatório em `gjq_sample` e `gjq_estimate`.
- `Guoji08` e `Baihua` exigem `allow_hardware=True` e aprovação de custo.
- `GJQ_MAX_SHOTS` limita shots; padrão 100.000.
- `GJQ_MAX_SUBMISSIONS_PER_SESSION` limita submissões; padrão 20.
- A chave vem só de `GJQ_API_KEY`; não há ferramenta para digitá-la no prompt.
- Não publique task ID com dado pessoal.
- Menor de idade usa conta do responsável.

## Proveniência

Registre por tarefa:

- `task_id`;
- backend e tipo (simulador/hardware);
- shots;
- timestamp;
- hash SHA-256 do QASM;
- versão do `gjq-client` e do Qiskit;
- status final;
- counts ou valores esperados;
- auditoria da soma.

## Exemplo: Bell state no FAS-CPU

```text
gjq_list_backends()
gjq_sample(qasm=BELL, backend_name="FAS-CPU", shots=1024, confirm=True)
gjq_task_status(task_id="...")
gjq_task_result(task_id="...")
gjq_audit_counts(counts={...}, shots=1024)
```

## Exemplo: CHSH

Prepare quatro circuitos, um por par de bases, e submeta cada um com
`confirm=True`. Calcule `E = (N00 + N11 - N01 - N10) / shots` e
`S = E00 + E01 + E10 - E11`. Em hardware, `S` pode ficar abaixo de `2√2`;
declare violação somente se o intervalo experimental sustentar `|S| > 2`.

## Limites

- Simulação ou uma execução não provam fidelidade, emaranhamento, vantagem
  quântica ou interpretação de Bohm.
- MPS acima de 200 qubits exige o SDK diretamente; o MCP limita a 200 qubits.
- O servidor oficial `gjq-runtime-mcp-server` não é usado: ele chama
  `Estimator.run(..., obs=...)` e `task_result(..., obs=...)`, assinaturas
  incompatíveis com `gjq-client 0.2.1`, e não exige `confirm=True`.
- A documentação da plataforma pode mudar; consulte os links oficiais.

## Documentação

- <https://tiangongqs.com/docs/quantum/QuantumProgrammingFramework.html>
- <https://tiangongqs.com/docs/quantum/ProgrammingQuantumCircuits.html>
- <https://tiangongqs.com/docs/quantum/JupyterNotebookUserGuide.html>
- <https://github.com/guoji-quantum/gjq_client>
- <https://github.com/guoji-quantum/gjq-runtime-mcp-server>
