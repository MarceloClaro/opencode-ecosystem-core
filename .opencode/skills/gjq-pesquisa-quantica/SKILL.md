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

## Catálogo de backends (R1104)

O catálogo canônico tem **19 recursos** no snapshot de 2026-11-09. Use o MCP
`gjq-backend-research` (`gjq_backend_catalog`, `gjq_resolve_backend`,
`gjq_research_plan`) para ver a lista completa, resolver aliases e montar o
plano. Resumo por família:

| Família | Recursos | Exemplos de API | Gate |
|---|---|---|---|
| hardware/emulação | Guoji No.1/4/7/8, Baihua, Yudu | `Guoji08`, `Baihua` | `allow_hardware=True` |
| CPU | Jiuxiao, Jiuyun, Jiuyuan, Jiuci | `FAS-CPU`, `SAS-CPU` | simulador |
| GPU | Qilv, Qijian, Qiyao, Qijing | `FAS-GPU`, `SAS-GPU` | simulador |
| MPS | MPS | `MPS` | `simulator_config` |
| NPU | Liangshi, Weina, Weichi, Weixin | nomes a confirmar | simulador |

A disponibilidade e a fila mudam. Sempre consulte `gjq_list_backends` antes de
escolher. `gjq_least_busy` pode retornar simulador. O nome exibido na UI pode
não ser o nome da API; confirme antes de submeter.

> **Guoji08:** a UI de 2026-11-09 mostra `Guoji No.8 (simulate)`. O gate trata
> como emulação de hardware e continua exigindo `allow_hardware=True`; resultados
> históricos devem ser lidos com a data e a calibração da época.

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

## MCP `gjq-backend-research`

Somente leitura, sem chave e sem rede. Ferramentas: `gjq_backend_catalog`,
`gjq_backend_snapshot`, `gjq_resolve_backend`, `gjq_select_backend`,
`gjq_research_plan`, `gjq_compare_plan`, `gjq_backend_limits`,
`gjq_provenance_template` e `gjq_calibration_snapshot`. Use-o antes do runtime
para escolher o backend, evitar single-amplitude por engano e preencher a
proveniência. Ele não lista fila ao vivo nem submete jobs.

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
- Hardware/emulação (Guoji01/04/07/08, Baihua e Yudu) exige `allow_hardware=True` e aprovação de custo.
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
- MPS tem 997 qubits de capacidade, mas o MCP limita a 200 por padrão; elevar `GJQ_MAX_QUBITS` exige revisão explícita.
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
- [Backends R1104](../../../docs/GJQ_BACKENDS_R1104.md)
