---
name: loop-engineering
description: Projeta e audita loops de agentes com trigger, ação, parada verificável, hard stop, verificação independente, maker-checker, estado durável, orçamento, observabilidade e gates humanos. Use para decidir se um loop vale a pena, desenhar um loop novo ou diagnosticar um loop que não converge; não executa loops, não instala CLI npm e não habilita auto-merge.
metadata:
  version: "1"
  origem: "R1100 — Loop Engineering no Core"
---

# Loop Engineering

Loop Engineering é engenharia de **sistemas que operam agentes**, não uma
técnica de escrever prompts melhores. A pergunta central muda de “qual é o
próximo prompt?” para “qual é o gatilho, a ação, a parada, a verificação e a
memória deste ciclo?”.

## Quando usar

- Decidir se uma tarefa merece um loop ou apenas um comando único.
- Transformar “faça até ficar bom” em uma condição de parada observável.
- Diagnosticar loop que não converge, gasta tokens demais ou entrega
  resultado que ninguém revisa.
- Separar quem produz de quem verifica.
- Auditar estado, orçamento, observabilidade e safety antes de aumentar
  a autonomia.
- Projetar um loop de triagem, manutenção, revisão, pesquisa ou conteúdo.

## Quando não usar

- Tarefa única, sem repetição e sem feedback entre voltas.
- Script determinístico que já tem cron e não precisa de verificação
  iterativa.
- Sistema já estável e compreendido; não reestruture só para “usar loop”.
- Tarefa criativa em que o critério de “bom” é totalmente subjetivo e não há
  humano disponível para o gate.
- Pedido para executar auto-merge, apagar dados ou operar produção sem
  allowlist e aprovação humana.

## Loop não é cron

| Conceito | O que é |
|---|---|
| Cron | dispara um comando fixo em horário fixo |
| Harness | ambiente de uma sessão: ferramentas, permissões, contexto e regras |
| Loop | harness + gatilho + repetição + verificação + estado + parada |

Um cron que só executa `backup.sh` não é loop. Um loop precisa de feedback
real entre voltas: o resultado da volta anterior muda a decisão da próxima.

## 1. Três elementos mínimos

Todo loop precisa responder:

1. **Trigger** — o que inicia a volta? Ex.: `cron diário`, `novo issue`,
   `CI falhou`, `novo arquivo na pasta`.
2. **Action** — o que a volta faz? Ex.: ler, classificar, propor patch,
   executar teste, atualizar estado.
3. **Stop condition** — quando a volta termina? Ex.: `nenhum item novo`,
   `critério X atingido`, `máximo de 3 iterações`.

Sem trigger, o loop não começa. Sem action, é vazio. Sem stop, pode consumir
recursos indefinidamente. Todo loop precisa também de um **hard stop**
independente da qualidade: número máximo de iterações, tempo ou custo.

## 2. Teste de merecimento

Quatro condições precisam ser satisfeitas:

1. **Repetição** — a tarefa acontece pelo menos semanalmente.
2. **Verificação** — existe teste, lint, gate numérico ou checker
   independente que reprova resultado ruim.
3. **Orçamento** — há teto de tokens, tempo e execuções; o custo de errar
   cabe no orçamento.
4. **Ferramental** — o agente tem logs, ambiente, testes e ferramentas para
   agir e observar o efeito.

Quatro de quatro: pode desenhar o loop. Três de quatro: resolva o gargalo
antes. Duas ou menos: use comando único, checklist ou automação simples.

## 3. Goal e verificação

A qualidade do loop é limitada pela qualidade do seu critério de parada.

- Ruim: “até ficar bom”, “até você gostar”, “até parecer pronto”.
- Bom: “teste `pytest -q` passa”, “S ≥ 2”, “fila vazia”, “máximo de 3
  tentativas”.
- Melhor ainda: critério objetivo **e** hard stop: “teste passa ou 3
  tentativas; se falhar, escalar com o log”.

Escada de verificação, da mais objetiva para a mais subjetiva:

1. teste, lint, schema, gate numérico;
2. checker independente com rubrica;
3. julgamento humano;
4. “eu acho” — não usar como parada de loop autônomo.

## 4. Maker-checker

Quem produz não deve aprovar o próprio trabalho.

- **Maker**: implementa, escreve, classifica ou propõe.
- **Checker**: read-only, recebe a saída, aplica critérios e tenta reprovar.
- O checker deve rodar testes ou conferir evidência, não apenas “olhar”.
- Se maker e checker forem o mesmo modelo/sessão, o gate é teatro.
- Se o checker não for read-only, ele pode “consertar” o resultado para
  passar, mascarando o problema.

Exceção: quando a verificação é puramente determinística (teste binário),
o checker pode ser o próprio runner de testes. Ainda assim, o maker não
define o critério depois de ver o resultado.

## 5. Arquitetura 5+1

| Componente | Pergunta |
|---|---|
| Heartbeat | qual é o gatilho e a cadência? |
| Worktree | o trabalho roda em espaço isolado? |
| Skill | as regras do projeto estão escritas e são lidas a cada volta? |
| Conector | quais ferramentas externas entram, com qual permissão? |
| Subagente | maker e checker estão separados? |
| Memória | onde ficam estado, tentativas, decisões e histórico? |

A memória é a coluna vertebral. Sem ela, cada volta começa amnésica e repete
erros. O estado precisa de schema, leitura no início, escrita no fim e poda
de itens resolvidos.

## 6. Construção progressiva

1. **Manual** — prove que a tarefa é compreendida e que o critério funciona.
2. **Skill** — escreva regras, comandos, formato de saída e limites.
3. **Trigger** — adicione cron, evento ou fila; ainda em report-only.
4. **Verificação + estado** — adicione checker independente, hard stop,
   orçamento, log e poda.
5. **Autonomia** — só depois de observar o loop em L1 por tempo suficiente.

Não pule etapas. Um loop que começa em L3 é um incidente esperando data.

## 7. Níveis de prontidão

| Nível | Nome | Critério |
|---|---|---|
| L0 | Rascunho | intenção documentada; nada executado |
| L1 | Relatório | triagem e estado; humano decide e executa |
| L2 | Assistido | pequenas ações com verificação; humano revisa |
| L3 | Não assistido | roda sem supervisão contínua; todos os gates |

Regra do Core: **L3 exige pelo menos 7 dias de L1 observado**, com logs e
verificação funcionando. L2 exige pelo menos 1 dia de L1. O auditor rebaixa
pedido de L3 sem essa janela.

## 8. Anti-padrões

- mesmo agente implementa e verifica;
- loop sem hard stop;
- `STATE.md` sem schema, sem poda e sem leitura no início;
- auto-merge sem allowlist de caminhos;
- conector MCP com escrita ampla no primeiro dia;
- notificar em toda execução, inclusive quando não há nada;
- corrigir teste intermitente com código sem classificar a causa;
- aumentar autonomia antes de medir a precisão da triagem;
- não ler o que o loop produziu.

## 9. Modos de falha

| Falha | Sintoma | Mitigação |
|---|---|---|
| Loop infinito de correção | mesma falha após 3+ tentativas | hard cap e escalar |
| Estado podre | referências a itens já fechados | podar e validar IDs |
| Teatro de verificação | checker aprova, CI reprova | checker independente e testes |
| Fadiga de notificação | equipe ignora alertas | notificar só ação humana |
| Queima de tokens | custo sobe sem resultado | orçamento, early exit, log |
| Excesso de escopo | loop mexe no que não devia | denylist e diff mínimo |
| Dívida de compreensão | código existe, equipe não entende | leitura humana e revisão |
| Colisão paralela | agentes pisam no mesmo arquivo | worktree por tentativa |

## 10. Checklist antes de ligar

- [ ] objetivo em uma frase e não objetivos explícitos;
- [ ] trigger, action e stop condition;
- [ ] hard stop de iterações/tempo/custo;
- [ ] verificação objetiva ou checker independente;
- [ ] maker e checker separados; checker read-only;
- [ ] estado com schema, leitura, escrita e poda;
- [ ] orçamento e kill switch;
- [ ] run log e métricas;
- [ ] denylist, allowlist e gate humano;
- [ ] rollback e escalonamento;
- [ ] nível L0–L3 declarado;
- [ ] auditoria determinística rodada.

## 11. Auditoria

```bash
python3 -m loops.loop_engineering specs/loops/harness-reasoning-97.md
```

O auditor devolve `score`, `computed_level`, `allowed_level`, `checks`,
`critical_failures`, `red_flags` e `missing`. Ele não executa o loop, não
acessa a rede e não escreve arquivos. O resultado é um checklist, não uma
prova de que o loop funciona.

## 12. Fontes e limites

Referências conceituais:

- Cobus Greyling, *Loop Engineering* (MIT);
- HuaShu, *Loop Engineering Orange Book* (MIT);
- *awesome-loop-engineering* (CC0);
- *kangarooking/loop-engineering-skill* (MIT);
- Addy Osmani, *Loop Engineering* (blog).

O texto desta skill é original e resume os conceitos com atribuição. Loop
Engineering é método de engenharia, não teoria científica validada. Um loop
auditado pode falhar; um loop não auditado pode falhar mais cedo. A decisão
final continua humana.
