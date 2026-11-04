# R1052 — texto integral, triagem humana, integridade e benchmark real

Data: 2026-11-04. Frente autorizada: conectar texto integral, triagem humana,
verificação de retratações/correções e benchmark real, conforme a sequência
proposta no R1051.

## O que foi entregue

| Item | Caminho |
|---|---|
| Indexação e citações de texto integral | `scientific_lab/fulltext.py` |
| Integridade via Crossref | `scientific_lab/integrity.py` |
| Leitura de decisões humanas e PRISMA | `scientific_lab/screening.py` |
| Integração e `refresh` | `scientific_lab/research_project.py` |
| CLI | `research project` e `research refresh` |
| Spec | `specs/SPEC-1052-texto-integral-triagem-integridade.md` |
| Testes | `tests/test_r1052_fulltext.py`, `test_r1052_integrity.py`, `test_r1052_screening.py`, `test_r1052_refresh.py` |
| Benchmark real | `reports/r1052/real-benchmark.json` |
| Regressão | `reports/r1052/final-regression.txt` |

## Texto integral

O pipeline agora aceita:

```bash
python -m marceloclaro.scientific_lab research project \
  --theme "tema" --out projects/tema-r1052 \
  --fulltext-dir /caminho/dos/pdfs \
  --fulltext-approval /caminho/aprovacao.json
```

- Indexa PDF, Markdown e TXT locais.
- Extrai texto por página (PDF) ou parágrafo (Markdown/TXT).
- Casa arquivos com estudos por DOI, título, nome de arquivo ou similaridade.
- Propõe recortes com `p.N`/`par.N`, SHA-256 do arquivo e do trecho.
- Gera `07_validation/fulltext-approval.template.json`.
- Só marca `verified` com aprovação humana explícita, revisor, data e
  `source_file`.
- Os demais recortes ficam `candidate` ou `rejected`.

A aprovação é contra o arquivo fornecido, **não** contra a versão publicada.

## Triagem humana

O pipeline lê `09_provenance/systematic_review/screening/*.json`, gerados por
`review.screen --human`, e produz:

- `02_screening/screening-summary.json`;
- conflitos entre revisores;
- pendências e estudos sem decisão;
- contagem de incluídos/excluídos;
- `human_verified` apenas com dois revisores, decisão de texto integral para
  todos os estudos e ausência de conflito.

Pendência nunca vira inclusão.

## Integridade

`--check-integrity` consulta o Crossref por DOI e classifica:

- `retracted`;
- `retracted_notice`;
- `correction`;
- `update`;
- `no_update_found`;
- `unchecked`;
- `error`.

Estudo retratado é excluído dos claims e registrado como lacuna.
`no_update_found` **não** é atestado de integridade.

## Atualização sem refazer a busca

```bash
python -m marceloclaro.scientific_lab research refresh \
  --out projects/tema-r1052 \
  --fulltext-dir /caminho/dos/pdfs \
  --fulltext-approval /caminho/aprovacao.json \
  --check-integrity
```

O `refresh`:

- não repete a busca;
- não recria estudos;
- preserva decisões humanas, claims e cartões;
- remove claims de estudos retratados;
- substitui annotations de texto integral de forma idempotente;
- regenera manuscrito, auditoria e manifesto.

## Benchmark real

Execução em 2026-11-04, com:

- consulta `open access citation advantage`;
- OpenAlex, Crossref e Europe PMC;
- 3 registros por base, 9 no total;
- timeout de 90 s;
- 3 verificações de integridade.

| Métrica | Resultado |
|---|---|
| Tempo | **5,86 s** |
| Registros | **9** |
| Estudos únicos | **8** |
| Duplicatas removidas | **1** |
| Com resumo indexado | **5** |
| Com DOI | **8** |
| Claims com evidência literal | **4** |
| Verificações de integridade | **3** |
| Retratados | **0** |
| Auditoria | **pass_with_pending_human** |
| Manifesto | **completed_pending_external_validation** |
| Integridade do manifesto | **pass** |

Distribuição por fonte: OpenAlex 3, Crossref 3, Europe PMC 3.

O benchmark encontrou um problema real: dois registros com o **mesmo título e
DOIs diferentes** não eram deduplicados. A regra foi corrigida para considerar
título normalizado além do DOI; o novo resultado mostra 9 registros e 8
estudos únicos.

### O que o benchmark prova

- O caminho de rede, busca, normalização, deduplicação, claims, integridade,
  auditoria e manifesto funciona de ponta a ponta.
- O orçamento de tempo e o limite por plataforma são respeitados.
- Nenhum registro foi inventado quando faltou resumo ou DOI.
- A auditoria interna passou com pendências humanas explícitas.

### O que ele não prova

- Não mede precisão ou recall: não há gold standard.
- Não avalia qualidade científica dos artigos.
- Não substitui triagem humana, texto integral ou revisão por pares.
- Uma consulta e três fontes não representam toda a literatura.
- `no_update_found` não é certificado de integridade.

## Testes

| Verificação | Resultado |
|---|---|
| Testes R1052 | **16 passed** |
| R1051 + R1052 | **29 passed** |
| Regressão R1033–R1052 | **376 passed, 1 skipped** |
| Guard Remotion | **11 casos, ok** |
| `doctor` | **healthy 22/22** |

## Limites

- A aprovação humana confirma o recorte contra o arquivo fornecido, não contra
  a versão publicada.
- PDFs digitalizados sem camada de texto podem produzir pouco texto.
- O casamento textual pode errar e marcar ambiguidade.
- Crossref pode não registrar toda retração/correção.
- `refresh` não atualiza a literatura; isso exige nova busca.
- Meta-análise, risco de viés, GRADE e submissão permanecem fora desta revisão.
- Nada foi publicado.
