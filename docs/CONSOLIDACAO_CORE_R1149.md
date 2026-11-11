# Consolidação do Core — R1149

**Data:** 2026-11-10
**Depende de:** R1132, R1148
**Escopo:** runtime contract, CI e persistência do claims graph.

## 1. Problema encontrado

O diagnóstico mostrou duas camadas paralelas:

| Camada existente | Camada nova (R1148) | Risco |
|---|---|---|
| `core_cognition.runtime_contract` (usada pelo orquestrador) | `mci.runtime_contract` | duas políticas de ação |
| `core_cognition.claims_ledger` | `mci.claims_graph` | dois ledgers desconectados |
| `core_cognition.n_of_1` (validador) | `mci.n_of_1` (runner/SCED) | conceitos com o mesmo nome |

Além disso, o `ci.yml` não disparava em `codex/**` e `whoosh3` não estava
declarado, embora os testes metacognitivos o usem.

## 2. O que mudou

### 2.1 Runtime: um contrato canônico

`mci.runtime_contract.RuntimeContract` agora é um **adaptador de execução**:

- importa `ActionClass`, `ActionRequest`, `RuntimeContract` e `RuntimeState`
  de `core_cognition.runtime_contract`;
- antes de executar, chama `core_contract.authorize(...)`;
- `allow` → executa; `ask` → escala; `defer`/`block` → bloqueia;
- mantém hooks `before`/`after`, circuit breaker e auditoria JSONL;
- atualiza `core_state` com sucesso/falha e expõe `core_decision` no retorno;
- ação irreversível aprovada ainda exige `approval_token`.

Resultado: o orquestrador e o adaptador compartilham a mesma política; o
adaptador adiciona execução segura, não uma segunda política.

### 2.2 CI: patch pronto, aplicação pendente

O token OAuth disponível não tem o escopo `workflow`; o GitHub recusa push que
altere `.github/workflows/`. Por isso a mudança de CI foi separada em
`docs/ci/r1149-ci-workflows.patch` (90 linhas, YAML validado):

- `push`/`pull_request` incluem `codex/**` e `feat/**`;
- `workflow_dispatch` habilitado;
- job `lean-proofs` instala `elan`, cacheia `livro-core/lean/.lake`, busca o
  cache do Mathlib e compila:
  - `ComplexProofs.lean`;
  - `CorrelationCounterproof.lean`;
  - `MathlibCounterproof.lean`;
- falha se aparecer `sorryAx` ou `error:` nos dois primeiros logs.

`ci-escopos.yml` também passa a cobrir `codex/**` e `feat/**`.

Aplicação (exige credencial com escopo `workflow`):

```bash
git apply docs/ci/r1149-ci-workflows.patch
git add .github/workflows/ci.yml .github/workflows/ci-escopos.yml
git commit -m "ci: cover codex branches and add Lean proofs job"
git push
```

`requirements-dev.txt` passa a declarar `whoosh3==3.25.3`, usado por
`skills.tooling.llm_reduction` e pelos testes R886/R1050.

### 2.3 Claims graph: persistência e ponte com o ledger

`mci.claims_graph.ClaimsGraph` ganhou:

- `save(path)`: JSON canônico + SHA-256;
- `load(path)`: valida schema, nós, arestas e pesos; falha fechado em aresta
  órfã;
- `audit()`: contagem de nós/arestas/claims, contradições, abstenções e
  warrants;
- `from_ledger(path)`: importa claims do `core_cognition.claims_ledger` como
  claims empíricas/hipóteses, com evidência importada peso 0,5;
- `to_ledger()`: exporta para o formato do ledger; recusa claim sem
  falsificador.

CLI:

```bash
python3 -m mci.claims_graph --load graph.json --save copy.json
python3 -m mci.claims_graph --from-ledger claims.jsonl --save graph.json
```

## 3. Verificação

| Item | Resultado |
|---|---|
| Testes R1148 de runtime | 11 pass |
| Testes R1148 de claims | 15 pass |
| Integração R1148 | 1 pass |
| YAML do patch de CI | válido; aplicação pendente de token com `workflow` |
| `core_state.allowed` após `read_only` | 1 |
| `user_requested_stop` | bloqueia com `runtime_contract:stop:*` |
| Irreversível sem aprovação | `ask` → `escalated` |
| Save/load do grafo | roundtrip com warrant preservado |
| Ledger → grafo → ledger | `claim_id`, `status`, `falsifier` preservados |
| Lean local | já compilado; CI dedicado adicionado |

## 4. Limites

- O patch de CI ainda não foi aplicado: o token OAuth não tem escopo
  `workflow`. Enquanto não for aplicado, os gatilhos `codex/**` e o job Lean
  não estão ativos no GitHub.
- O job Lean depende de rede e cache do Mathlib; pode levar dezenas de minutos.
- A ponte ledger↔grafo é **lossy**: evidência vira nó com peso 0,5 e o
  pareamento continua editorial.
- `core_cognition.n_of_1` (validador de protocolo) e `mci.n_of_1` (runner
  SCED) ainda coexistem; a fusão completa fica para a próxima rodada.
- Nenhum hardware foi executado; nenhuma confiança foi promovida.
