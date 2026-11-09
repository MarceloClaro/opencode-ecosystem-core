# SPEC-935-R1104 — Agentes e MCP para os recursos GJQ/Tiangong

> **Atualização R1105 (2026-11-09):** a camada foi ampliada com orientação
> `best_for`/`avoid` por backend, frescor do snapshot, `gjq_backend_drift` no
> runtime, validação de proveniência e 5 templates de experimento. O MCP
> `gjq-backend-research` passou de 9 para 12 ferramentas.

**Status:** implementação local
**Data:** 2026-11-09
**Escopo:** catálogo canônico dos recursos do serviço de computação quântica
supercondutora GJQ/Tiangong, MCP de pesquisa de backends e um agente
especialista para cada recurso listado pelo usuário.

## 1. Contexto

O Core já possui o MCP `gjq-runtime` (submissão e leitura de tarefas) e o MCP
`gjq-experiments` (E01–E18). O snapshot de recursos fornecido pelo usuário em
2026-11-09 inclui 19 recursos, além dos dois backends originalmente tratados
(`Guoji08` e `Baihua`):

- 6 recursos de hardware/emulação: Guoji No.1, Guoji No.4, Guoji No.7,
  Guoji No.8 (simulate), Baihua e Yudu;
- 4 simuladores de CPU: Jiuxiao (full amplitude), Jiuyun (noise),
  Jiuyuan (single amplitude) e Jiuci (partial amplitude);
- 4 simuladores de GPU: Qilv (full amplitude), Qijian (noise),
  Qiyao (single amplitude) e Qijing (partial amplitude);
- 1 simulador MPS;
- 4 simuladores de NPU: Liangshi (full amplitude), Weina (noise),
  Weichi (single amplitude) e Weixin (partial amplitude).

O nome exibido na interface nem sempre é o nome aceito pela API. O catálogo
separa `display_name`, `api_name` e `aliases`, e marca `api_name_verified`
apenas quando o nome aparece na documentação oficial do `gjq-client` ou já é
usado pelo Core. Nomes não verificados não são inventados: o agente deve
resolvê-los com `gjq_list_backends` antes de submeter.

## 2. Requisitos

- **R1.** Criar um registro canônico, versionado e somente leitura com os 19
  recursos, incluindo família, tipo, qubits, status, T1/T2, data de calibração,
  nome de API, aliases, restrições e notas.
- **R2.** Criar o MCP `gjq-backend-research`, sem rede e sem chave, com
  ferramentas de catálogo, resolução de nome, seleção, plano de pesquisa,
  comparação simulador/hardware, limites e template de proveniência.
- **R3.** Criar um agente de catálogo para cada um dos 19 recursos, com
  capacidade exclusiva, contrato de saída, spec e teste compartilhados.
- **R4.** Resolver aliases como `Guoji No.8 (simulate)`, `FAS-GPU`, `SAS-CPU`
  e `MPS` sem confundir simulador com hardware.
- **R5.** Manter o gate de hardware: qualquer recurso marcado como hardware ou
  emulação de hardware exige `allow_hardware=True` e `confirm=True` no MCP de
  submissão; o novo MCP não submete jobs.
- **R6.** Não aceitar API key no prompt, não gravar segredo e não exigir
  `GJQ_API_KEY` para consultar o catálogo estático.
- **R7.** Declarar os limites: snapshot não é estado ao vivo; capacidade de
  qubits não garante praticidade; counts não provam fidelidade, emaranhamento
  ou vantagem quântica.
- **R8.** Registrar a proveniência da pesquisa: backend, task ID, shots,
  timestamp, hash do QASM, versão do SDK e status.

## 3. Catálogo

| ID | Nome exibido | Família | Qubits | Status no snapshot | API provável |
|---|---|---|---:|---|---|
| `guoji-01` | Guoji No.1 | hardware | 20 | maintenance | `Guoji01` (não verificada) |
| `guoji-04` | Guoji No.4 | hardware | 100 | maintenance | `Guoji04` (não verificada) |
| `guoji-07` | Guoji No.7 | hardware | 100 | maintenance | `Guoji07` (não verificada) |
| `guoji-08-sim` | Guoji No.8 (simulate) | hardware/emulação | 20 | online | `Guoji08` |
| `baihua` | Baihua | hardware | 156 | online | `Baihua` |
| `yudu` | Yudu | hardware | 72 | maintenance | `Yudu` (não verificada) |
| `jiuxiao-fas-cpu` | Jiuxiao-Full Amplitude Simulator | cpu | 20 | online | `FAS-CPU` |
| `jiuyun-noise-cpu` | Jiuyun-Noise Simulator | cpu | 20 | online | não verificada |
| `jiuyuan-sas-cpu` | Jiuyuan-Single Amplitude Simulator | cpu | 200 | online | `SAS-CPU` |
| `jiuci-pas-cpu` | Jiuci-Partial Amplitude Simulator | cpu | 20 | online | não verificada |
| `qilv-fas-gpu` | Qilv-Full Amplitude Simulator | gpu | 29 | online | `FAS-GPU` |
| `qijian-noise-gpu` | Qijian-Noise Simulator | gpu | 29 | online | não verificada |
| `qiyao-sas-gpu` | Qiyao-Single Amplitude Simulator | gpu | 29 | online | `SAS-GPU` |
| `qijing-pas-gpu` | Qijing-Partial Amplitude Simulator | gpu | 29 | online | não verificada |
| `mps` | MPS Simulator | mps | 997 | online | `MPS` |
| `liangshi-fas-npu` | Liangshi-Full Amplitude Simulator | npu | 10 | online | não verificada |
| `weina-noise-npu` | Weina-Noise Simulator | npu | 10 | online | não verificada |
| `weichi-sas-npu` | Weichi-Single Amplitude Simulator | npu | 10 | online | não verificada |
| `weixin-pas-npu` | Weixin-Partial Amplitude Simulator | npu | 10 | online | não verificada |

**Snapshot:** `https://www.tiangongqs.com/cloud/server`, informado pelo usuário
em 2026-11-09. O snapshot não foi obtido por automação autenticada e não
substitui `gjq_list_backends`.

## 4. MCP `gjq-backend-research`

Ferramentas somente leitura, sem `GJQ_API_KEY` e sem submissão:

| Ferramenta | Função |
|---|---|
| `gjq_backend_catalog` | catálogo completo, com filtros por família |
| `gjq_backend_snapshot` | contagens por família/status e data do snapshot |
| `gjq_resolve_backend` | resolve ID, nome exibido, API ou alias |
| `gjq_select_backend` | seleciona por família, qubits e status |
| `gjq_research_plan` | recomenda backend e protocolo para um objetivo |
| `gjq_compare_plan` | plano simulador versus hardware |
| `gjq_backend_limits` | limites por família e restrições |
| `gjq_provenance_template` | campos obrigatórios de proveniência |
| `gjq_calibration_snapshot` | T1/T2 do snapshot, com aviso de validade |

O MCP não substitui `gjq-runtime`: para estado ao vivo, listar backends e
submeter, use o MCP `gjq-runtime`, com `confirm=True` e `allow_hardware=True`
quando aplicável.

## 5. Agentes

Um card por recurso, em `agents/catalog/gjq-backend-<id>.md`, com:

- `agent_id` igual ao nome do arquivo;
- capacidade exclusiva `profile_gjq_backend_<id_com_underscores>`;
- tags de família (`gjq_hardware`, `gjq_cpu`, `gjq_gpu`, `gjq_mps`, `gjq_npu`);
- spec e teste compartilhados (`SPEC-935-R1104` e
  `tests/test_r1104_gjq_backend_agents.py`);
- instrução para resolver o nome vivo, não confundir simulador com hardware e
  não declarar fidelidade sem evidência.

## 6. Aceitação

- registro com 19 recursos e nenhum ID duplicado;
- 6 hardware/emulação, 4 CPU, 4 GPU, 1 MPS e 4 NPU;
- resolução de `Guoji No.8 (simulate)`, `FAS-GPU`, `SAS-CPU` e `MPS`;
- MCP com as 9 ferramentas e `executed=False`/`network_access=False` no status;
- 19 cards válidos pelo `AgentLifecycleService.validate`;
- nenhum segredo nos cards, no registro, no MCP ou nos testes;
- testes R1104 passando e `opencode.json` regenerado.

## 7. Não objetivos

- Não submeter jobs, não consumir hardware e não testar a nuvem nesta spec.
- Não declarar que os nomes não verificados são os nomes reais da API.
- Não elevar a confiança do catálogo por uma execução local.
- Não substituir a revisão científica ou o peer review do livro.
