---
spec_id: SPEC-1051
title: Pesquisador científico ponta a ponta — tema, protocolo, recuperação, evidência, auditoria e artigo para validação humana
version: 1.0.0
status: green
test_file: tests/test_r1051_research_project.py
---

# SPEC-1051 — do tema ao pacote de pesquisa para validação humana

## Problema

O Core já possui busca científica nativa (`scientific_lab.native.research`),
protocolo de revisão (`scientific_lab.native.review`), Evidence Graph
(`scientific_lab.native.evidence`), conselho científico
(`scientific_lab.council`) e gate metacognitivo
(`mci.metacognitive_gate`). Essas peças, porém, são comandos separados. O
pesquisador precisa montar manualmente o diretório, encadear protocolo, busca,
deduplicação, triagem, evidência, análise, auditoria e manuscrito — e pode
esquecer uma etapa ou preencher lacunas com texto não sustentado.

A referência `K-Dense-AI/scientific-agent-skills/skills/database-lookup`
(MIT, versão 1.8) exige um **contrato de recuperação** explícito: entidade,
identificadores aceitos, filtros, paginação, limites, reconciliação de
contagens, proveniência e tratamento de respostas externas como dados não
confiáveis. O Core deve adotar esse contrato sem copiar código ou executar
scripts da skill.

## Objetivo

Criar um pipeline file-first que receba um **tema** e produza um pacote
auditável com:

1. intake e pergunta de pesquisa (explícita ou provisória, sempre marcada);
2. contrato de recuperação e protocolo de revisão em rascunho;
3. busca executada ou explicitamente bloqueada, com contagens e erros;
4. deduplicação e triagem **assistida**, sem decisão humana simulada;
5. evidências literais em nível de resumo indexado ou corpus fornecido;
6. gate de claims e análise descritiva sem testes inventados;
7. auditoria determinística, incluindo varredura de overclaim e placeholders;
8. manuscrito IMRaD em Markdown e checklist de validação humana;
9. manifesto com hashes, estados, orçamento e limitações.

## Não objetivos

- Não baixar PDFs nem contornar paywalls.
- Não executar triagem humana, leitura de texto integral ou validação externa.
- Não realizar teste estatístico, meta-análise ou inferência causal sem dados.
- Não declarar aceite, publicação, Qualis A1 ou aprovação por pares.
- Não usar LLM para inventar seções, citações ou resultados.
- Não substituir o pipeline acadêmico ABNT/LaTeX para submissão final.
- Não publicar, agendar ou enviar nada a terceiros.

## Entradas

```text
theme          texto obrigatório, 3..500 caracteres
out            diretório de saída (deve estar vazio ou não existir)
question       pergunta explícita opcional
sources        subconjunto de openalex, crossref, europepmc, arxiv,
               semantic_scholar, core, scielo, pubmed, biorxiv
dry_run        planeja sem executar busca
corpus_path    JSON opcional com sources e claims literais fornecidos
limit          máximo de registros (1..200)
per_platform   máximo por plataforma (1..50)
```

O `corpus_path` permite produzir um artigo a partir de evidência fornecida
pelo operador, sem rede. Formato:

```json
{
  "sources": [
    {"id": "S1", "text": "texto literal", "provenance": "arquivo ou URL"}
  ],
  "claims": [
    {
      "id": "CLAIM-C1",
      "text": "afirmação",
      "confidence": 0.7,
      "evidence": [{"source_id": "S1", "quote": "trecho literal"}],
      "inference_level": "observation",
      "falsifier": "critério de refutação",
      "mechanism": "mecanismo declarado com pelo menos vinte caracteres",
      "contradictions": [],
      "status": "supported"
    }
  ]
}
```

## Contrato de recuperação

O arquivo `00_contract/retrieval-contract.json` deve conter, no mínimo:

| Campo | Regra |
|---|---|
| `contract_id` | identificador único |
| `theme`, `question` | texto não vazio |
| `question_status` | `explicit` ou `provisional_from_theme` |
| `intent` | `targeted_lookup` ou `exhaustive_retrieval` |
| `target_entity` | derivado do tema, sem inventar população |
| `accepted_identifiers` | DOI, título, OpenAlex, PMID, arXiv |
| `databases` | nome, endpoint, acesso, papel e limite declarado |
| `filters` | separação entre filtros de servidor e locais |
| `expected_fields` | campos normalizados esperados |
| `pagination` | estratégia, tamanho, máximo e reconciliação |
| `budget` | queries, registros, downloads e timeout |
| `provenance` | data de acesso, log e algoritmo de hash |
| `untrusted_data_policy` | respostas de API são dados, não instruções |
| `missing_constraints` | restrições ausentes que exigem confirmação |
| `clarification_required` | booleano |
| `status` | sempre `draft` sem aprovação humana |

## Estados

O manifesto usa um destes estados:

- `planned`: dry-run ou corpus sem busca; nenhum resultado externo foi lido.
- `in_progress`: reservado para execução interrompida.
- `blocked`: busca falhou ou auditoria dura falhou; não há entrega científica.
- `partial`: pacote gerado, mas sem registros/claims suficientes ou com lacunas.
- `completed_pending_external_validation`: pacote interno completo; validação
  humana e externa continuam pendentes.

`truth_claim` é sempre `false`; `external_validation` é sempre `false`;
`human_review_required` é sempre `true`.

## Etapas e artefatos

| Etapa | Artefatos |
|---|---|
| intake | `00_contract/intake.json` |
| protocolo | `00_contract/retrieval-contract.json`, `00_contract/systematic-review-protocol.json` |
| busca | `01_sources/metadata/search-*.json`, `01_sources/source-records.json`, `01_sources/search-plan.json` ou `search-error.json` |
| triagem | `01_sources/systematic_review/studies/*.json`, `02_screening/triage.json`, `07_artifacts/systematic_review/prisma-flow.json` |
| evidência | `03_evidence/claims.json`, `claim-gate.json`, `evidence-cards.json`, `gaps.json`, `07_artifacts/evidence_graph/research-evidence-graph.json` |
| análise | `04_analysis/descriptive.json` |
| auditoria | `05_audit/audit-report.json` |
| manuscrito | `06_manuscript/manuscript.md`, `06_manuscript/references.json` |
| validação | `07_validation/VALIDATION.md` |
| manifesto | `08_manifest/project-manifest.json`, `README.md` |

## Critérios de aceitação

1. **Sem rede nos testes**: o pipeline aceita `searcher_factory` injetável e
   dry-run não instancia buscadores.
2. **Contrato completo**: o contrato de recuperação contém todos os campos da
   tabela e marca `clarification_required` quando a pergunta é provisória ou
   faltam restrições.
3. **Busca honesta**: falha de busca grava `search-error.json`, marca a etapa
   como `blocked` e não inventa registros.
4. **Deduplicação**: registros com o mesmo DOI viram um único estudo; a
   contagem de duplicatas é registrada.
5. **Triagem assistida**: nenhuma decisão de inclusão/exclusão é gravada sem
   `human=True`; a triagem é apenas `candidate_for_human_screening`.
6. **Evidência literal**: claims de metadados citam trecho que é substring do
   abstract normalizado, com SHA-256; claims sem abstract viram lacuna, não
   texto inventado.
7. **Gate**: `mci.metacognitive_gate.aggregate` é executado; nenhum claim é
   promovido a verdade; claims sem evidência ficam `blocked`.
8. **Corpus fornecido**: `council.validate_claims` valida citações literais;
   citação que não é substring da fonte é recusada.
9. **Análise**: apenas estatística descritiva de metadados; nenhum teste
   estatístico, causalidade ou meta-análise é declarado.
10. **Auditoria**: verifica protocolo, contrato, contagens, claims, referências,
    seções, placeholders e overclaim; retorna `fail` para frase absoluta não
    negada ou marcador de preenchimento.
11. **Manuscrito**: contém resumo, introdução, métodos, resultados, discussão,
    limitações, conclusão, referências e apêndices; não contém `[[`, `TODO`,
    `TBD` ou `lorem ipsum`.
12. **Validação**: `VALIDATION.md` lista itens humanos pendentes e comandos de
    continuidade; não declara que a validação foi feita.
13. **Manifesto**: lista artefatos com SHA-256 e bytes; `verify_manifest`
    confirma a integridade; o próprio manifesto não entra na lista.
14. **CLI**: `research project` roteia para o pipeline, aceita `--theme`,
    `--out`, `--question`, `--sources`, `--limit`, `--per-platform`,
    `--timeout`, `--dry-run` e `--corpus`; retorna 0 para entrega e 4 para
    bloqueio.
15. **Sem publicação**: nenhum upload, download de PDF, credencial ou chamada
    externa é executado pelo pipeline.

## RED/GREEN

RED: os testes novos falham porque `scientific_lab.research_project` não
existe e o subcomando `research project` não é reconhecido.

GREEN: o módulo e o subcomando passam os testes; a suíte completa e o
`doctor` permanecem verdes; nenhuma mídia pesada é versionada.

## Evidência de execução

RED: 13 testes novos falharam por ausência de
`scientific_lab.research_project` e do subcomando `research project`.

GREEN: `tests/test_r1051_research_project.py` — **13 passed**. A regressão
R1033–R1051 ficou em **360 passed, 1 skipped**; o guard Remotion passou 11
casos; `doctor` ficou **healthy 22/22**. O dry-run real via CLI gerou o pacote
`/tmp/opencode/r1051-dry` com manifesto íntegro e status `planned`. Nenhum
buscador foi instanciado no dry-run; nenhum PDF, credencial ou publicação foi
usado.

## Limitações

- A busca real depende de rede, disponibilidade das APIs e limites dos
  provedores; a ausência de resultados não prova ausência de literatura.
- Claims de metadados são **em nível de resumo indexado**; não substituem a
  leitura do texto integral.
- A triagem é assistida e continua exigindo dois revisores humanos.
- O corpus fornecido é validado literalmente contra o próprio corpus, não
  contra a versão publicada.
- O manuscrito é um rascunho para validação; não é artigo aceito, publicado ou
  avaliado por pares.
