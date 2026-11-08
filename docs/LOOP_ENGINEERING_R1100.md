# Loop Engineering no Core — R1100

**Data:** 2026-11-08
**Status:** skill, agente, auditor determinístico e harness implementados.
**Escopo:** projeto e auditoria de loops de agentes. Não executa loops, não
instala CLI npm e não habilita auto-merge.

## 1. O que é

Loop Engineering é a prática de projetar o **sistema que opera agentes** em
vez de escrever o próximo prompt manualmente. Um loop tem:

```text
trigger + action + stop condition + verification + state
```

Não é cron. Cron dispara um comando fixo; loop usa o resultado da volta
anterior para decidir a próxima, verifica o resultado e persiste estado.

## 2. Pesquisa no GitHub

Estrelas e metadados foram consultados em 2026-11-08 e mudam.

| Repositório | Licença | Estrelas | Função | Decisão |
|---|---|---:|---|---|
| `cobusgreyling/loop-engineering` | MIT | 11.731 | padrões, starters, CLI, L1–L3 | **Adotar conceitos**; não instalar CLI |
| `HKUDS/DeepCode` | MIT | 16.823 | agent harness, loop engineering, multiagente | **Referência** |
| `alchaincyf/loop-engineering-orange-book` | MIT | 1.141 | guia em PDF, chinês + inglês | **Referência** |
| `ChaoYue0307/awesome-loop-engineering` | CC0 | — | definição, taxonomia, anti-padrões | **Adotar conceitos** |
| `kangarooking/loop-engineering-skill` | MIT | — | oito skills destiladas | **Adotar conceitos** |
| `valkor-ai/loom` | Apache-2.0 | 1.445 | loop engineering para entrega de software | **Referência** |
| `agentic-in/inferoa` | Apache-2.0 | 569 | harness de inferência para loops | **Referência** |
| `baidu-baige/LoongFlow` | Apache-2.0 | 483 | loop Plan-Execute-Summary | **Referência** |
| `GaosCode/PlanWeave` | MIT | 434 | loop file-backed para agentes longos | **Referência** |
| `ModelEngine-Group/nexent` | MIT | 6.163 | plataforma de agentes | **Referência** |
| `Windy3f3f3f3f/how-claude-code-works` | MIT | 3.816 | internos de agent loop | **Referência** |
| `neomjs/neo` | MIT | 3.298 | organismo de engenharia com loops | **Referência** |
| `wquguru/harness-books` | Sem licença | 3.240 | harness engineering | **Não integrar** |

Commits auditados dos quatro principais:

- `cobusgreyling/loop-engineering` — `68ccc887ccf1e0cf3a1a1d787ce2da48f4959081`;
- `alchaincyf/loop-engineering-orange-book` — `829aa6084cd68680e7f389bbde9dcaebda7a43e6`;
- `ChaoYue0307/awesome-loop-engineering` — `593a5e01b41df37400b242edae1452bd664549b3`;
- `kangarooking/loop-engineering-skill` — `f959a779480fcb56808c3c0d7647c1e664f5f6f9`.

## 3. O que foi adotado

| Conceito | Uso no Core |
|---|---|
| Três elementos | trigger, action e stop explícitos |
| Teste de merecimento | quatro condições antes de criar loop |
| Goal verificável | parada objetiva + hard stop |
| Maker-checker | produtor e verificador separados; checker read-only |
| 5+1 | heartbeat, worktree, skill, conector, subagente, memória |
| Construção progressiva | manual → skill → trigger → verificação + estado |
| L0–L3 | prontidão e rollout |
| Anti-padrões | lista de recusas automáticas |
| Modos de falha | diagnóstico de loops que não convergem |

## 4. O que não foi adotado

- **CLI npm `@cobusgreyling/loop`**: é runtime de terceiro, exige Node/npm,
  escreve `STATE.md` e pode operar GitHub. Fica para avaliação futura.
- **Auto-merge**: proibido sem allowlist e gate humano.
- **Cópia de texto/código**: o Core usa conceitos e escreve seus próprios
  artefatos, com atribuição.
- **Alegação científica**: Loop Engineering é método de engenharia, não
  teoria validada experimentalmente.
- **Execução de loops**: o auditor apenas lê e pontua especificações.

## 5. Artefatos no Core

| Artefato | Caminho |
|---|---|
| Spec | `specs/SPEC-935-R1100-loop-engineering.md` |
| Skill | `.opencode/skills/loop-engineering/SKILL.md` |
| Agente | `agents/catalog/loop-engineering-architect.md` |
| Auditor | `loops/loop_engineering.py` |
| Harness | `harnesses/loop-engineering/HARNESS.md` |
| Testes | `tests/test_r1100_loop_engineering.py` |

### Auditor

```bash
python3 -m loops.loop_engineering specs/loops/harness-reasoning-97.md
```

O resultado contém:

- `score` e `max_score`;
- `computed_level`, `allowed_level`, `requested_level`;
- `checks` por dimensão;
- `critical_failures` e `critical_partial`;
- `red_flags` e `missing`;
- `human_review_required = true`;
- `scientifically_validated = false`.

Dimensões e pesos:

| Dimensão | Peso | Crítica |
|---|---:|---|
| purpose + non-goals | 1,0 | não |
| trigger | 1,0 | não |
| action | 0,5 | não |
| stop + hard cap | 1,5 | sim |
| verification | 1,5 | sim |
| maker-checker | 1,5 | sim |
| state | 1,0 | sim |
| budget | 0,5 | não |
| observability | 0,5 | não |
| safety | 1,0 | sim |

## 6. Resultados da auditoria

### Spec sintética completa

```text
score = 10,0
computed_level = L3
allowed_level = L3
critical_failures = []
red_flags = []
```

### Spec incompleta

```text
score = 5,0
computed_level = L1
allowed_level = L1
critical_failures = stop, maker_checker, state, safety
```

Red flags: mesmo agente faz e verifica; checker não é read-only; auto-merge
sem allowlist; ausência de hard stop; ausência de estado durável.

### `specs/loops/harness-reasoning-97.md`

```text
score = 7,25
computed_level = L2
allowed_level = L1
observed_days = 0
```

Motivo do rebaixamento: o loop não tem um dia de L1 observado. Faltam
`non_goals`, `budget` completo, `maker_checker` explícito, `observability`,
`safety` com denylist/gate e `state` com schema/poda.

Isso não significa que o loop existente seja ruim; significa que a
especificação não documenta os gates necessários para L2/L3.

## 7. Regras de ouro

1. Quatro de quatro no teste de merecimento; caso contrário, não criar loop.
2. Stop objetivo **e** hard stop.
3. Maker e checker separados; checker read-only.
4. Estado com schema, leitura, escrita e poda.
5. Orçamento e kill switch.
6. Run log e métricas.
7. Denylist, allowlist e gate humano.
8. L1 por pelo menos 7 dias antes de L3.
9. Não auto-merge sem allowlist.
10. Ler o que o loop produziu.

## 8. Limites

- Checklist determinístico não prova que o loop funciona.
- Não há execução, cron, PR, merge ou medição de produtividade.
- O auditor pode reprovar um loop bom mal documentado; o relatório mostra
  o que falta.
- O auditor pode aprovar uma spec bem documentada que ainda falha na prática;
  a execução observada continua necessária.
- Custo, segurança e merge continuam responsabilidade humana.

## 9. Fontes

- Cobus Greyling, *Loop Engineering* — <https://github.com/cobusgreyling/loop-engineering>.
- HuaShu, *Loop Engineering Orange Book* — <https://github.com/alchaincyf/loop-engineering-orange-book>.
- *awesome-loop-engineering* — <https://github.com/ChaoYue0307/awesome-loop-engineering>.
- *kangarooking/loop-engineering-skill* — <https://github.com/kangarooking/loop-engineering-skill>.
- Addy Osmani, *Loop Engineering* — <https://addyosmani.com/blog/loop-engineering/>.
- `HKUDS/DeepCode`, `valkor-ai/loom`, `agentic-in/inferoa`,
  `baidu-baige/LoongFlow`, `GaosCode/PlanWeave`.

Os textos do Core são originais; os repositórios são referência conceitual e
não endossam este livro ou este ecossistema.
