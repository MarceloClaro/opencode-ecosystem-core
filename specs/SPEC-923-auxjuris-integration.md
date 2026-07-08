# SPEC-923: Integração AUXJURIS — Agentes Jurídicos, RAG e Webapp

**STATUS**: IMPLEMENTADO
**DATA**: 2026-07-08
**AUTOR**: marceloclaro
**VERSÃO**: 1.0

## 1. Objetivo

Integrar as capacidades do **AUXJURIS** (assistente jurídico inteligente com React/TypeScript, multi-agentes, RAG por keywords e LLM on-device via MediaPipe/Gemma) ao OpenCode Ecosystem Core, expandindo o módulo `legal/` com:

1. **4 agentes jurídicos especializados** no catálogo OpenCode (A2A)
2. **Base de conhecimento jurídico** com RAG por keywords + Datajud
3. **Sumarizador de documentos jurídicos** com análise de precedentes
4. **Ponte para webapp** (UI React → MetaBus/Blackboard)

## 2. Integração com AuxJuris

| AuxJuris Feature | OpenCode Equivalente | Melhoria |
|---|---|---|
| 4 agents (system prompts) | `agents/catalog/` + `legal/agents.py` | Agentes jurídicos registrados no A2A |
| RAG por keywords | `rag/` + `legal/knowledge_base.py` | RAG jurídico híbrido (keywords + vetores) |
| KnowledgeDocument | `legal/knowledge_base.py` | Base expansível com dados do Datajud |
| Gemini API + MediaPipe | `integrations/` | Provider on-device opcional |
| UI React/TypeScript | `webapp/` | Blueprint de integração frontend |
| Sumarização de documentos | `legal/summarizer.py` | Pipeline com PrecedentAnalyzer |

## 3. Agentes Jurídicos (Catálogo OpenCode)

| # | Agente | ID | Função |
|---|---|---|---|
| 1 | **Assistente Jurídico Geral** | `auxjuris_legal_assistant` | Informações jurídicas, análise de casos, subsunção |
| 2 | **Sumarizador de Documentos** | `auxjuris_document_summarizer` | Resumo de petições, contratos, ementas |
| 3 | **Redator de E-mail Jurídico** | `auxjuris_email_drafter` | Minutas de comunicação profissional |
| 4 | **Analista de Pesquisa Jurídica** | `auxjuris_legal_research` | Pesquisa em base de conhecimento + Datajud |

## 4. Módulos Implementados

| Módulo | Descrição |
|---|---|
| `legal/agents.py` | Mapeamento A2A dos 4 agentes, construtor de Agent Cards, resolvedor por especialidade |
| `legal/knowledge_base.py` | Base de conhecimento jurídico com documentos indexados por keywords + conteúdo, RAG contextual, integração com Datajud |
| `legal/summarizer.py` | Sumarizador de documentos jurídicos com compressão por relevância e análise de precedentes |

## 5. Critérios de Aceitação (TDD)

1. Agentes: 4 agentes registrados com IDs, nomes, descrições e system prompts
2. `LegalKnowledgeBase.add_document()` adiciona documento com keywords
3. `LegalKnowledgeBase.search()` retorta documentos por keyword match
4. `LegalKnowledgeBase.search()` aplica RAG contextual com limite de caracteres
5. `LegalKnowledgeBase.rag_context()` monta prompt com contexto jurídico
6. `LegalDocumentSummarizer.summarize()` retorna resumo conservando pontos essenciais
7. `LegalDocumentSummarizer.summarize()` extrai entidades jurídicas (leis, artigos)
8. `AgentResolver.resolve()` retorna agente por especialidade
9. `AgentResolver.get_agent_card()` retorna Agent Card compatível com A2A
10. `LegalKnowledgeBase.load_from_datajud()` carrega documentos do Datajud
