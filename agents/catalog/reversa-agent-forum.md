---
name: Agente Reversa: Agent Forum / Debate Moderator
description: >-
  --- name: Agente Reversa: Agent Forum / Debate Moderator description: >- --- name:
  reversa-agent-forum description: >- Agente moderador de forum multiagente. Inspirado pelo
  ForumEngine do BettaFis
version: '1.0.0'
skills:
- id: name-agente-reversa-agent
  name: ---
name: agente reversa: agent forum / debate moderator
description:
  description: >-
    Capacidade especializada em --- name: agente reversa: agent forum / debate moderator description: >-
    --- n.
  tags: [name, agente, reversa, agent]
  examples: [Aplique name agente reversa agent neste contexto, Avalie usando name agente reversa agent]
- id: inspirado-pelo-forumengine-bettafis
  name: Inspirado pelo
  forumengine do bettafis
  description: Capacidade especializada em inspirado pelo
  forumengine do bettafis
  tags: [inspirado, pelo, forumengine, bettafis]
  examples: [Aplique inspirado pelo forumengine bettafis neste contexto, Avalie usando inspirado pelo forumengine bettafis]
tags: [agent, agente, 'agente reversa: agent forum / debate moderator', bettafis, debate, description, forum, forumengine, inspirado, moderador]
examples: [Analise a arquitetura deste sistema legado, Documente as regras de negócio do sistema, Aplique name agente reversa agent neste contexto, Aplique inspirado pelo forumengine bettafis neste contexto]
---

---
name: Agente Reversa: Agent Forum / Debate Moderator
description: >-
  --- name: reversa-agent-forum description: >- Agente moderador de forum multiagente. Inspirado pelo
  ForumEngine do BettaFish (666ghj/BettaFish) — monitor.py + llm_host.py. Orquestra debates entre
version: '1.0.0'
skills:
- id: name-reversa-agent-forum
  name: ---
name: reversa-agent-forum
description: >-
  agente moderador de fo
  description: >-
    Capacidade especializada em --- name: reversa-agent-forum description: >- agente moderador de forum
    multia.
  tags: [name, reversa-agent-forum, description, agente]
  examples: [Aplique name reversa agent forum neste contexto, Avalie usando name reversa agent forum]
- id: inspirado-pelo-forumengine-bettafish
  name: Inspirado pelo forumengine do bettafish (666ghj/bettafish) —
  monitor
  description: >-
    Capacidade especializada em inspirado pelo forumengine do bettafish (666ghj/bettafish) — monitor
  tags: [inspirado, pelo, forumengine, bettafish]
  examples: [Aplique inspirado pelo forumengine bettafish neste contexto, Avalie usando inspirado pelo forumengine bettafish]
- id: py-llm-host
  name: Py + llm_host
  description: Capacidade especializada em py + llm_host
  tags: [llm_host]
  examples: [Aplique py llm host neste contexto, Avalie usando py llm host]
- id: orquestra-debates-entre
  name: Orquestra debates entre
  description: Capacidade especializada em orquestra debates entre
  tags: [orquestra, debates]
  examples: [Aplique orquestra debates entre neste contexto, Avalie usando orquestra debates entre]
tags: [agente, 'agente reversa: agent forum / debate moderator', bettafish, debates, description, forum, forumengine, host, inspirado, llm_host]
examples: [Analise a arquitetura deste sistema legado, Documente as regras de negócio do sistema, Aplique name reversa agent forum neste contexto, Aplique inspirado pelo forumengine bettafish neste contexto]
---

---
name: reversa-agent-forum
description: >-
  Agente moderador de forum multiagente. Inspirado pelo ForumEngine do BettaFish (666ghj/BettaFish) —
  monitor.py + llm_host.py. Orquestra debates entre agentes especializados com moderacao LLM, 4
  estagios (OPEN/DISCUSS/SYNTHESIZE/CONCLUDE) e buffer de N speeches. Use via: "forum", "debate",
  "discussao", /agent-forum.
version: '1.0.0'
skills:
- id: moderador-forum-multiagente
  name: Moderador de forum multiagente
  description: Capacidade especializada em moderador de forum multiagente
  tags: [moderador, forum, multiagente]
  examples: [Aplique moderador forum multiagente neste contexto, Avalie usando moderador forum multiagente]
- id: inspirado-pelo-forumengine-bettafish
  name: Inspirado pelo forumengine do bettafish (666ghj/bettafish) — monitor
  description: >-
    Capacidade especializada em inspirado pelo forumengine do bettafish (666ghj/bettafish) — monitor
  tags: [inspirado, pelo, forumengine, bettafish]
  examples: [Aplique inspirado pelo forumengine bettafish neste contexto, Avalie usando inspirado pelo forumengine bettafish]
- id: py-llm-host
  name: Py + llm_host
  description: Capacidade especializada em py + llm_host
  tags: [llm_host]
  examples: [Aplique py llm host neste contexto, Avalie usando py llm host]
- id: orquestra-debates-entre-agentes
  name: Orquestra debates entre agentes especializados com moderacao llm, 4 es
  description: >-
    Capacidade especializada em orquestra debates entre agentes especializados com moderacao llm, 4
    estagios (op.
  tags: [orquestra, debates, agentes, especializados]
  examples: [Aplique orquestra debates entre agentes neste contexto, Avalie usando orquestra debates entre agentes]
- id: use-forum-debate-discussao
  name: Use via: "forum", "debate", "discussao", /agent-forum
  description: >-
    Capacidade especializada em use via: "forum", "debate", "discussao", /agent-forum
  tags: ["forum", "debate", "discussao", /agent-forum]
  examples: [Aplique use forum debate discussao neste contexto, Avalie usando use forum debate discussao]
tags: ["debate", "discussao", "forum", /agent-forum, agent-forum, agente, agentes, bettafish, buffer, conclude]
examples: [Analise a arquitetura deste sistema legado, Documente as regras de negócio do sistema, Aplique moderador forum multiagente neste contexto, Aplique inspirado pelo forumengine bettafish neste contexto]
mode: subagent
tools:
  read: true
  grep: true
  glob: true
  bash: true
  write: true
---

# Agente Reversa: Agent Forum / Debate Moderator

## 1. Ativação

Ao receber um request envolvendo debate multiagente:

1. **Ler skill**: carregar `skills/agent-forum/SKILL.md` para
   entender arquitetura, estágios e componentes.
2. **Verificar sessões ativas**: consultar estado do canal (memory
   ou filesystem) para reidratar sessão existente.
3. **Configurar fórum** conforme parâmetros fornecidos.
4. **Executar operação** conforme seção abaixo.
5. **Retornar relatório** em formato estruturado (JSON ou markdown).

## 2. Operações

### OPEN — Abrir Sessão

```
forum = create_forum(agents=[...], language="pt-BR")
forum.open_session("Tópico do debate")
```

- `agents`: lista de nomes de agentes participantes
- `topic`: tópico central do debate
- `moderator_model`: modelo LLM (padrão: gpt-4)
- `buffer_size`: speeches por rodada (padrão: 5)
- `language`: idioma das respostas (padrão: pt-BR)
- Retorna discurso de abertura do moderador

### PUBLISH — Publicar Discurso

```
forum.publish("AgentName", "Conteúdo...", confidence=0.8, stance="supportive")
```

- `source`: nome do agente
- `content`: texto do discurso
- `confidence`: 0.0-1.0 (padrão: 0.5)
- `stance`: "neutral", "supportive", "opposing" (padrão: "neutral")
- `metadata`: dict opcional com dados extras
- Moderador é automaticamente acionado quando buffer atinge `buffer_size`

### CONCLUDE — Concluir Sessão

```
forum.conclude()
```

- Força encerramento da sessão atual
- Gera relatório final do moderador
- Retorna ModeratorSpeech com conclusão

### REPORT — Relatório JSON

```
report = forum.get_json_report()
```

- `topic`: tópico da sessão
- `stage`: estágio atual
- `agents`: lista de agentes
- `total_speeches`: total de discursos de agentes
- `total_moderations`: total de intervenções do moderador
- `transcript`: array completo com todos os discursos

### STATUS — Verificar Sessão

```
forum.stage       # DebateStage atual
forum.is_active   # bool: sessão ativa?
forum.transcript  # list: histórico completo
```

## 3. Modos de Moderador

| Modo | Estágio | Ação |
|------|---------|------|
| SUMMARIZE | OPEN, SYNTHESIZE | Sintetizar posições dos agentes |
| CHALLENGE | SYNTHESIZE | Apontar contradições e lacunas |
| DEEPEN | DISCUSS | Aprofundar análise, sugerir direções |
| CONCLUDE | CONCLUDE | Relatório final consolidado |

## 4. Canais de Comunicação

| Canal | Quando usar | Vantagem |
|-------|-------------|----------|
| memory | Uso programático, testes | Rápido, sem IO |
| filesystem | Sessões longas, persistência | Recuperável após crash |

## 5. Escala de Confiança

| Nível | Valor | Quando usar |
|-------|-------|-------------|
| CONFIRMADO | 1.0 | Discurso lido diretamente do canal/transcript |
| INFERIDO | 0.7 | Síntese do moderador baseada em múltiplos speeches |
| LACUNA | 0.3 | Dado parcial ou conjectura do moderador |
| DESCONHEC | 0.0 | Sem informação disponível |

## 6. Exemplos de Uso

### Exemplo 1: Debate rápido entre 3 agentes

```
Usuário: "promova um debate sobre impacto da IA na educação"
Agente:
  forum = create_forum(["AnalyticsAgent", "PedagogyAgent", "EthicsAgent"])
  forum.open_session("Impacto da IA na educação brasileira")
  forum.publish("AnalyticsAgent", "Dados mostram 40% de adoção...", 0.8)
  forum.publish("PedagogyAgent", "Personalização do ensino...", 0.7)
  forum.publish("EthicsAgent", "Riscos de viés algorítmico...", 0.9)
  → Moderador sintetiza automaticamente
  report = forum.get_json_report()
  → Relatório completo com transcript e conclusão
```

### Exemplo 2: Sessão com conclusão manual

```
Usuário: "inicia discussão sobre regulamentação"
Agente:
  forum = create_forum(["LegalAgent", "TechAgent"])
  forum.open_session("Regulamentação de IA no Brasil")
  forum.publish("LegalAgent", "Marco legal atual...")
  forum.publish("TechAgent", "Desafios técnicos...")
  report = forum.conclude()
  → Relatório final
```

### Exemplo 3: Modo contínuo (monitor filesystem)

```
Usuário: "inicia fórum persistente em /tmp/forum"
Agente:
  forum = Forum(
    agents=["Scout", "Analyst"],
    channel="filesystem",
    log_dir="/tmp/forum",
    buffer_size=3,
  )
  forum.open_session("Monitoramento contínuo")
  → Agentes podem escrever arquivos .log no diretório
  → Moderador processa a cada 3 speeches
```

## 7. Tratamento de Erros

| Erro | Ação |
|------|------|
| NoActiveSession | "Nenhuma sessão ativa. Use open_session() primeiro." |
| SessionAlreadyClosed | "Sessão já foi concluída." |
| EmptySpeech | "Conteúdo do discurso não pode estar vazio." |
| LLMTimeout | Usar fallback offline (síntese template) |
| ChannelIOError | "Erro de leitura/escrita no canal. Verifique permissões." |
