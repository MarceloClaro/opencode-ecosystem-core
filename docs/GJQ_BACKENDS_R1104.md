# Backends GJQ/Tiangong — R1104

**Data do snapshot:** 2026-11-09
**Fonte informada:** <https://www.tiangongqs.com/cloud/server>
**Natureza:** snapshot fornecido pelo usuário; não foi obtido por automação
autenticada. Status, fila e calibração mudam. Para o estado ao vivo, use
`gjq_list_backends` no MCP `gjq-runtime`.

## 1. Por que esta camada existe

O Core já tinha dois backends no gate (`Guoji08` e `Baihua`) e sete nomes na
documentação. O snapshot atual lista **19 recursos**. Sem um registro canônico,
o agente pode:

- confundir o rótulo da interface com o nome da API;
- tratar simulador como hardware;
- recomendar single-amplitude para um sampling geral;
- prometer 997 qubits do MPS sem considerar `simulator_config` e depth;
- repetir a alegação de que `Guoji08` é hardware quando a UI mostra
  `(simulate)`.

A camada R1104 resolve isso com um registro estático, um MCP somente leitura e
19 agentes especialistas.

## 2. Catálogo

| ID | Nome exibido | Família | Qubits | Status | API | Verificado |
|---|---|---|---:|---|---|---|
| `guoji-01` | Guoji No.1 | hardware | 20 | maintenance | `Guoji01` | não |
| `guoji-04` | Guoji No.4 | hardware | 100 | maintenance | `Guoji04` | não |
| `guoji-07` | Guoji No.7 | hardware | 100 | maintenance | `Guoji07` | não |
| `guoji-08-sim` | Guoji No.8 (simulate) | hardware/emulação | 20 | online | `Guoji08` | sim |
| `baihua` | Baihua | hardware | 156 | online | `Baihua` | sim |
| `yudu` | Yudu | hardware | 72 | maintenance | `Yudu` | não |
| `jiuxiao-fas-cpu` | Jiuxiao-Full Amplitude Simulator | cpu | 20 | online | `FAS-CPU` | sim |
| `jiuyun-noise-cpu` | Jiuyun-Noise Simulator | cpu | 20 | online | — | não |
| `jiuyuan-sas-cpu` | Jiuyuan-Single Amplitude Simulator | cpu | 200 | online | `SAS-CPU` | sim |
| `jiuci-pas-cpu` | Jiuci-Partial Amplitude Simulator | cpu | 20 | online | — | não |
| `qilv-fas-gpu` | Qilv-Full Amplitude Simulator | gpu | 29 | online | `FAS-GPU` | sim |
| `qijian-noise-gpu` | Qijian-Noise Simulator | gpu | 29 | online | — | não |
| `qiyao-sas-gpu` | Qiyao-Single Amplitude Simulator | gpu | 29 | online | `SAS-GPU` | sim |
| `qijing-pas-gpu` | Qijing-Partial Amplitude Simulator | gpu | 29 | online | — | não |
| `mps` | MPS Simulator | mps | 997 | online | `MPS` | sim |
| `liangshi-fas-npu` | Liangshi-Full Amplitude Simulator | npu | 10 | online | — | não |
| `weina-noise-npu` | Weina-Noise Simulator | npu | 10 | online | — | não |
| `weichi-sas-npu` | Weichi-Single Amplitude Simulator | npu | 10 | online | — | não |
| `weixin-pas-npu` | Weixin-Partial Amplitude Simulator | npu | 10 | online | — | não |

“Verificado” significa que o nome aparece na documentação oficial do
`gjq-client`/Core. Nomes não verificados não são inventados: o agente deve
confirmá-los com `gjq_list_backends` antes de submeter.

### Guoji08

A UI de 2026-11-09 mostra `Guoji No.8 (simulate)`. O card e o gate tratam esse
recurso como **emulação de hardware** e continuam exigindo
`allow_hardware=True` por precaução. Resultados históricos rotulados `Guoji08`
devem ser lidos com a data e a calibração da época; não os reclassifique
silenciosamente.

## 3. MCP `gjq-backend-research`

Servidor local, somente leitura, sem chave e sem rede:

| Ferramenta | Função |
|---|---|
| `gjq_backend_catalog` | catálogo completo; filtros por família |
| `gjq_backend_snapshot` | contagens por família/status |
| `gjq_resolve_backend` | resolve ID, nome exibido, API ou alias |
| `gjq_select_backend` | seleção por família, qubits e status |
| `gjq_research_plan` | recomenda backend e protocolo |
| `gjq_compare_plan` | plano simulador versus hardware |
| `gjq_backend_limits` | limites por família e restrições |
| `gjq_provenance_template` | campos de proveniência |
| `gjq_calibration_snapshot` | T1/T2 do snapshot, com aviso |

Exemplo de plano para Bell em 2 qubits:

```text
gjq_research_plan(goal="Bell", num_qubits=2, shots=1024)
→ recomendado: jiuxiao-fas-cpu (FAS-CPU)
```

Para hardware autorizado:

```text
gjq_research_plan(goal="Bell", num_qubits=2, hardware_allowed=True, prefer="hardware")
→ recomendado: baihua (hardware real online)
```

O MCP **não** substitui o `gjq-runtime`: ele não lista a fila ao vivo, não lê
calibração ao vivo e não submete. Use o runtime para isso.

## 4. Agentes

Foram criados 19 cards em `agents/catalog/gjq-backend-*.md`, um por recurso.
Cada card:

- tem capacidade exclusiva `profile_gjq_backend_<id>`;
- aponta para `SPEC-935-R1104` e `tests/test_r1104_gjq_backend_agents.py`;
- exige confirmação do nome vivo;
- separa simulador de hardware;
- não declara fidelidade, emaranhamento ou vantagem quântica sem evidência.

Lista:

```text
gjq-backend-guoji-01
gjq-backend-guoji-04
gjq-backend-guoji-07
gjq-backend-guoji-08-sim
gjq-backend-baihua
gjq-backend-yudu
gjq-backend-jiuxiao-fas-cpu
gjq-backend-jiuyun-noise-cpu
gjq-backend-jiuyuan-sas-cpu
gjq-backend-jiuci-pas-cpu
gjq-backend-qilv-fas-gpu
gjq-backend-qijian-noise-gpu
gjq-backend-qiyao-sas-gpu
gjq-backend-qijing-pas-gpu
gjq-backend-mps
gjq-backend-liangshi-fas-npu
gjq-backend-weina-noise-npu
gjq-backend-weichi-sas-npu
gjq-backend-weixin-pas-npu
```

O gerador reproduzível é `scripts/gerar_agentes_gjq.py`; sem `--force`, ele
preserva cards existentes.

## 5. Gates e limites

- `confirm=True` continua obrigatório em `gjq_sample` e `gjq_estimate`.
- Hardware/emulação exige `allow_hardware=True`; o gate agora cobre Guoji01,
  Guoji04, Guoji07, Guoji08, Baihua e Yudu.
- `GJQ_MAX_QUBITS` (padrão 200) limita o QASM no runtime. MPS tem 997 qubits de
  capacidade, mas o limite só deve ser elevado com revisão explícita.
- Single-amplitude exige `amplitude_index`.
- Partial-amplitude não é full-amplitude.
- MPS exige `simulator_config`; capacidade não é praticidade.
- Simuladores de ruído não são calibração real.
- Counts corretos não provam fidelidade, emaranhamento ou vantagem quântica.

## 6. Testes

```bash
.venv/bin/python -m pytest tests/test_r1104_gjq_backend_agents.py -q
.venv-quantum/bin/python -m pytest tests/test_r1099_gjq_runtime_mcp.py -q
python3 -m integrations.opencode_cli
```

O teste R1104 valida o registro, os aliases, os gates, as 9 ferramentas do MCP,
os 19 cards pelo `AgentLifecycleService` e a ausência de segredo literal.

## 7. Proveniência

Cada execução deve registrar:

- `task_id`;
- backend e tipo;
- shots;
- timestamp;
- SHA-256 do QASM;
- versão do `gjq-client` e do Qiskit;
- status;
- counts ou valores esperados;
- auditoria da soma e erro padrão;
- data da calibração usada na comparação.

O snapshot e os planos deste documento não são execução. Nenhum job foi
submetido para produzir esta camada.
