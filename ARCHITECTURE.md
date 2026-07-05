# Arquitetura: OpenCode Ecosystem Core

Este documento detalha a arquitetura do núcleo do OpenCode Ecosystem, centrada no orquestrador `marceloclaro` e na camada **Metacognitive Interconnect (MCI)**.

## Diagrama de Arquitetura

```mermaid
graph TD
    %% Atores e Orquestrador
    User([Usuário / CLI]) -->|Comandos| Orchestrator[Orquestrador: marceloclaro]
    
    %% Camada Transformer
    subgraph TF [Transformer Layer]
        Attn[AttentionRouter<br>Multi-Head]
        Pipe[TransformerPipeline<br>Gerar-Verificar-Revisar]
        HTM[(Hierarchical<br>Memory HTM)]
        Emb[TaskEmbedder<br>d=64]
        
        Attn -.->|Usa| Emb
        HTM -.->|Usa| Emb
    end
    
    %% Camada MCI
    subgraph MCI [Metacognitive Interconnect]
        MB[MetaBus<br>Global Workspace]
        BB[Blackboard<br>A2A Protocol]
        Mem[(Metacognitive<br>Memory)]
        Ref[Reflexion<br>Middleware]
        
        MB <--> Mem
        BB <--> MB
        Ref <--> MB
    end
    
    %% Orquestrador integra as camadas
    Orchestrator -->|1. Recuperação em 2 níveis| HTM
    HTM -->|Lê Episódica| Mem
    Orchestrator -->|2. Roteia Tarefa| Attn
    Attn -->|Publica Volunteer| BB
    Orchestrator -->|3. Executa| Pipe
    
    %% Agentes
    subgraph Agents [Agentes do Ecossistema]
        A1[Researcher]
        A2[Coder]
        A3[Reviewer]
        A4[Academic Writer]
        A5[Auditor]
    end
    
    %% Fluxo de Agentes
    Agents -.->|Registra Agent Card| BB
    BB -.->|Call for Proposals| Agents
    Agents -->|Voluntaria-se| BB
    Agents -->|Conclui Tarefa| Ref
    
    %% MCP
    MCP[MCP Server] -->|Expõe API| MCI
    External[External Tools / LLMs] -->|JSON-RPC| MCP
```

## Fluxo de Vida de uma Tarefa (Arquitetura Transformer + MCI)

1. **Registro (Agent Loader):** Na inicialização, o sistema lê os arquivos `agents/*.md` e extrai o *frontmatter* YAML. Cada agente é registrado no Blackboard com um **Agent Card** (Padrão A2A).
2. **Percepção Hierárquica (HTM):** Antes de delegar, o orquestrador consulta a memória global usando a `HierarchicalMemory`. O `TaskEmbedder` vetoriza a consulta e a atenção é feita em dois níveis: atenção grossa sobre sumários de chunks, seguida de atenção fina sobre os eventos dos melhores chunks.
3. **Delegação via Atenção (Multi-Head Attention):** A tarefa é postada no Blackboard. Quando o *Call for Proposals (CFP)* retorna os agentes elegíveis, o `AttentionRouter` calcula scores softmax baseados em 4 cabeças: semântica (vetores d=64), cobertura de capacidade, *confidence ledger* e carga atual. O agente com maior score recebe a atribuição.
4. **Execução (Transformer Pipeline):** A tarefa entra no *encoder stack*. O agente selecionado executa o ciclo **Gerar → Verificar → Revisar** (padrão *Aletheia*). O `GradingHead` pontua a saída de 0 a 7 (padrão *IMO-GradingBench*). Se a nota for baixa, a tarefa volta para revisão com a conexão residual preservando o contexto anterior.
5. **Reflexão (MCI):** Ao reportar a conclusão, o *Reflexion Middleware* intercepta o evento, gera uma auto-reflexão, atualiza o *Confidence Ledger* do agente e persiste a experiência na memória semântica para futuras recuperações.
