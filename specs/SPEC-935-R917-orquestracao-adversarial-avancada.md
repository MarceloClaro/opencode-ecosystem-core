---
spec_id: SPEC-935-R917
title: Orquestração Avançada e Rastreio A2A/MetaBus para Rigor Acadêmico Adversarial
component: academic.adversarial_research
status: proposed
test_file: tests/test_r917_academic_orchestration.py
---

# R917 — Orquestração Avançada e Rastreio A2A/MetaBus

## 1. Objetivo
Expandir e solidificar a integração do módulo de rigor acadêmico adversarial (`academic.adversarial_research`) diretamente no `MarceloClaroOrchestrator`, utilizando o Blackboard (A2A), o MetaBus (memória metacognitiva compartilhada), o Trust Engine e o SpecVerifier (contratos SDD).

## 2. Requisitos Funcionais
- **RF-01:** O orquestrador primário `MarceloClaroOrchestrator` expõe o método `run_academic_adversarial_review(project, **limits)` que executa o pipeline de revisão por especialistas de forma auditável e com rastreio de tarefas no Blackboard.
- **RF-02:** Cada tarefa iniciada por especialista registra sua intenção no Blackboard com contrato SDD verificado por `SpecVerifier`.
- **RF-03:** O resultado de cada etapa é publicado no MetaBus com escopo de contrato (`contract_only`), evitando poluição ou recompensa indevida de confiança sem evidência externa.
- **RF-04:** Tratamento robusto de cancelamento, timeout, orçamento de passos e artefatos truncados, gerando gaps informativos rastreáveis.
- **RF-05:** Conformidade estrita com o princípio anti-overclaim (nenhuma revisão local substitui revisão humana ou validação científica externa).
- **RF-06:** Separar `local_checks` de tarefas delegadas a perfis gerenciados; ausência de perfil deve ser reportada, não ocultada.
- **RF-07:** Não concluir tarefas Blackboard nem atribuir inferência a agente quando apenas o verificador local executou.
- **RF-08:** Preservar no recibo hashes do artefato, escopo da execução e observação MetaBus sem promoção de confiança.

## 3. Critérios de Aceitação (CA)
- `R916-AC1`: Chamadas ao pipeline acadêmico pelo orquestrador primário registram rastreio completo no Blackboard e MetaBus.
- `R916-AC2`: Orçamento de passos (`max_steps`) e timeout são rigorosamente respeitados, interrompendo a execução de forma limpa.
- `R916-AC3`: Testes de integração cobrem falhas, cancelamentos e validam o comportamento esperado (RED → GREEN).
- `R916-AC4`: Uma revisão local não emite `task.complete` em nome de especialista, não fecha tarefa A2A e declara `agent_inference_executed=false`.
- `R916-AC5`: Inventário distingue definições no registro de perfis gerenciados validados no catálogo físico.
- `R916-AC6`: Falha/ausência de perfil produz resultado explícito `profile_unavailable`/`dispatch_blocked`, sem tarefa ou inferência fabricada.
- `R916-AC7`: Revisão registra observação MetaBus com hashes, escopo e `confidence_promoted=false`; não promove aprovação científica.

## 4. Limites
Esta extensão não escolhe nem troca provedores/modelos automaticamente, não prova que tarefa pendente foi executada e não representa calibração científica. Seleção por custo de tokens e proveniência de mapas são escopos separados, a formalizar antes de implementação.
