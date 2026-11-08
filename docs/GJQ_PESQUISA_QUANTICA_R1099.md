# GJQ para pesquisa quântica — R1099

**Data:** 2026-11-08
**Escopo:** instalação e auditoria da pilha GJQ/CETC-ICQ no Core, com MCPs, agente e skill para experimentos e pesquisa quântica.
**Fontes oficiais consultadas:**

- <https://tiangongqs.com/docs/quantum/QuantumProgrammingFramework.html>
- <https://tiangongqs.com/docs/quantum/ProgrammingQuantumCircuits.html>
- <https://tiangongqs.com/docs/quantum/JupyterNotebookUserGuide.html>
- <https://github.com/guoji-quantum/gjq_client>
- <https://github.com/guoji-quantum/gjq-runtime-mcp-server>
- <https://github.com/guoji-quantum/industry_solution>

## 1. Versões fixadas

| Componente | Versão | Observação |
|---|---|---|
| Python | >= 3.12 | exigência do `gjq-client` |
| `gjq-client` | 0.2.1 | SDK oficial; PyPI é a referência |
| Qiskit | 2.3.0 | dependência fixa do SDK |
| `qiskit-ibm-runtime` | 0.45.0 | dependência do SDK |
| `fastmcp` | >= 2, < 4 | usado apenas na auditoria do servidor oficial |
| MCP do Core | `mcp` 1.x | usado pelo wrapper nativo |

O fork <https://github.com/MarceloClaro/gjq_client> está em
`1aa4621ad1964c9122aeb6403525af82d3b30f27`, com `0.2.1.post1` e Apache-2.0.
Ele espelha o repositório oficial; a instalação recomendada é pelo PyPI,
`gjq-client==0.2.1`, porque o próprio guia avisa que GitHub e PyPI podem diferir.

## 2. Backends documentados

| Backend | Tipo | Qubits | Modo | Uso |
|---|---|---:|---|---|
| `FAS-CPU` | simulador full-amplitude CPU | 20 | job | validação rápida |
| `FAS-GPU` | simulador full-amplitude GPU | 32 | job | circuitos maiores |
| `SAS-CPU` | simulador single-amplitude CPU | 200 | job | uma amplitude; exige `amplitude_index` |
| `SAS-GPU` | simulador single-amplitude GPU | 32 | job | uma amplitude; exige `amplitude_index` |
| `MPS` | tensor network GPU | 1000 | job | escala; exige `simulator_config` |
| `Baihua` | hardware supercondutor | 156 | job | hardware; custo e fila |
| `Guoji08` | hardware supercondutor | 20 | job, session | hardware; sessões |

A disponibilidade, a fila e a calibração mudam. `least_busy` pode retornar
simulador; confirme o tipo antes de assumir hardware.

## 3. Dois MCPs, dois escopos

| MCP | Ferramentas | Escopo | Gate |
|---|---:|---|---|
| `gjq-experiments` | 7 | executa E01–E18 pelo script canônico | simulação local antes do hardware; `confirm=True`; chave no ambiente |
| `gjq-runtime` | 12 | pesquisa livre: backends, sampling, estimativa, tarefas | `confirm=True`; hardware só com `allow_hardware=True`; chave no ambiente |

### `gjq-experiments`

Mantido para a trilha do livro. Ferramentas: `gjq_status`, `gjq_catalog`,
`gjq_prepare`, `gjq_sim`, `gjq_run`, `gjq_result`, `gjq_audit`. O `gjq_run`
retorna `blocked` sem chave ou sem JSON simulado.

### `gjq-runtime`

Implementado em `integrations/gjq_runtime_mcp.py`. Ferramentas:

| Ferramenta | Efeito |
|---|---|
| `gjq_runtime_status` | local; SDK, chave e limites |
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

Limites: 200 qubits, 100.000 shots, 50.000 caracteres de QASM e 20 submissões
por processo. O wrapper não aceita API key como argumento, não executa código
arbitrário, não usa shell e mantém stdout limpo para o transporte stdio.

## 4. Auditoria do servidor oficial `gjq-runtime-mcp-server`

Fork auditado: `MarceloClaro/gjq-runtime-mcp-server`, commit
`8989745852a36faa0348ed142df4f3b2a3ea8560`, Apache-2.0.

**O que foi verificado:**

- 12 ferramentas e testes no repositório.
- Em venv isolado com `gjq-client==0.2.1`, `fastmcp 3.4.11` e Qiskit 2.3.0:
  **23 testes passaram, 1 foi pulado**.
- O código usa `asyncio.to_thread` para não bloquear o event loop.
- Há limites `GJQ_MAX_SHOTS` (100.000) e
  `GJQ_MAX_SUBMISSIONS_PER_SESSION` (20).

**Defeitos encontrados:**

1. `Estimator.run(..., obs=obs)` — a assinatura real do SDK 0.2.1 é
   `Estimator.run(..., observable=...)`. A chamada falha em runtime.
2. `service.task_result(task_id, obs=obs)` — a assinatura real é
   `task_result(task_id, observable=...)`. A chamada falha em runtime.
3. Os testes passam porque usam mocks; não exercitam a assinatura real.
4. Não há `confirm=True`: `sample_tool` e `estimate_tool` submetem direto.
5. `task_log` depende de `service._client`, API privada.
6. O `pyproject` fixa `gjq-client>=0.1.2,<0.2`, mas o SDK atual é 0.2.1.

**Decisão:** não registrar o servidor oficial. O `gjq-runtime` do Core corrige
as assinaturas e adiciona os gates. O fork permanece como referência e o
`gjq-client` oficial é a dependência.

## 5. `industry_solution`

Fork: `MarceloClaro/industry_solution`, commit
`5b8cc4c96032d25e83f4aa0506d904341d9702fe`. O repositório contém apenas
`README.md` com a descrição “guoji quantum industry solution open source
repository”. Não há código, dados ou casos executáveis. **Decisão: referência
institucional; não integrar.**

## 6. Agente e skill

| Item | Arquivo | Função |
|---|---|---|
| Agente | `agents/catalog/gjq-quantum-research.md` | projeta e conduz pesquisa; exige confirmação e controle de custo |
| Skill | `.opencode/skills/gjq-pesquisa-quantica/SKILL.md` | fluxo, backends, ferramentas, proveniência e limites |
| Skill existente | `.opencode/skills/gjq-experimentos-quanticos/SKILL.md` | E01–E18 e simulação prévia |

O agente não aceita API key no prompt, não declara fidelidade ou vantagem
quântica sem evidência e diferencia simulador de hardware.

## 7. Proveniência de pesquisa

Registre por tarefa:

- `task_id`;
- backend e tipo;
- shots;
- timestamp;
- SHA-256 do QASM;
- versão de `gjq-client` e Qiskit;
- status final;
- counts ou valores esperados;
- auditoria da soma e erro padrão.

## 8. Testes

```bash
.venv/bin/python -m pytest tests/test_r1099_livro_quantico_package.py -q
.venv-quantum/bin/python -m pytest tests/test_r1099_gjq_runtime_mcp.py -q
.venv-quantum/bin/python -m pytest tests/test_r1099_quantum_simulator_mcp.py -q
```

O handshake MCP stdio do `gjq-runtime` foi verificado com 12 ferramentas. Sem
`GJQ_API_KEY`, `gjq_list_backends` e `gjq_sample` retornam `blocked`; nenhum job
foi submetido nesta sessão.

## 9. Limites

- Não houve execução real na GJQ: a chave não está no ambiente.
- Não houve validação de fidelidade, calibração ou vantagem quântica.
- O cache do SDK em `~/.gjq_client/gjq_client_account.json` deve ser protegido
  com `chmod 600` e nunca versionado.
- O MCP limita a 200 qubits; MPS acima disso exige o SDK diretamente.
- A documentação da plataforma pode mudar; consulte os links oficiais.
