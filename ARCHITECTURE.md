# Arquitetura: OpenCode Ecosystem Core

Este documento detalha a arquitetura do núcleo do OpenCode Ecosystem, centrada no orquestrador `marceloclaro` e na camada **Metacognitive Interconnect (MCI)**.

## Diagrama de Arquitetura

```mermaid
graph TD
    %% Atores e Orquestrador
    User([Usuário / CLI]) -->|Comandos| Orchestrator[Orquestrador: marceloclaro]
    
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
    
    %% Orquestrador interage com MCI
    Orchestrator -->|1. Percebe lições| Mem
    Orchestrator -->|2. Posta Tarefa| BB
    
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

## Fluxo de Vida de uma Tarefa

1. **Registro (Agent Loader):** Na inicialização, o sistema lê os arquivos `agents/*.md` e extrai o *frontmatter* YAML. Cada agente é registrado no Blackboard com um **Agent Card** (Padrão A2A), declarando suas capacidades (`search`, `python`, `audit`, etc.).
2. **Percepção (Orchestrator):** Antes de delegar qualquer tarefa, o orquestrador `marceloclaro` consulta o Global Workspace (Memória Metacognitiva) para herdar o contexto recente e as lições aprendidas em falhas anteriores.
3. **Delegação (Blackboard):** O orquestrador posta a tarefa no Blackboard, especificando as capacidades requeridas.
4. **Voluntariado:** O Blackboard emite um *Call for Proposals (CFP)* para os agentes elegíveis. Se houver múltiplos candidatos, o Blackboard os ordena pelo *Confidence Ledger* (um score mantido via Média Móvel Exponencial baseado no histórico de sucesso).
5. **Execução e Reflexão:** O agente selecionado executa a tarefa. Ao reportar a conclusão, o *Reflexion Middleware* intercepta o evento, gera uma auto-reflexão sobre a abordagem utilizada, atualiza o *Confidence Ledger* do agente e persiste as lições na memória semântica.
