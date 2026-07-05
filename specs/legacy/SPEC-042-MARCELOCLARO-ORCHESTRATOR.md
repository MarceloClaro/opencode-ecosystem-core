# SPEC-042: Marcelo Claro Supreme Orchestrator (/marceloclaro)

## 1. Visão Geral
O agente `/marceloclaro` (avatar digital de Prof. Marcelo Claro Laranjeira) atua como o **Orquestrador Supremo e Centralizador** de todo o OpenCode e do OpenCode Ecosystem. Ele é a camada de comando definitiva acima do `MasterOrchestrator`, traduzindo a intenção estratégica do usuário em ações coordenadas e auditadas. Quando o usuário executa `/marceloclaro`, o ecossistema aciona este agente para orquestrar os quatro pilares fundamentais de forma perfeita.

## 2. Os Quatro Pilares da Orquestração Suprema
* **Pilar 1: Engenharia de Extremo Rigor (TDD & Conformidade Científica)**
  - Valida e garante que qualquer código ou spec gerada passe pelas suítes de testes determinísticos (`tests/test_environment.sh` e testes unitários) antes de considerar a tarefa concluída.
* **Pilar 2: Contenção de Desvios e Alucinações (Cognitive Guardrails & SPEC-038 TrustEngine)**
  - Aciona as barreiras preventivas de comportamento, monitorando as respostas e ações dos subagentes em tempo real para impedir o desvio de objetivos (Goal Drift) e alucinações cognitivas.
* **Pilar 3: Visão de Negócio SaaS (Monetização & Token Economy)**
  - Rastreia e simula a economia de tokens, gerindo conexões Pay-as-you-go e preparando a telemetria do TrustEngine como um serviço em nuvem (*Trust-as-a-Service - TaaS*).
* **Pilar 4: Unificação e Alinhamento de CLIs (Ollama, OpenCode, Antigravity)**
  - Coordena e alinha as operações do **Ollama CLI** (motor local), **OpenCode CLI** (shell interativo), e **Antigravity CLI / agy** (orquestração externa de subagentes paralelos e navegação).

## 3. Arquitetura do Agente e Comando
* **Arquivo do Agente:** `agents/marceloclaro.md`
* **Arquivo do Comando:** `command/marceloclaro.md`
* **Fluxo de Delegação:**
  1. `/marceloclaro` intercepta o input do terminal.
  2. Inicializa o contexto de auditoria e segurança cognitiva.
  3. Deferirá a execução de tarefas específicas para:
     - `MasterOrchestrator` (`agents/master-orchestrator.md`): Para coordenação geral de pipelines.
     - `AntigravityOrchestrator` (`agents/antigravity-orchestrator.md`): Para navegação web, geração de imagens e subagentes paralelos.
  4. Consolida e emite um relatório final contendo o status de cada um dos quatro pilares.

## 4. Casos de Teste (TDD - `tests/core/test_marceloclaro.py`)
* **CT-4201 (Registro do Comando):** Garante que o comando `marceloclaro` e a rota `/marceloclaro` estão carregados e disponíveis no `CommandDispatcher`.
* **CT-4202 (Orquestração de Pilares):** Valida se o agente retorna o status consolidado com validação dos 4 pilares em seu resultado de execução.
* **CT-4203 (Delegação e Alinhamento):** Testa se a chamada delega e interage corretamente com o `AntigravityOrchestrator` e o `MasterOrchestrator` em cenários simulados.
* **CT-4204 (Controle de Erro & Guardrails):** Verifica se o agente detecta e bloqueia comandos instáveis acionando as regras de contenção do TrustEngine.
* **CT-4205 (Integração de Bridge):** Valida se a ponte do Antigravity no TypeScript (`antigravity-bridge.ts`) reconhece e prioriza a orquestração do `marceloclaro` com prioridade crítica.

## 5. Refinamento de Integração TUI
O menu interativo (`menu.py`) foi refinado com a ação global `iniciar_marceloclaro`, que executa o `opencode` pré-configurado com a opção `--agent marceloclaro` no diretório de projetos. O item MarceloClaro na categoria Estratégia dispara automaticamente essa orquestração direta em vez de permanecer inativo.

