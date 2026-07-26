# SPEC-935-R212 — Bootstrap resiliente do LiteRT-LM e orquestração nanogranular

**Versão**: 1.3.0  
**Status**: red  
**Data**: 2026-07-23  
**Autor**: Marcelo Claro (OpenCode Ecosystem Core)  
**Rótulos**: `litert-lm`, `opencode`, `orchestration`, `attention-routing`, `self-healing`, `sdd`, `tdd`, `security`

### Histórico de revisão

| Versão | Mudança |
|---|---|
| 1.0.0 | Bootstrap, supervisor, DAG, atenção multicritério e testes externos. |
| 1.1.0 | Incorpora hardening bloqueador: contenção de modelos, limites MCP e permissões OpenCode least-privilege. |
| 1.2.0 | Separa liveness local de readiness externa no TouchTerrain e limita seu watchdog. |
| 1.3.0 | Torna o backend Node de relevo um serviço systemd supervisionado e reiniciável. |

## 1. Problema

O OpenCode anuncia o LiteRT-LM como provider padrão, mas o daemon HTTP em
`127.0.0.1:9379` não é iniciado de forma única e supervisionada durante o
bootstrap do OpenCode. Existem caminhos concorrentes de inicialização no MCP,
provider e shell, sem lock interprocesso ou circuit breaker compartilhado.

O plano de controle multiagente também possui lacunas: capacidades obrigatórias
são tratadas como `any`, o Behavioral Gate pode falhar aberto, os scores das
cabeças de roteamento têm escalas incompatíveis, a carga/confiança pode estar
obsoleta e tarefas complexas não são decompostas em um DAG nanogranular
verificável.

Por fim, a suíte raiz mistura testes herméticos com testes de serviços locais,
causando falhas ambientais falsas ou não reproduzíveis em CI.

## 2. Objetivo

Entregar um caminho único, seguro e testável para:

1. solicitar o bootstrap do daemon LiteRT-LM em toda inicialização do OpenCode;
2. impedir processos duplicados e limitar tentativas de autocura;
3. separar testes herméticos de verificações externas opt-in;
4. decompor desafios em tarefas atômicas organizadas como DAG;
5. selecionar agentes por hard gates e ranking multicritério normalizado,
   inspirado em atenção Transformer, sem alegar equivalência neural;
6. executar recuperação automática apenas dentro de limites explícitos,
   idempotentes e auditáveis.

## 3. Decisões arquiteturais

### 3.1 Supervisor único do LiteRT-LM

- Um módulo Python versionado será a fonte canônica de `status`, `ensure`,
  `wait`, `stop` e estado do circuit breaker.
- O supervisor usará lock interprocesso, PID validado, endpoint de readiness,
  ambiente mínimo e bind fixo em loopback.
- O plugin do projeto solicitará `ensure --non-blocking` ao ser carregado pelo
  OpenCode. O MCP também fará a mesma solicitação como fallback; o lock garante
  idempotência.
- Uma unit `systemd --user` opcional executará o daemon em foreground. O
  supervisor preferirá a unit quando instalada e cairá para spawn controlado.
- Cold start não bloqueará indefinidamente o bootstrap do OpenCode.

### 3.2 Runtime nanogranular

- Uma tarefa complexa será representada por `TaskGraph` acíclico e por
  `NanoTaskSpec` imutáveis.
- Cada nó terá um artefato esperado, capacidades obrigatórias, dependências,
  critérios de aceitação, risco, orçamento e número máximo de tentativas.
- A decomposição inicial será determinística e limitada; decomposição por LLM
  poderá ser acoplada posteriormente, mas não será necessária para os testes.

### 3.3 Roteamento inspirado em atenção

- Hard gates precedem qualquer score: todas as capacidades obrigatórias,
  agente disponível, trust mínimo e ausência de circuit breaker.
- Cabeças semântica, capacidade, confiança e carga produzirão scores em
  `[0, 1]`; pesos somarão 1 e o softmax será aplicado somente aos elegíveis.
- A decisão será explicável e determinística, sem codificação posicional baseada
  na ordem global das tarefas.

### 3.4 Autocura delimitada

- Recuperação será uma máquina de estados com retries, backoff, reatribuição e
  circuit breaker, nunca um loop ilimitado.
- Operações destrutivas, instalação de dependências, abertura de rede, importação
  ou exclusão de modelos continuarão exigindo aprovação explícita.
- Esgotado o orçamento, a tarefa ficará `blocked`, `failed` ou `quarantined`.

## 4. Critérios de aceitação

| ID | Critério | Verificação |
|---|---|---|
| CA1 | O supervisor LiteRT expõe `status/ensure/wait/stop` e opera somente em `127.0.0.1:9379`. | Testes unitários/CLI |
| CA2 | Cinquenta solicitações concorrentes de `ensure` produzem no máximo um spawn. | Teste multiprocesso ou lock mockado |
| CA3 | O ambiente do filho contém apenas variáveis permitidas e não repassa canários `*_KEY`, `*_TOKEN` ou `*_SECRET`. | Teste com `Popen` mockado |
| CA4 | Três falhas de start abrem circuit breaker temporário; novas chamadas não criam processos até o período half-open. | Relógio fake + testes de estado |
| CA5 | Processo que não atinge readiness é terminado/reaped e o estado registra falha sem órfão conhecido. | Teste com processo fake |
| CA6 | O plugin OpenCode solicita bootstrap não bloqueante no carregamento, usando caminho fixo do workspace, e preserva o contrato `ProviderHook`. | Teste estático + typecheck quando disponível |
| CA7 | O MCP solicita bootstrap no início sem confundir seu transporte stdio com o daemon HTTP; handshake MCP continua funcional. | Teste/subprocesso stdio |
| CA8 | Uma unit `systemd --user` versionada executa o daemon em foreground, com loopback, restart limitado e quotas de processo/memória. | Auditoria estrutural da unit |
| CA9 | `doctor` inclui estado do LiteRT e distingue `offline`, `starting`, `ready`, `circuit_open` e `unavailable`, sem declarar inferência real. | Teste do doctor |
| CA10 | O teste de package build detecta `build.__main__`, usa saída temporária e não confunde namespace Debian com PyPA build. | Teste hermético |
| CA11 | Testes Geomaker/TouchTerrain que dependem de `/opt`, systemd ou portas locais são marcados `external` e ficam opt-in; testes unitários permanecem sempre ativos. | Execução pytest padrão/opt-in |
| CA12 | O nome canônico do bridge é `geomaker-api`; a unidade antiga não é iniciada em paralelo. | Teste/configuração operacional |
| CA13 | O Blackboard exige todas as capacidades obrigatórias (`all_of`) e consulta confiança viva. | Teste unitário |
| CA14 | Se todos os agentes forem bloqueados pelo Trust Engine, nenhuma atribuição ocorre e a tarefa fica explicitamente bloqueada. | Teste do orquestrador |
| CA15 | Todas as cabeças do roteador produzem scores normalizados; pesos configurados somam 1 e a decisão é determinística. | Testes numéricos |
| CA16 | `explain()` expõe elegíveis, exclusões, scores por cabeça, utilidade e pesos finais sem alegar atenção neural aprendida. | Teste de contrato |
| CA17 | O decompositor gera nós atômicos com IDs estáveis, dependências válidas e critérios verificáveis; ciclos ou dependências ausentes são rejeitados. | Testes de DAG |
| CA18 | Um DAG diamante libera o nó de junção somente após todas as dependências concluírem. | Teste de scheduler |
| CA19 | O runtime limita profundidade, fan-out, número de nós, tentativas e wall-clock; limites excedidos falham fechado. | Testes de orçamento |
| CA20 | Falhas transitórias podem ser reatribuídas dentro do orçamento; conclusão duplicada/atrasada é idempotente e não altera trust duas vezes. | Testes de autocura |
| CA21 | `MarceloClaroOrchestrator` oferece `nanogranulate`, `submit_graph`, `dispatch_ready`, `explain_assignment` e estado de recuperação, preservando `delegate()` legado. | Testes de integração |
| CA22 | Assinaturas do orquestrador no MetaBus são idempotentes por instância lógica. | Teste de múltiplas instâncias |
| CA23 | A configuração gerada permanece idêntica ao `opencode.json`, sem paths absolutos específicos da máquina. | `integrations.opencode_cli --check` |
| CA24 | Gates direcionados passam; a suíte completa reporta separadamente skips externos e não mascara falhas herméticas. | pytest/doctor |
| CA25 | O ciclo R212 e a reflexão MetaBus registram correções, falhas, score provisório e limitações restantes. | Auditoria de estado |
| CA26 | IDs de modelo vazios, `.`, `..`, absolutos, com barras invertidas, travessia ou symlink fora do cache são rejeitados antes de localizar/importar/excluir; exclusão via agente exige confirmação explícita. | Testes de filesystem temporário |
| CA27 | O MCP LiteRT aceita apenas os quatro modelos canônicos e limita mensagens, bytes, saída e temperatura antes de HTTP ou spawn. | Testes de payload com doubles |
| CA28 | O gerador OpenCode não concede escrita/shell universalmente: permissões declaradas são preservadas e agentes de auditoria/leitura permanecem sem mutação. | Teste reprodutível do config |
| CA29 | O watchdog TouchTerrain verifica `/healthz` puramente local, exige falhas consecutivas, usa lock/cooldown e não chama `sudo` quando executado pelo systemd. | Testes unitários com relógio/subprocesso fake |
| CA30 | A instalação operacional expõe `/healthz`, mantém `/main` como readiness funcional e atualiza a unit do watchdog sem tornar Earth Engine gatilho de restart local. | Teste externo opt-in + auditoria de unit |
| CA31 | O backend `relevo-server.cjs` é supervisionado por uma unit `geomaker-relevo`, volta após reboot/restart e responde pela porta 8083 e pelo proxy Nginx; loops manuais deixam de ser a fonte de verdade. | Auditoria da unit + teste externo opt-in |

## 5. Limites de segurança

- LiteRT-LM: um daemon, loopback, concorrência de inferência 1, fila máxima 8,
  startup máximo de 300 s e três falhas antes de abrir circuito por 15 min.
- Orquestração autônoma: profundidade máxima 3, fan-out 4, 20 nós por chamada
  interativa padrão, três tentativas por nó e uma reatribuição.
- Sem retry automático para exclusão, importação, instalação, commit/push,
  edição de credenciais ou mudanças fora do workspace.
- Um resultado mockado ou um health check não constitui evidência de inferência
  real nem aprovação SDD.

## 6. Estratégia TDD

1. **RED**: testes do supervisor, autostart, circuit breaker, hard gates, DAG,
   idempotência e separação de testes externos.
2. **GREEN**: implementação mínima de cada contrato.
3. **REFACTOR**: centralizar lifecycle LiteRT e remover caminhos concorrentes.
4. **VERIFICAR**: testes direcionados, suíte hermética, testes externos opt-in,
   doctor, config e handshake MCP.

## 7. Não objetivos

- Alegar que heurísticas multicritério são uma rede Transformer treinada.
- Garantir disponibilidade de Earth Engine, Cloudflare ou outros provedores de
  terceiros.
- Executar alterações destrutivas autonomamente.
- Considerar cartões do catálogo como 182 workers simultâneos reais.
- Declarar todos os bugs futuros resolvidos; o gate cobre defeitos reproduzidos
  e invariantes formalizados nesta versão.

## 8. Evidências obrigatórias para encerramento

- saída dos testes RED e GREEN;
- status real do daemon e `/v1/models` quando o runtime local permitir;
- ausência de processos LiteRT duplicados;
- `doctor`, `git diff --check` e `integrations.opencode_cli --check`;
- relatório honesto dos serviços externos que permanecerem indisponíveis.
