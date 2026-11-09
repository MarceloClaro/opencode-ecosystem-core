# SPEC-935-R1105 — Melhorias da camada GJQ

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** SPEC-935-R1104

## 1. Contexto

A R1104 criou o catálogo de 19 recursos, 19 agentes e o MCP
`gjq-backend-research`. A camada funciona, mas ainda é genérica em cinco
pontos:

1. os agentes não dizem **para que serve** e **o que evitar** em cada backend;
2. o catálogo não informa a **idade do snapshot**;
3. não há comparação entre o catálogo estático e a lista ao vivo;
4. o template de proveniência não valida um registro;
5. não há circuitos de referência para Bell, GHZ, CHSH, QFT e VQE.

## 2. Requisitos

- **R1.** Cada backend deve ter `best_for`, `avoid` e
  `recommended_experiments`, derivados do tipo/família e exibidos no perfil.
- **R2.** O catálogo e o resumo devem informar `age_days`, `stale`,
  `stale_after_days` e `clock_skew`.
- **R3.** O MCP `gjq-runtime` deve oferecer `gjq_backend_drift`, que compara
  o registro estático com `list_backends` ao vivo, sem submeter job.
- **R4.** O MCP `gjq-backend-research` deve validar registros de proveniência
  e rejeitar campos ausentes, hash inválido, shots inválidos e soma de counts
  incompatível.
- **R5.** O MCP `gjq-backend-research` deve expor templates de experimentos
  em OpenQASM 2.0: Bell, GHZ-3, CHSH (4 circuitos), QFT-2 e ansatz VQE.
- **R6.** Nenhuma ferramenta nova pode exigir API key no prompt, gravar
  segredo ou submeter job.
- **R7.** O drift deve declarar `network_access=True`, `executed=False` e
  `jobs_submitted=False`.
- **R8.** A idade do snapshot deve ser tratada com honestidade: data futura
  gera `clock_skew`, não “fresco”.

## 3. Orientação por backend

A orientação é derivada de `kind` e ajustada por `family`:

| Tipo | Melhor uso | Evitar |
|---|---|---|
| superconducting | hardware real, calibração, Bell/CHSH com ruído | generalizar uma execução; circuitos longos sem QEC |
| emulated_hardware | ensaiar fluxo de hardware, comparar com histórico | alegar medida física |
| full_amplitude | validação rápida, distribuição completa | confundir simulação com hardware |
| noise | estudar ruído modelado, robustez | inferir T1/T2 do chip |
| single_amplitude | uma amplitude específica | sampling geral |
| partial_amplitude | subconjunto de amplitudes | distribuição completa |
| tensor_network | muitos qubits com baixo emaranhamento | circuitos profundos/altamente emaranhados |

## 4. Drift

`gjq_backend_drift` retorna:

- `matched`: pares `live_name` ↔ `registry_id`;
- `missing_in_registry`: nomes vivos sem correspondência;
- `missing_live`: IDs do registro sem correspondência viva;
- `ambiguous`: nomes com mais de um match;
- `unverified_api_names`: matches cujo nome de API não foi verificado;
- `network_access=True`, `executed=False`, `jobs_submitted=False`.

Sem chave, retorna `blocked`. A ferramenta não lê resultado nem submete.

## 5. Proveniência

`gjq_provenance_validate(record)` verifica:

- campos obrigatórios do template;
- `qasm_sha256` com 64 hexadecimais;
- `shots` inteiro positivo;
- `counts_or_evs` com soma igual a `shots` quando todos os valores forem inteiros;
- `backend` resolvido no catálogo;
- `status` em `INITIALIZING`, `QUEUED`, `RUNNING`, `DONE`, `ERROR`, `CANCELLED`;
- `limitations` não vazio.

Retorna `ok`, `errors`, `warnings`, `resolved_backend` e `executed=False`.

## 6. Templates

| Nome | Qubits | Uso |
|---|---:|---|
| `bell` | 2 | correlação e CHSH |
| `ghz3` | 3 | emaranhamento de três qubits |
| `chsh` | 2 | quatro circuitos ZZ, ZX, XZ, XX |
| `qft2` | 2 | transformada de Fourier quântica |
| `vqe_ansatz` | 2 | ansatz variacional com observável ZZ |

Os templates são texto; não são executados.

## 7. Aceitação

- 19 perfis com `best_for`, `avoid` e `recommended_experiments`;
- `gjq_backend_profile` e `gjq_backend_catalog` exibem a orientação;
- `gjq_backend_snapshot` informa idade/validade;
- `gjq_backend_drift` funciona com serviço falso e não submete;
- `gjq_provenance_validate` aceita registro válido e rejeita inválido;
- `gjq_experiment_template` retorna 5 templates e CHSH com 4 circuitos;
- testes R1105 passando; R1104/R1099 continuam passando;
- `opencode.json`, agentes e `mod-10` regenerados.

## 8. Não objetivos

- Não executar os templates.
- Não consultar a nuvem sem chave.
- Não substituir `gjq_list_backends`/`gjq_backend_properties`.
- Não provar fidelidade, emaranhamento ou vantagem quântica.
