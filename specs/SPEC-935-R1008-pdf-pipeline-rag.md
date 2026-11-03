---
spec_id: SPEC-935-R1008
title: Pipeline de PDF legal com auditoria, fichamento crítico, resenha e RAG
component: research.pdf_pipeline
status: implemented
test_file: tests/test_r1008_pdf_pipeline.py
---

# SPEC-935-R1008 — PDF legal → auditoria → fichamento → resenha → RAG

**Status:** Implementado (RED → GREEN)
**Data:** 2026-11-01
**Agente:** marceloclaro

## 1. Problema

O Core precisa transformar um DOI em um pacote auditável: PDF obtido por via
legal, texto extraído por página, recortes com citação ABNT, tradução e
argumentação, e um índice RAG consultável. A tentação de "completar" traduções
ou argumentos com texto inventado é o risco central: isso destruiria a
rastreabilidade e a defesa acadêmica.

## 2. Objetivo

`research.pdf_pipeline` orquestra: resolução OA → download verificado →
extração por página → pasta de auditoria → fichamento/resenha → base RAG.

## 3. Não-objetivos

- Acessar fontes não autorizadas (política `research.source_policy`).
- Declarar leitura integral, nota ou qualidade científica.
- Substituir revisão humana da tradução e da argumentação.
- Gerar embeddings neurais: o índice é lexical e determinístico.

## 4. Requisitos

- R1. PDF só é baixado quando a licença e a URL passam pela política.
- R2. `fetcher` injetável; sem ele, nenhum download. Resposta precisa ter
  `%PDF-` e respeitar limite de tamanho.
- R3. Extração por página via pypdf; página sem texto é registrada como vazia.
- R4. Recortes determinísticos, com página e offsets.
- R5. Tradução só é aceita se não introduzir números ausentes no original e
  tiver razão de comprimento plausível; caso contrário, `status="pending"`.
- R6. Argumentação exige justificativa e argumento com extensão mínima e
  menção ao autor; caso contrário, `status="pending"`.
- R7. Nenhum texto pendente é apresentado como tradução ou argumento.
- R8. Citação ABNT por recorte: `(SOBRENOME, ano, p. N)` + referência completa.
- R9. RAG grava `chunks.jsonl`, `index.json` e `manifest.json` com SHA-256.
- R10. Consulta RAG devolve página, score e citação.

## 5. Critérios de aceitação

| ID | Critério | Verificação |
|---|---|---|
| CA1 | Resolver recusa fonte bloqueada | `test_resolver_recusa_fonte_bloqueada` |
| CA2 | Sem runner, nenhum PDF | `test_sem_runner_nao_baixa` |
| CA3 | Fetcher rejeita não-PDF | `test_fetcher_rejeita_nao_pdf` |
| CA4 | Extração preserva páginas | `test_extracao_por_pagina` |
| CA5 | Recortes determinísticos com página | `test_recortes_deterministicos` |
| CA6 | Tradução com número inventado é rejeitada | `test_traducao_com_numero_inventado_rejeitada` |
| CA7 | Sem tradutor, status pendente | `test_sem_tradutor_fica_pendente` |
| CA8 | Argumentação sem autor é rejeitada | `test_argumentacao_sem_autor_rejeitada` |
| CA9 | Fichamento contém citação ABNT | `test_fichamento_tem_citacao_abnt` |
| CA10 | RAG recupera a página correta | `test_rag_recupera_pagina` |
| CA11 | Manifesto RAG detecta alteração | `test_manifesto_rag_detecta_adulteracao` |

## 6. Limites

A qualidade da tradução e da argumentação depende do tradutor/argumentador
injetado (LLM local ou humano). O pipeline valida forma e anti-fabricação
heurística; não prova equivalência semântica nem correção argumentativa.
