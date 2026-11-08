# SPEC-935-R1100 — Loop Engineering no Core

**Status:** implementação autorizada pelo usuário
**Data:** 2026-11-08
**Escopo:** adicionar ao Core uma camada de projeto e auditoria de loops de agentes, baseada em Loop Engineering, sem executar loops nem habilitar auto-merge.

## 1. Contexto

A pesquisa no GitHub identificou um ecossistema ativo:

- `cobusgreyling/loop-engineering` — MIT, padrões, starters e CLI;
- `alchaincyf/loop-engineering-orange-book` — MIT, guia em PDF;
- `ChaoYue0307/awesome-loop-engineering` — CC0, definição e taxonomia;
- `kangarooking/loop-engineering-skill` — MIT, oito skills destiladas;
- `HKUDS/DeepCode`, `valkor-ai/loom`, `agentic-in/inferoa`,
  `baidu-baige/LoongFlow` e `GaosCode/PlanWeave` — implementações e variações.

O Core já tem specs de loop (`specs/loops/`) e um motor de orquestração. A
integração não duplica o motor: acrescenta **método, auditoria e gates** para
desenhar loops seguros.

## 2. Objetivo

Permitir que o orquestrador primário:

1. recuse loops desnecessários;
2. transforme objetivo vago em condição de parada verificável;
3. exija verificação independente e maker-checker;
4. audite estado, orçamento, observabilidade e safety;
5. classifique a prontidão em L0–L3;
6. bloqueie L3 sem uma semana de L1 observado;
7. bloqueie auto-merge sem allowlist e auto-verificação.

## 3. Artefatos

| Artefato | Caminho | Função |
|---|---|---|
| Spec | `specs/SPEC-935-R1100-loop-engineering.md` | este documento |
| Skill | `.opencode/skills/loop-engineering/SKILL.md` | método, checklist e limites |
| Agente | `agents/catalog/loop-engineering-architect.md` | projeta e audita loops |
| Auditor | `loops/loop_engineering.py` | `audit_loop`, `parse_loop_markdown`, `audit_loop_file` |
| Harness | `harnesses/loop-engineering/HARNESS.md` | etapas, gates e template |
| Testes | `tests/test_r1100_loop_engineering.py` | unidade e integração |
| Pesquisa | `docs/LOOP_ENGINEERING_R1100.md` | repositórios, licenças e decisões |

## 4. Requisitos funcionais

### 4.1 Skill

- Explicar loop como `trigger + action + stop condition`.
- Aplicar o teste de merecimento de quatro condições.
- Exigir goal verificável e hard stop.
- Exigir maker/checker separados, com checker read-only.
- Descrever a arquitetura 5+1: heartbeat, worktree, skill, conector,
  subagente e memória.
- Descrever a construção progressiva: manual → skill → trigger →
  verificação + estado.
- Classificar L0–L3 e os critérios de passagem.
- Listar anti-padrões e modos de falha.
- Citar as fontes e declarar que é método de engenharia, não teoria
  científica validada.

### 4.2 Auditor determinístico

`audit_loop(spec: dict) -> dict` deve:

- pontuar 10 dimensões com pesos que somam 10;
- distinguir checks críticos: stop, verificação, maker-checker, estado e safety;
- retornar `score`, `computed_level`, `allowed_level`, `requested_level`,
  `critical_failures`, `red_flags`, `checks`, `missing`;
- retornar sempre `human_review_required=True` e
  `scientifically_validated=False`;
- não acessar rede, não executar comandos e não escrever arquivos.

`parse_loop_markdown(text) -> dict` deve ler o formato de `specs/loops/*.md`.

`audit_loop_file(path)` deve devolver o resultado com `source` e `sha256`.

### 4.3 Agente

`loop-engineering-architect` deve:

- projetar loops a partir de objetivo, restrições e orçamento;
- auditar specs existentes;
- recusar L3 sem 7 dias de L1;
- recusar auto-merge sem allowlist;
- recusar maker e checker iguais;
- exigir hard stop e estado durável;
- entregar `status`, `findings`, `evidence` e `limitations`;
- não executar loops, não instalar CLI npm, não habilitar conectores
  com escrita ampla e não declarar que um loop funciona sem execução
  observada.

### 4.4 Harness

O harness deve conter etapas, gates, template de spec, schema de estado,
orçamento, observabilidade, handoff e critérios de parada.

## 5. Critérios de aceitação

- [ ] `loop-engineering-architect` valida pelo contrato `managed-v1`.
- [ ] A skill tem frontmatter e descreve os oito conceitos.
- [ ] Spec completa e bem preenchida retorna `score >= 9,5` e `L3` quando
  `observed_days >= 7`.
- [ ] Maker e checker iguais retornam falha crítica e nível máximo L1.
- [ ] Ausência de stop ou de estado retorna falha crítica.
- [ ] Auto-merge sem allowlist retorna falha crítica de safety.
- [ ] Pedido de L3 com `observed_days < 7` é rebaixado.
- [ ] `specs/loops/harness-reasoning-97.md` é parseado e não é promovido a L3.
- [ ] O auditor não usa rede, shell, `eval` ou `exec`.
- [ ] O resultado nunca declara validação científica.
- [ ] `opencode.json` inclui o agente após regeneração.
- [ ] `tests/test_r1100_loop_engineering.py` passa.

## 6. Não objetivos

- Não instalar `@cobusgreyling/loop` nem qualquer CLI npm.
- Não executar loops, cron, GitHub Actions ou auto-merge.
- Não copiar texto ou código dos repositórios; usar somente conceitos,
  com atribuição.
- Não substituir o motor de loops existente em `specs/loops/`.
- Não declarar eficácia, ganho de produtividade ou validade científica.
- Não conceder ao agente permissão de escrita ampla ou auto-merge.

## 7. Riscos

- **Falso positivo:** um checklist completo não garante que o loop funciona.
- **Falso negativo:** um loop simples e seguro pode pontuar baixo por falta
  de documentação; o auditor deve explicar o que falta, não apenas reprovar.
- **Custo:** loops mal projetados consomem tokens; o orçamento e o kill switch
  são obrigatórios.
- **Dívida de compreensão:** automação sem leitura humana aumenta a distância
  entre o que existe e o que a equipe entende.
- **Segurança:** conectores com escrita ampla e auto-merge aumentam o raio de
  impacto; o padrão é read-only e gate humano.

## 8. Fontes e licenças

- Cobus Greyling, `loop-engineering`, MIT, commit
  `68ccc887ccf1e0cf3a1a1d787ce2da48f4959081`.
- HuaShu, `loop-engineering-orange-book`, MIT, commit
  `829aa6084cd68680e7f389bbde9dcaebda7a43e6`.
- `awesome-loop-engineering`, CC0, commit
  `593a5e01b41df37400b242edae1452bd664549b3`.
- `kangarooking/loop-engineering-skill`, MIT, commit
  `f959a779480fcb56808c3c0d7647c1e664f5f6f9`.
- Addy Osmani, “Loop Engineering” (blog), referência conceitual.
- `HKUDS/DeepCode`, MIT; `valkor-ai/loom`, Apache-2.0;
  `agentic-in/inferoa`, Apache-2.0; `baidu-baige/LoongFlow`, Apache-2.0;
  `GaosCode/PlanWeave`, MIT.
