# HARNESS — Loop Engineering (R1100)

**Objetivo:** transformar um pedido de automação em uma especificação de loop
auditável, com parada verificável, verificação independente, estado, orçamento,
observabilidade e gates humanos.

**Não faz:** não executa o loop, não instala CLI, não abre PR, não faz merge,
não agenda cron e não altera `specs/loops/`.

## Entradas

- objetivo em uma frase;
- tarefa repetitiva e frequência;
- ferramentas e permissões disponíveis;
- dados/estado que precisam sobreviver entre voltas;
- orçamento de tokens, tempo e execuções;
- risco e caminhos proibidos;
- nível pretendido: L0, L1, L2 ou L3.

## Etapas

### 1. Delimitar

Produza:

- `purpose`: uma frase;
- `non_goals`: o que o loop não fará;
- `scope`: repositórios, branches, filas ou tickets observados;
- `owner`: quem responde pelo loop.

Se o objetivo não couber em uma frase, ainda não é um loop: é um projeto.

### 2. Testar merecimento

Marque as quatro condições:

- [ ] repete ao menos semanalmente;
- [ ] existe verificação objetiva ou checker independente;
- [ ] o orçamento cobre tentativas e erros;
- [ ] o agente tem ferramentas, logs e ambiente para agir e observar.

Menos de 4/4: registre o gargalo e recomende comando único, checklist ou
automação simples. **Não** force um loop.

### 3. Desenhar o ciclo

Preencha:

| Campo | Conteúdo |
|---|---|
| Trigger | cron, evento, fila ou manual |
| Action | uma sequência de verbos com ferramentas |
| Stop | critério objetivo **e** hard stop |
| Terminal states | `success`, `no_op`, `blocked`, `stalled`, `exhausted`, `error` |
| Escalation | quando e para quem |

Sem hard stop, o harness não avança.

### 4. Verificar

Ordem de preferência:

1. teste, lint, schema ou gate numérico;
2. checker independente com rubrica;
3. humano;
4. opinião — proibida como parada autônoma.

O checker deve ser read-only, receber a saída e tentar reprovar. Se
`maker == checker`, pare e corrija.

### 5. Auditar 5+1

- [ ] heartbeat;
- [ ] worktree isolado por tentativa;
- [ ] skill do projeto;
- [ ] conector com permissão mínima;
- [ ] maker e checker separados;
- [ ] memória durável.

### 6. Estado

`STATE.md` ou equivalente deve ter:

```yaml
schema_version: "1"
updated_at: "2026-11-08T00:00:00Z"
items:
  - id: "item-1"
    status: "open|in_progress|blocked|done|dropped"
    attempts: 0
    last_action: "..."
    evidence: "caminho/para/log"
    owner: "humano ou agente"
```

Regras: ler no início, escrever no fim, podar itens fechados, validar IDs
contra a fonte e nunca guardar segredo.

### 7. Orçamento e kill switch

```yaml
budget:
  max_tokens_per_run: 100000
  max_runs_per_day: 4
  max_runtime_minutes: 30
  kill_switch: "label loop-pause ou flag em STATE.md"
```

Sem orçamento e kill switch, o loop não passa de L1.

### 8. Observabilidade

- `loop-run-log.md` append-only;
- uma linha por execução: início, itens, ações, escalações, custo;
- métricas: execuções, sucessos, falhas, itens podados;
- inspeção sem ler o chat.

### 9. Safety

- denylist: segredos, auth, pagamentos, infraestrutura, produção;
- allowlist de caminhos para qualquer auto-merge;
- conector read-only no primeiro dia;
- gate humano para risco alto;
- rollback e contato de escalonamento.

### 10. Rollout

| Nível | Permitido |
|---|---|
| L0 | documentar |
| L1 | report-only, sem ação |
| L2 | pequenas ações com checker e revisão |
| L3 | sem supervisão, após 7 dias de L1 |

Pedido de L3 sem 7 dias de L1 é rebaixado pelo auditor.

### 11. Auditar

```bash
python3 -m loops.loop_engineering specs/loops/SEU_LOOP.md
```

Aceite somente com:

- `critical_failures == []`;
- `allowed_level` igual ao nível pretendido;
- `red_flags` vazias ou justificadas por escrito;
- `human_review_required == true`.

### 12. Handoff

Entregue:

- spec do loop;
- resultado do auditor;
- `STATE.md` inicial;
- orçamento e kill switch;
- dono humano;
- data da próxima revisão;
- decisão: prosseguir, corrigir ou não fazer loop.

## Template de spec

```markdown
# nome — Loop Specification

**Descrição:** uma frase.
**Use quando:** condição de uso.

## Trigger
- Tipo: `cron|evento|manual`
- Cadência: ...
- Justificativa: ...

## Objetivo e Verificação
- Objetivo: critério objetivo.
- Verificável: sim
- Check real: comando/gate.
- Hard stop: N iterações ou T minutos.

## Arquitetura
- `maker_checker`

## Estados Terminais Nomeados
- `success`
- `no_op`
- `blocked`
- `stalled`
- `exhausted`
- `error`

## Regra de Parada
- Detector de estagnação: janela=N, limiar=X.
- Teto de orçamento: N iterações.

## Memória
- caminho, schema, poda.

## Guardrails
- denylist, allowlist, gate humano, kill switch.
```

## Gates

- G1: 4/4 no teste de merecimento.
- G2: trigger, action e stop explícitos.
- G3: hard stop numérico.
- G4: verificação independente.
- G5: maker e checker separados; checker read-only.
- G6: estado com schema e poda.
- G7: orçamento e kill switch.
- G8: run log e métricas.
- G9: denylist, allowlist e gate humano.
- G10: L3 somente após 7 dias de L1.

Falha em G2–G6 ou G9 bloqueia autonomia. Falha em G1 recomenda não fazer loop.

## Limites

O harness é um contrato de engenharia. Ele não prova que o loop funciona, não
mede produtividade e não substitui revisão humana. Custo, segurança e merge
continuam responsabilidade do operador.
