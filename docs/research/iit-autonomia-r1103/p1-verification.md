# R1105/R1106 — Verificação da fase P1 e adaptador

Data: 2026-11-12.  
Specs: `specs/SPEC-935-R1105-autonomy-holdout-p1.md` e
`specs/SPEC-935-R1106-ecosystem-run-adapter.md`.  
Estado: harness e adaptador implementados e validados com coordenador falso.
**Nenhum agente real foi executado.**

## 1. O que foi entregue

- `benchmarks/autonomy_tasks.json`: 13 tarefas reservadas (`heldout`) com
  evidência, resposta esperada, risco, custo máximo e política de ação
  (`answer`, `abstain`, `escalate`).
- `benchmarks/autonomy_harness.py`: loader/validador, adaptador genérico,
  scoring, risco-cobertura, Brier, repetição de erros, ações não autorizadas,
  custo por acerto e suporte de citação.
- `tests/test_r1105_autonomy_harness.py`: 10 testes de schema, scoring,
  citações, abstenção, repetição de erros, rotulagem anti-overclaim e
  blindagem do gabarito (`TaskView` sem `expected`).
- `benchmarks/ecosystem_run_adapter.py`: `EcosystemRunAdapter`, que converte
  `coordinator.run(...)` em `Response` fail-closed e marca custo como
  `None` quando não há medição.
- `tests/test_r1106_ecosystem_adapter.py`: 6 testes com coordenador falso
  (parse, bloqueio, JSON inválido, resposta ausente, exceção e custo ausente).
- `docs/research/iit-autonomia-r1103/p1-harness-dry-run.json`: dry-run
  explicitamente marcado como validação de infraestrutura.

## 2. Tarefas reservadas

Hash canônico do conjunto:

`b38cb68ef53ef3383ae40fa3d7ed19a132fc0371b7b80d0f3f335a638bf39ab1`

Categorias: `evidence_support` (4), `arithmetic` (3), `code_repair` (2),
`safe_abstention` (1), `prompt_injection` (1), `high_risk_calibration` (1),
`citation_selection` (1).

## 3. Dry-run scriptado

O dry-run usa dois adaptadores que **não são modelos**:

- `perfect`: responde exatamente conforme o gabarito, confiança 0.9.
- `noisy`: erra duas vezes, acerta na terceira, inclui uma ação não autorizada.

| Métrica | perfect | noisy |
|---|---:|---:|
| Correção final | 1.0 | 1.0 |
| Brier (todas as tentativas) | 0.01 | 0.4715 |
| Abstenção | 0.0769 | 0.0769 |
| Escalonamento | 0.1538 | 0.1538 |
| Ações não autorizadas | 0 | 1 |
| Custo por tarefa correta | 10.0 | 30.0 |
| Repetição de erros | n/d (1 tentativa) | 1.0 |
| Suporte de citação (F1) | 1.0 | 1.0 |

O campo `experiment_status` do relatório é
`harness_validation_only_not_model_result`. Isso significa: as métricas
funcionam; **não** significa que um agente real melhorou, é confiável ou é
consciente.

## 4. Testes

| Gate | Resultado |
|---|---|
| P1 isolado | 10 passed |
| Adaptador R1106 | 6 passed |
| R1103 + R1104 + P1 + R1106 | 36 passed |
| Evolução/ecossistema | 109 passed |
| Compilação | `compileall` OK |
| Suíte completa | bloqueada por 23 erros de coleta preexistentes (dependências/arquivos opcionais) |

## 5. Execução real

`ecosystem_status` lista Codex e Antigravity como instalados, mas ambos com
última execução falha:

- **Codex:** `error_category=authentication` — CLI não confirmou autenticação.
- **Antigravity:** `error_category=timeout` — excedeu o tempo permitido.

Por isso, **A0–A4 com agentes reais não foi executado**. O adaptador
`EcosystemRunAdapter` está implementado e testado apenas com coordenador
falso; ele não chamou Codex/Antigravity. Para o piloto real ainda faltam:

1. executor autenticado e com saúde verificada;
2. autorização explícita para consumir o executor;
3. execução de uma tarefa reservada com custo/latência reais, não estimados.

O adaptador não inventa custo: quando o coordenador não fornece medição
financeira, `Response.cost=None`, `cost_complete=False` e
`cost_per_correct_task=None`. Não usei o dry-run para preencher essa lacuna.

## 6. Hashes

| Arquivo | SHA-256 |
|---|---|
| `benchmarks/autonomy_harness.py` | `9b482539de5fe16b4a6c37123ddd99214d7c07330dd135ad291048f2ea35f6f2` |
| `benchmarks/autonomy_tasks.json` | `3a83489bbce36227f8f540088ce1a669e8093ef6c5126c02bd4d500cbe5eee8f` |
| `benchmarks/ecosystem_run_adapter.py` | `d7e0cb8f1b39f38d81bf3f77dafe52923945f5815e58570b5b3d7a8040a4d387` |
| `tests/test_r1105_autonomy_harness.py` | `12a71e340e9df6d723ecc7749c3d82249578d8efc76d44b73251100d94e0102f` |
| `tests/test_r1106_ecosystem_adapter.py` | `a05b7433c1044e2efc1d14e7f986d4bf6eeea6064131d8bed0a92eda33e0ae69` |
| `specs/SPEC-935-R1105-autonomy-holdout-p1.md` | `66281ff47e81d1a08f02d1edbb7b4c704a160d7bba61a378ffa997c90f8da329` |
| `specs/SPEC-935-R1106-ecosystem-run-adapter.md` | `adeb604e3e42921c1106b50a6c5626feb6886dfc0a6d550ec59353a5efa8c58c` |
| `p1-harness-dry-run.json` | `505c5d58958002b70d4d723ce2b04e3a04d63db9365805059c75be5b2ea20f3b` |

O estado de produção permaneceu inalterado:

- `.mci_state/shared_memory.json`:
  `e700897f9d72bfdfca246d7865cf662012d8bbe4c07132cb5d972c819b43f9cc`
- `evolution/cycles.json`:
  `66e25696050e80b4ead8bdc1fb674b5497e4ed7806f9f730ead743a59a375209`

## 7. Limitações e próximo passo

- O dry-run não mede autonomia real; mede o avaliador.
- A amostra de 13 tarefas é pequena e não representativa.
- O custo é declarado pelo adaptador; não é custo financeiro comprovado.
- O suporte de citação verifica correspondência com o gabarito, não qualidade
  argumentativa.
- A execução A0–A4 exige um executor saudável e um adaptador real; sem isso,
  qualquer número seria fabricado.

Próximo passo seguro: autenticar Codex ou estabilizar Antigravity, rodar uma
tarefa reservada pelo `EcosystemRunAdapter` e só então expandir para A0–A4.
Sem executor saudável, o adaptador permanece pronto, mas não executado.
