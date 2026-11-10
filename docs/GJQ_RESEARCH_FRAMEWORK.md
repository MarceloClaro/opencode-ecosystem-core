# Core como framework de pesquisa quântica GJQ

**Status:** habilitado localmente; nenhum hardware executado.
**Módulo:** `integrations/gjq_research_framework.py`
**MCP:** `gjq-runtime` (habilitado no `opencode.json`)

## 1. O que é

Uma camada de orquestração que transforma o Core no framework de trabalho para
pesquisa GJQ:

- inventário do SDK, credencial, orçamento e catálogo E01–E18;
- plano de pesquisa com fases SDD/TDD, gates e manifesto;
- roteamento de agentes por capacidade;
- integração com o provider (`gjq_provider_*`);
- proveniência e limites explícitos.

Não é um motor de descoberta científica, não executa hardware sozinho e não
declara fidelidade, emaranhamento ou vantagem.

## 2. Ferramentas MCP

| Ferramenta | Efeito | Rede |
|---|---|---|
| `gjq_research_status` | catálogo, provider, agentes, readiness | não |
| `gjq_research_plan` | plano de fases/gates/roteamento | não |
| `gjq_provider_status` | SDK, credencial, orçamento | não |
| `gjq_provider_compilation` | auditoria de layout/QASM | sim, sem job |
| `gjq_provider_submit` | execução com gates | sim |
| `gjq_provider_result` | status/resultado/auditoria | sim |

O `opencode.json` mantém `gjq-runtime`, `gjq-experiments` e
`gjq-backend-research` habilitados.

## 3. Plano de pesquisa

Exemplo:

```bash
# via MCP, ferramenta gjq_research_plan
{
  "objective": "Comparar layouts com desenho pareado",
  "backend_name": "FAS-CPU",
  "shots": 2048,
  "required_capabilities": ["research", "audit"]
}
```

O plano devolve:

1. spec e critérios;
2. TDD;
3. simulação;
4. pré-registro;
5. auditoria de compilação;
6. gate de hardware;
7. execução via provider;
8. auditoria de counts;
9. reflexão no MetaBus/Evolution.

Cada fase tem gate próprio; não se transferem créditos entre fases.

## 4. Agentes roteados

| Capacidade | Agente |
|---|---|
| `research` | `gjq-quantum-research` |
| `experiment` | `gjq-experiment-runner` |
| `optimization` | `gjq-hardware-optimizer` |
| `readout` | `gjq-readout-mitigation` |
| `audit` | `quantum-experiment-auditor` |

O roteamento é uma recomendação; a execução continua sob o primário
`marceloclaro`.

## 5. Gates

- `confirm=True` para submissão;
- `allow_hardware=True` para Baihua/Guoji/Yudu;
- `GJQ_HARDWARE_ENABLED=1` para hardware;
- orçamento local e ledger;
- auditoria de layout antes de submissão;
- nenhuma chave em prompt, arquivo ou log.

## 6. Estado da integração

- Provider e MCP integrados; 4 tools do provider + 2 do framework.
- Conta cacheada suportada pelo provider.
- Teste controlado `compile=False`: **blocked** antes da submissão por
  `Failed to fetch machine config for Baihua`; nenhum task ID.
- Nenhum job foi submetido nesta habilitação.

## 7. Limites

- O servidor GJQ não devolve layout físico; a auditoria é local.
- `compile=False` no serviço ainda não foi aceito/testado.
- O framework não substitui SDD/TDD, revisão humana ou validação externa.
- Um count correto não prova fidelidade, emaranhamento ou vantagem.

## 8. Domínios de pesquisa (R1142–R1143)

`gjq_research_plan` aceita `domain`:

| Domínio | Fases adicionais | Agente |
|---|---|---|
| `general` | — | `gjq-quantum-research` |
| `classification` | dataset/split, feature map, kernel, baseline, calibração, ruído | `22_agente_ml_dl_datamining` |
| `cooking` | variáveis/objetivo, restrições, QUBO/QAOA, validação sensorial | `42_agente_desenvolvedor_cientista_computacao` |

Módulos offline:

- `quantum_research.classification`: kernel ZZ, kernel ridge, RBF, leakage.
- `quantum_research.cooking`: QUBO, brute force, QAOA p=1.

“Cozimento quântico” **não** é um campo estabelecido; o Core o trata como
otimização de processo com QUBO sintético. Não há dados sensoriais nem
alegação de vantagem quântica.

Dossiê: `docs/LITERATURA_CLASSIFICACAO_COZIMENTO_R1142.md`.
Resultados melhorados: kernel quântico multi-seed 0,854 vs RBF 0,896 (ruído
0,15) e 0,833 vs 0,771 (ruído 0,20); sem vantagem robusta. QAOA p=3:
−2,4623 vs brute force −2,6000 (ratio 0,925). Ver
`docs/RELATORIO_PESQUISA_QUANTICA_R1142.md`.

## 9. Reprodução

```bash
.venv-quantum/bin/python -m pytest tests/test_r1141_research_framework.py \
  tests/test_r1139_gjq_core_provider.py tests/test_r1099_gjq_runtime_mcp.py -q
```

MCP: use `gjq_research_status` e `gjq_research_plan`.
