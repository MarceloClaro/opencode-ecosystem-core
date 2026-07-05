# SPEC-036: Master Orchestrator (PhD & Polimata Ecosystem)

## 1. Visão Geral
O `MasterOrchestrator` é o agente supremo e central do OpenCode Ecosystem, responsável por iniciar, gerenciar e finalizar tarefas complexas que englobam todo o ecossistema (PhD e Polimata). Ele atua como a camada hierárquica máxima de controle do ciclo de vida, orquestrando recursos nativos do ecossistema e delegando sub-tarefas para orquestradores de subnível como `StageOrchestrator` e `AntigravityOrchestrator`.

## 2. Metas e Objetivos
* **Único Ponto de Entrada:** Fornecer um único ponto focal para iniciar e finalizar operações complexas.
* **Orquestração Omnipresente:** Integrar a inteligência do ecossistema PhD (matemática, física, metodologia) com o ecossistema Polimata (ferramentas amplas, navegação).
* **Conformidade TDD e SDD:** Assegurar o uso estrito de Desenvolvimento Orientado a Documentação de Software (SDD) antes do Desenvolvimento Orientado a Testes (TDD).
* **Auditoria e Reprodutibilidade:** Garantir que todo o processo seja 100% auditável, documentado minuciosamente para atualizar e integrar continuamente à dissertação de mestrado.

## 3. Arquitetura do Agente
* **Arquivo Base:** `agents/master-orchestrator.md`
* **Dependências de Delegação:** 
  1. `stage-orchestrator.md`: Para fluxos estruturados (8-stage pipeline).
  2. `antigravity-orchestrator.md`: Para tarefas além das capacidades de terminal estrito do OpenCode.
  3. Módulo `MCSP Solver` & `CrossValidationEngine`: Para resolução de precedências de tarefas e validações de coerência epistemológica.
* **Outputs:**
  - Plano de Execução SDD (Software Design Document).
  - Atualizações no `ecosystem-state.json`.
  - Relatórios de Execução Consolidada para Auditoria.

## 4. Workflow (Ciclo de Vida E2E)
O MasterOrchestrator segue 5 etapas obrigatórias:
1. **Intenção e Triagem (Initiation):** Análise do comando do usuário e formulação de plano macro-estratégico via SDD.
2. **Setup de Auditoria (Audit Prep):** Inicialização do rastreador de sessões para reprodutibilidade rigorosa.
3. **Distribuição e Execução (Execution):** Invocação de subagentes ou suborquestradores de acordo com a natureza da demanda.
4. **Validação Rigorosa (TDD Validation):** Exigência de que todas as sub-entregas possuam cobertura de testes comprovada.
5. **Encerramento e Documentação (Finalization):** Consolidação dos resultados em artefatos, log final do pipeline e atualizações nas seções da dissertação (resultados/metodologia).

## 5. TDD e SDD
Casos de Teste esperados (`tests/test_master_orchestrator.py`):
* **CT-3601 (Inicialização SDD):** Verifica se a intenção foi traduzida em um artefato estruturado SDD antes da execução.
* **CT-3602 (Delegação e Roteamento):** Testa se a tarefa é corretamente ramificada e atribuída aos sub-orquestradores adequados.
* **CT-3603 (Conformidade de Auditoria):** Garante que cada etapa de transição registre log imutável no state local.
* **CT-3604 (Fechamento e Consolidação):** Valida a emissão de relatórios de conclusão e status `completed` da tarefa mestre.
