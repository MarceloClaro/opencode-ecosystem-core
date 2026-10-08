---
spec_id: SPEC-935-R663
title: Percurso cientifico reprodutivel com proveniencia explicita
status: green
validation_scope: local_runtime
release_gate: docs/evidence/R663_R666_RELEASE_GATE.json
component: research/provenance_pipeline.py + research/statistical_methods.py + research/hub.py + skills/tooling/data_knowledge_hub/datasets.py + agentic_science_v2/deep_research.py + mci/pipeline/scientific_governance_pipeline.py
test_file: tests/test_r663_scientific_provenance.py
---

# R663 — Pesquisa com fontes, dados e execução rastreáveis

## Contratos

1. Uma API delimitada liga pergunta, referências coletadas ou snapshots
   identificados, CSV real declarado com origem, método prespecificado,
   execução estatística, reprodução em processo separado e relatório/artigo
   Markdown. Não aceita código arbitrário, dados demonstrativos ou resultados
   provenientes de fallback como evidência de execução real.
2. Métodos internos: descrição numérica, correlação de Pearson com teste de
   permutação e comparação de dois grupos por Welch. A saída declara premissas,
   limitações, hipótese nula, estimativa, incerteza e ausência de inferência causal.
3. CSV, referências, configuração e código gerado têm snapshots e SHA-256.
   Ausência de fonte, alteração de hash, números não finitos ou schema inválido
   bloqueiam antes da criação de artefatos. Proveniência declarada de um arquivo
   não é certificação independente da origem dos dados.
4. Reprodução executa somente o script interno gerado; compara resultados e
   hash do dataset. Revisão computacional não é revisão humana por pares.
5. Fontes de datasets indisponíveis retornam erro/vazio por padrão. Exemplos
   demonstrativos continuam acessíveis somente por opção explícita e carregam
   evidence_kind=demonstration, synthetic=true, evidence_eligible=false.
6. ResearchHub preserva status, tipo de evidência e proveniência do DataKnowledgeHub.
   Dados offline/demonstrativos permanecem no diagnóstico, sem serem promovidos
   a resultados elegíveis para evidência científica.
7. O Deep Research legado conserva sua demonstração, com status=simulation,
   evidence_eligible=false, executed=false e verified=false. Não registra sucesso
   real de código/API. Governança sem executor bloqueia antes de gerar claims;
   com callable, identifica números reportados separadamente de um experimento.

## Critérios executáveis

- `R663-PROVENANCE` — snapshots, hashes e proveniência são obrigatórios e preservados.
- `R663-EXECUTION` — análises delimitadas coincidem com estatísticas de referência.
- `R663-REPRODUCTION` — outro processo reproduz resultado e detecta alteração do CSV.
- `R663-ABSTENTION` — fonte inválida ou simulada bloqueia; fallback não fabrica evidência.
- `R663-REPORT` — artigo e código contêm resultados executados, limites e revisão computacional.
- `R663-LEGACY` — simulações e executores ausentes não podem produzir sucesso científico.

## Validação

Testes herméticos usam fixtures explicitamente artificiais para verificar
contratos, sem promover essas fixtures a evidência de pesquisa externa.
O probe real coleta o arquivo bezdekIris.data diretamente da UCI e metadados
bibliográficos HTTP coletados durante a execução; não usa API paga ou LLM.
Pearson usa 150 registros; Welch usa o subconjunto prespecificado de duas
espécies, com 100 registros. Ambos são reproduzidos em processos separados.
