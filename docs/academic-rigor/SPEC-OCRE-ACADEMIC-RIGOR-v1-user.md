# SPEC-OCRE-ACADEMIC-RIGOR v1.0

Sistema Multiagente de Pesquisa Científica, Auditoria Adversarial e Bancas Examinadoras

Especificação proposta — não implementada

Identifiquei o repositório MarceloClaro/opencode-ecosystem-core e sua arquitetura existente. O OCRE já possui um orquestrador principal `marceloclaro`, comunicação por Blackboard e MetaBus, catálogo de agentes, contratos SDD/TDD, mecanismos de evidência e testes.

Portanto, a solução deve estender o ecossistema existente, e não criar um segundo orquestrador independente ou simplesmente adicionar dezenas de prompts sem integração operacional.

A especificação será fundamentada nas oito questões de banca do material fornecido, que abrangem originalidade, justiça epistêmica, amostragem, inferência causal, ética indígena, integridade de publicações, viabilidade e aderência institucional. Esses temas serão transformados em verificações reutilizáveis para pesquisas de diferentes áreas, não apenas para o caso UNILAB.

Objetivo: sempre que o OCRE desenvolver ou avaliar uma pesquisa, deverá formular críticas metodológicas rigorosas, buscar evidências que possam refutar hipóteses, explicitar fragilidades e só liberar conclusões proporcionais às provas disponíveis.

A inspeção também identificou um componente que deve ser reaproveitado: o SPEC-935-R439 — RigorousBoard, que já define revisão crítica, classificação de falhas e ciclos de correção. A nova arquitetura deverá acrescentar agentes de investigação epistemológica, metodológica e adversarial, preservando a compatibilidade com esse módulo e com a SPEC-006 — Protocolo SDD/TDD dos agentes.

# SPEC-OCRE-ACADEMIC-RIGOR v1.0

**Projeto:** OpenCode Ecosystem Core (OCRE)\
**Componente:** Sistema Multiagente de Rigor Científico Adversarial\
**Estado:** PROPOSED — implementação pendente\
**Padrão:** SDD + TDD + A2A + Evidence-First\
**Identificador definitivo:** reservar próximo número livre na série `SPEC-935-R*`.

## 1. Objetivo

Implementar um sistema de especialistas científicos capaz de analisar projetos, dissertações, teses, artigos, protocolos e resultados de pesquisa com rigor equivalente ao de uma banca examinadora crítica.

O sistema deverá identificar fragilidades científicas, formular objeções fundamentadas, confrontar as respostas do pesquisador, exigir evidências apropriadas e propor correções verificáveis.

**Princípio fundamental:** nenhum agente poderá transformar hipóteses em resultados, plausibilidade em comprovação, métricas técnicas em validade científica ou publicação em certificação automática de qualidade.

## 2. Requisitos funcionais

| ID    | Requisito obrigatório                                                                                         |
| ----- | ------------------------------------------------------------------------------------------------------------- |
| RF-01 | Decompor toda investigação em problema, objetivos, teorias, hipóteses, procedimentos, evidências e conclusões |
| RF-02 | Verificar originalidade e lacunas perante literatura recuperada                                               |
| RF-03 | Formular objeções científicas potencialmente capazes de modificar ou refutar alegações                        |
| RF-04 | Detectar confusões conceituais e falhas de operacionalização                                                  |
| RF-05 | Examinar amostragem, unidades de análise, corpus e validade                                                   |
| RF-06 | Separar associação, mudança observada e inferência causal                                                     |
| RF-07 | Verificar ética, proteção de dados e autoridade sobre conhecimentos culturalmente sensíveis                   |
| RF-08 | Auditar artigos, referências, métricas e resultados computacionais                                            |
| RF-09 | Avaliar cronogramas, recursos, riscos e dependências                                                          |
| RF-10 | Verificar aderência a programas, editais e áreas científicas                                                  |
| RF-11 | Conduzir bancas interativas, uma pergunta por vez, com réplicas                                               |
| RF-12 | Emitir relatórios com evidências, limitações e correções propostas                                            |
| RF-13 | Integrar Blackboard, MetaBus, RigorousBoard e SpecVerifier                                                    |
| RF-14 | Executar testes RED/GREEN e manter rastreabilidade de cada decisão                                            |
| RF-15 | Adaptar a matriz de avaliação ao projeto, à instituição e ao domínio científico                               |

## 3. Arquitetura dos 34 agentes especializados

Os agentes serão organizados em sete núcleos. Cada agente deverá possuir identificador único, responsabilidade delimitada, contrato de entrada, contrato de saída, restrições e testes específicos.

### Núcleo A — Coordenação e rastreabilidade

| ID  | Agente                        | Responsabilidade                                                                                    |
| --- | ----------------------------- | --------------------------------------------------------------------------------------------------- |
| A01 | `research-intake-auditor`     | Identificar documentos, objetivos, restrições, lacunas de contexto e tipos de evidência disponíveis |
| A02 | `research-problem-decomposer` | Decompor o problema em perguntas verificáveis e dependências científicas                            |
| A03 | `research-evidence-ledger`    | Registrar alegações, fontes, localizadores, status de verificação e decisões                        |
| A04 | `research-banca-chair`        | Coordenar especialistas e consolidar objeções sem substituir o orquestrador primário                |

### Núcleo B — Originalidade e epistemologia

| ID  | Agente                                | Responsabilidade                                                                            |
| --- | ------------------------------------- | ------------------------------------------------------------------------------------------- |
| A05 | `research-gap-verifier`               | Identificar lacunas e exigir sustentação bibliográfica                                      |
| A06 | `research-novelty-opponent`           | Contestar alegações de originalidade e distinguir novidade teórica, metodológica e empírica |
| A07 | `research-concept-genealogist`        | Analisar origem, significado, pressupostos e limites dos conceitos                          |
| A08 | `research-operationalization-auditor` | Converter construtos teóricos em indicadores observáveis, verificando erros categoriais     |
| A09 | `research-rival-hypotheses`           | Propor explicações alternativas e buscar condições capazes de contrariar hipóteses          |

### Núcleo C — Desenho metodológico e validade

| ID  | Agente                              | Responsabilidade                                                                             |
| --- | ----------------------------------- | -------------------------------------------------------------------------------------------- |
| A10 | `research-sampling-auditor`         | Examinar amostragem, seleção, tamanho, suficiência informacional e vieses                    |
| A11 | `research-corpus-auditor`           | Conferir unidades, contagens, dependências e critérios de composição de corpus               |
| A12 | `research-model-variance-auditor`   | Examinar variabilidade de IA, versões, parâmetros, repetições e condições de execução        |
| A13 | `research-causal-inference-skeptic` | Identificar inferências causais indevidas, confundidores e efeito de teste                   |
| A14 | `research-instrument-calibrator`    | Avaliar rubricas, instrumentos, comparabilidade, piloto e consistência                       |
| A15 | `research-triangulation-auditor`    | Analisar convergências, divergências e limitações entre fontes e métodos                     |
| A16 | `research-interrater-auditor`       | Examinar revisão independente, desacordos e consistência de classificação                    |
| A17 | `research-transferability-auditor`  | Distinguir generalização estatística, analítica, transferibilidade e extrapolações indevidas |

### Núcleo D — Ética, direitos e governança

| ID  | Agente                                   | Responsabilidade                                                                                         |
| --- | ---------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| A18 | `research-human-ethics-auditor`          | Verificar consentimento, recrutamento, relações hierárquicas e avaliação ética aplicável                 |
| A19 | `research-indigenous-governance-auditor` | Examinar autoridade comunitária, protocolos próprios, conhecimentos coletivos e autorizações pertinentes |
| A20 | `research-data-governance-auditor`       | Examinar confidencialidade, minimização, retenção, acesso, LGPD e segurança                              |
| A21 | `research-epistemic-extraction-watchdog` | Identificar riscos de apropriação de conhecimentos, silenciamento e representação indevida               |

### Núcleo E — Fontes, resultados e reprodutibilidade

| ID  | Agente                                  | Responsabilidade                                                                        |
| --- | --------------------------------------- | --------------------------------------------------------------------------------------- |
| A22 | `research-source-provenance-auditor`    | Verificar origem, autenticidade, rastreabilidade e pertinência de evidências            |
| A23 | `research-citation-integrity-auditor`   | Detectar referências não verificadas, citações inadequadas e extrapolação de fontes     |
| A24 | `research-computational-claims-auditor` | Auditar alegações envolvendo IA, embeddings, métricas, código e estatísticas            |
| A25 | `research-reproducibility-auditor`      | Exigir protocolos, versões, parâmetros, dados e procedimentos de reprodução pertinentes |
| A26 | `research-negative-cases-auditor`       | Buscar casos contraditórios, resultados nulos e evidências desfavoráveis às hipóteses   |

### Núcleo F — Viabilidade científica

| ID  | Agente                             | Responsabilidade                                                       |
| --- | ---------------------------------- | ---------------------------------------------------------------------- |
| A27 | `research-timeline-auditor`        | Examinar cronograma, precedências, caminho crítico e entregas          |
| A28 | `research-operational-feasibility` | Analisar disponibilidade, custos, infraestrutura e acesso ao campo     |
| A29 | `research-contingency-auditor`     | Construir cenários de atraso, indisponibilidade e revisão metodológica |

### Núcleo G — Aderência e defesa científica

| ID  | Agente                                 | Responsabilidade                                                                      |
| --- | -------------------------------------- | ------------------------------------------------------------------------------------- |
| A30 | `research-institutional-fit-auditor`   | Confrontar projeto com edital, linha de pesquisa, programa e missão institucional     |
| A31 | `research-interdisciplinarity-auditor` | Verificar integração efetiva de disciplinas, e não apenas justaposição de referências |
| A32 | `research-adversarial-examiner`        | Formular perguntas difíceis e réplicas vinculadas a fragilidades específicas          |
| A33 | `research-rubric-scoring-auditor`      | Aplicar rubricas declaradas, justificar pontuações e registrar ausência de observação |
| A34 | `research-remediation-planner`         | Propor revisões proporcionais aos problemas detectados e encaminhar reavaliação       |

**Restrição arquitetural:** A04 será um coordenador científico subordinado ao `MarceloClaroOrchestrator`. Não poderá assumir a função de orquestrador global, alterar políticas centrais ou iniciar ferramentas privilegiadas fora do roteamento autorizado.

## 4. Protocolo de operação dos agentes

Cada especialista deverá executar um ciclo padronizado:

1. Identificar a alegação ou decisão metodológica a examinar.
2. Recuperar a evidência disponível, sem pressupor que exista.
3. Formular ao menos uma objeção específica e testável.
4. Determinar que evidência resolveria ou reduziria a objeção.
5. Examinar hipóteses e interpretações alternativas.
6. Classificar severidade e incerteza.
7. Emitir recomendação com fundamento verificável.
8. Encaminhar sua saída ao registro compartilhado e ao coordenador.

A objeção deverá ser proporcional ao domínio e ao objetivo. Por exemplo, uma pesquisa qualitativa não deverá ser rejeitada automaticamente por não possuir cálculo de poder estatístico; uma pesquisa causal, por outro lado, deverá demonstrar condições adequadas de identificação causal.

## 5. Matriz obrigatória de questionamento científico

Cada projeto deverá ser submetido a oito famílias de perguntas, com adaptação ao contexto.

| Eixo                   | Pergunta adversarial obrigatória                                                  |
| ---------------------- | --------------------------------------------------------------------------------- |
| Originalidade          | Qual lacuna comprovadamente permanece e o que este estudo acrescentará?           |
| Epistemologia          | Os conceitos foram operacionalizados corretamente ou existem erros categoriais?   |
| Amostragem             | O desenho permite sustentar as inferências propostas?                             |
| Validade               | As evidências distinguem mudança, associação, explicação e causalidade?           |
| Ética                  | Quem pode participar, consentir, interpretar e autorizar o uso dos conhecimentos? |
| Integridade científica | Os resultados são observados, simulados, hipotéticos ou reproduzidos?             |
| Viabilidade            | Existem tempo, recursos, dependências resolvidas e contingências proporcionais?   |
| Aderência              | Por que este problema exige a abordagem científica e institucional escolhida?     |

Em cada eixo, gerar no mínimo uma questão central, uma réplica metodológica e uma condição explícita de resolução.

Não gerar perguntas artificialmente agressivas, sem pertinência científica ou baseadas em premissas falsas.

## 6. Contratos de dados

### ResearchClaim

Campos obrigatórios:

- `claim_id`
- `statement`
- `claim_type`: factual, teórica, metodológica, inferencial ou normativa
- `source_refs`
- `evidence_status`: verified, reported, proposed, hypothetical, contradicted, insufficient ou not_checked
- `limitations`
- `reviewer_agent_ids`

### AdversarialObjection

Campos obrigatórios:

- `objection_id`
- `target_claim_ids`
- `question`
- `scientific_rationale`
- `required_evidence`
- `severity`: critical, major, minor ou advisory
- `uncertainty`
- `source_refs`
- `responsible_agent`

### ResearchReview

Campos obrigatórios:

- `research_id`
- `spec_id`
- `reviewed_artifact_hash`
- `claims`
- `objections`
- `unresolved_gaps`
- `recommended_actions`
- `evidence_manifest`
- `review_status`
- `human_review_required`

Toda objeção deverá apontar para a alegação examinada. Referências sem identificador ou localizador não poderão receber status de verificação concluída.

## 7. Orquestração A2A

Fluxo obrigatório:

**marceloclaro → Research Intake → Evidence Ledger → especialistas selecionados → Adversarial Examiner → RigorousBoard → Remediation Planner → SpecVerifier → revisão humana → entrega.**

Os especialistas poderão operar em etapas paralelas quando não houver dependência lógica entre suas análises.

O orquestrador deverá selecionar agentes conforme o tipo de estudo. Não será obrigatório executar os 34 agentes em toda pesquisa.

Exemplos de roteamento:

- Pesquisa bibliográfica: originalidade, conceitos, fontes, referências, síntese e casos contraditórios.
- Pesquisa qualitativa com pessoas: acrescentar amostragem, ética, instrumentos, triangulação e transferibilidade.
- Pesquisa experimental: acrescentar identificação causal, confundidores, controles e reprodutibilidade.
- Pesquisa com IA: acrescentar auditoria computacional, variabilidade, benchmarks e proveniência.
- Pesquisa sobre conhecimentos indígenas: acrescentar governança comunitária, autoridade interpretativa e riscos de extração.
- Preparação de banca: acrescentar examinador adversarial, pontuação por rubrica e revisão das respostas.

## 8. Gates de qualidade

**G0 — Especificação:** objetivo, escopo, perguntas e critérios de aceitação formalizados.

**G1 — Evidências:** fontes recuperadas e alegações mapeadas; lacunas não verificadas explicitadas.

**G2 — Método:** coerência entre pergunta, desenho, participantes, instrumentos e inferências.

**G3 — Ética:** ausência de violações identificadas e encaminhamento de exigências pendentes. Nenhum parecer automatizado substitui avaliação ética institucional.

**G4 — Auditoria adversarial:** objeções críticas enfrentadas com evidências ou registradas como impedimentos.

**G5 — Conclusões:** resultados proporcionais às evidências, com limitações e interpretações rivais.

**G6 — Entrega:** testes executados, recibos registrados e revisão humana quando exigida.

O sistema poderá entregar um relatório de pesquisa com pendências, mas não poderá classificá-lo como aprovado ou validado quando houver impedimentos críticos não resolvidos.

## 9. Modo de banca examinadora

O sistema deverá oferecer simulação interativa independente da auditoria documental.

Regras:

- Exibir uma pergunta por vez.
- Aguardar resposta real do candidato.
- Formular réplica coerente com a resposta recebida.
- Não divulgar resposta-modelo antes da tentativa, salvo solicitação.
- Registrar objeções não respondidas.
- Avaliar exclusivamente competências observadas.
- Produzir feedback específico, correções sugeridas e relatório final.

Rubricas institucionais deverão ser carregadas de documentos verificados; critérios não deverão ser inventados.

Para o caso de referência MIH/UNILAB, a rubrica de treinamento será composta por cinco dimensões de até 2 pontos: clareza e argumentação; fundamentação teórica e metodologia; trajetória acadêmico-profissional; produção científica e aderência; interdisciplinaridade e disponibilidade.

A nota será apenas simulada. Aspectos não observados deverão permanecer explicitamente identificados, sem atribuição fictícia de desempenho.

## 10. Integração com o código existente

Reaproveitar prioritariamente:

- `marceloclaro/orchestrator.py` — coordenação primária.
- `academic/rigorous_board.py` — auditoria existente, a ser ampliada por adaptadores.
- `academic/maswos.py` — integração com produção acadêmica.
- `agents/catalog/` — descritores dos especialistas.
- `sdd/spec_engine.py` — contratos SDD e verificação.
- Blackboard e MetaBus — comunicação, estado e evidências.
- `integrations/opencode_cli.py` — compilação da configuração.

Componentes novos sugeridos, sujeitos à verificação de conflitos com módulos existentes:

- `academic/adversarial_research/contracts.py`
- `academic/adversarial_research/registry.py`
- `academic/adversarial_research/router.py`
- `academic/adversarial_research/evidence.py`
- `academic/adversarial_research/board.py`
- `academic/adversarial_research/scoring.py`
- `academic/adversarial_research/guards.py`

Não editar diretamente arquivos gerados quando existir gerador oficial. O catálogo será a fonte primária dos novos descritores, sujeito aos padrões do repositório.

## 11. Critérios de aceitação

| ID    | Critério verificável                                                                                      |
| ----- | --------------------------------------------------------------------------------------------------------- |
| CA-01 | Todos os agentes declarados possuem identificadores exclusivos e manifesto válido                         |
| CA-02 | Todo agente possui limites de competência, entradas, saídas e protocolo SDD/TDD                           |
| CA-03 | Nenhum subagente ignora o orquestrador primário                                                           |
| CA-04 | O pipeline preserva origem e evidência para alegações factuais                                            |
| CA-05 | Uma pesquisa sem fontes suficientes não é classificada como cientificamente comprovada                    |
| CA-06 | O auditor de IA rejeita equivalência entre similaridade de cosseno de 0,90 e 90% de precisão de tradução  |
| CA-07 | O auditor de corpus distingue 192 respostas planejadas de 192 observações independentes                   |
| CA-08 | O auditor causal identifica limites de estudos antes/depois sem controle                                  |
| CA-09 | O auditor ético não considera publicação pública autorização irrestrita para uso de conhecimento sensível |
| CA-10 | A banca apresenta exatamente uma questão por vez no modo interativo                                       |
| CA-11 | A pontuação não inclui competências sem evidência de desempenho                                           |
| CA-12 | Nenhum relatório omite pendências críticas ou incertezas relevantes                                       |
| CA-13 | A auditoria especializada não quebra o `RigorousBoard` existente                                          |
| CA-14 | Configuração gerada, diagnóstico e testes de regressão permanecem consistentes                            |

## 12. TDD — Testes obrigatórios

Implementar testes unitários, de integração e de regressão para pelo menos os seguintes cenários:

- `test_critical_claim_without_evidence_is_blocked`
- `test_novelty_requires_literature_support`
- `test_operationalization_rejects_category_error`
- `test_corpus_count_distinguishes_independence`
- `test_causal_auditor_rejects_uncontrolled_effect_claim`
- `test_llm_cosine_similarity_not_translation_accuracy`
- `test_indigenous_governance_requires_contextual_review`
- `test_unverified_citation_not_promoted_to_verified`
- `test_negative_evidence_not_suppressed`
- `test_examiner_waits_for_candidate_answer`
- `test_scoring_marks_unobserved_competence`
- `test_blackboard_metabus_evidence_trace`
- `test_existing_rigorous_board_backward_compatibility`
- `test_agent_registry_no_duplicate_ids`
- `test_budget_timeout_and_cancellation`
- `test_sdd_green_without_fabricated_external_validation`

Cada teste deverá possuir condição RED verificável antes da implementação e evidência GREEN após a correção.

## 13. Benchmark derivado das oito questões

Construir um conjunto de testes de referência inspirado no material fornecido, sem tratar respostas-modelo como gabaritos científicos infalíveis.

Casos positivos e negativos:

- Originalidade: novo território não comprova inovação.
- Justiça epistêmica: erro factual isolado não comprova injustiça.
- Corpus: contagem correta não garante independência.
- Oficinas: diferenças antes/depois não identificam causalidade automaticamente.
- Conhecimentos indígenas: fonte pública não elimina responsabilidades éticas.
- Dzubukuá: métricas computacionais não comprovam reconstrução linguística.
- Viabilidade: cronograma não comprova liberação profissional.
- Aderência institucional: afinidade conceitual não equivale a pesquisa internacional empírica.

Para cada caso, testar detecção, justificativa, evidência solicitada, classificação de gravidade e presença de uma objeção adversarial cientificamente válida.

## 14. Plano de implementação

**Fase 1 — Inventário e compatibilidade:** localizar agentes existentes, identificar competências duplicadas, reservar identificador SPEC e escrever testes RED.

**Fase 2 — Contratos e primeiros agentes:** implementar os componentes de evidência, originalidade, método e auditoria de alegações. Priorizar integração real em vez de expansão nominal do catálogo.

**Fase 3 — Especialização:** incorporar ética, governança, revisão interavaliadores, viabilidade e aderência institucional.

**Fase 4 — Banca interativa:** implementar perguntas progressivas, réplicas, registro de respostas e rubricas verificadas.

**Fase 5 — Integração e regressão:** executar SpecVerifier, TDD, diagnóstico, compilação da configuração, testes de compatibilidade e auditoria de permissões.

**Fase 6 — Avaliação científica:** revisar casos com especialistas humanos, medir falhas de detecção e falsos positivos, registrar limites e aprovar implantação gradual.

## 15. Entregáveis

- SPEC aprovada e versionada.
- Inventário de agentes reutilizados e novos.
- Catálogo de especialistas com contratos explícitos.
- Motor de roteamento adversarial.
- Registro de evidências e alegações.
- Banco de casos científicos de referência.
- Simulador de banca examinadora.
- Adaptador para `RigorousBoard`.
- Suíte TDD e testes de regressão.
- Relatório de avaliação com erros conhecidos.
- Guia de ativação, desativação e recuperação.

## 16. Definição de conclusão

A funcionalidade somente será considerada implementada quando os especialistas puderem receber uma pesquisa real, produzir objeções rastreáveis, detectar alegações sem evidência, registrar réplicas, executar testes de regressão e entregar relatório que distinga fatos verificados, hipóteses, resultados relatados e limitações.

**A quantidade de agentes registrados não constituirá evidência de capacidade científica. A capacidade dependerá do comportamento efetivamente testado e de revisão especializada.**

## Exemplo de manifesto para geração de um agente

Este é um modelo inicial compatível com as convenções observadas no catálogo, sujeito à validação pelo gerador do repositório. Os agentes restantes deverão ser derivados do mesmo contrato, com competências e testes próprios.

```

---
id: research-causal-inference-skeptic
agent_id: research-causal-inference-skeptic
name: Research Causal Inference Skeptic
description: >
  Auditor adversarial de causalidade, confundimento,
  efeitos de teste, validade interna e inferências indevidas.
version: "1.0.0"
mode: subagent
category: academic
capabilities:
  - causal_inference_audit
  - design_validity
  - confounder_detection
  - counterargument_generation
  - evidence_gap_reporting
---

# Missão

Examinar se as conclusões causais são sustentadas
pelo delineamento, pelas observações e pelo controle
dos fatores alternativos.

# Entradas

- research_question
- study_design
- variables
- observations
- claimed_effects
- supporting_sources

# Saídas

- detected_issues
- adversarial_questions
- rival_explanations
- missing_evidence
- methodological_limitations
- decision

# Invariantes

1. Não inferir causalidade apenas de correlação.
2. Não atribuir efeitos exclusivamente à intervenção
   em estudos antes/depois sem identificação adequada.
3. Não inventar grupos de controle nem variáveis medidas.
4. Distinguir observações, interpretações e hipóteses.
5. Documentar evidências que contrariem a tese inicial.

# Protocolo SDD

Derivar requisitos, critérios de aceitação,
invariantes e não-objetivos antes da análise.

# Protocolo TDD

Executar os casos adversariais definidos na SPEC.
Registrar RED, GREEN e resultado de regressão.
Nunca declarar sucesso sem evidência dos testes.

# Gate de saída

Bloquear aprovação científica quando uma conclusão
causal depender de evidências ausentes.
Permitir relatório de pendências com status explícito.

```

## Ordem recomendada de implantação

O OCRE já contém uma banca rigorosa de manuscritos e agentes acadêmicos; por isso, não recomendo registrar os 34 de imediato. Primeiro, implemente um piloto de oito especialistas, cobrindo evidências, originalidade, operacionalização teórica, amostragem, inferência causal, ética, auditoria computacional e exame adversarial. Após os testes de integração, expanda para os demais.

A SPEC aproveita a arquitetura existente sem presumir que os agentes foram instalados ou que seus testes já foram executados. Nenhuma alteração foi feita no repositório. A especificação está pronta para orientar sua próxima implementação no OpenCode Ecosystem Core.  