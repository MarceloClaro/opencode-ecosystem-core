# Pesquisador científico — R1052: texto integral, triagem humana e integridade

O R1052 conecta o pipeline R1051 a três coisas que faltavam para sair do mapa
de resumos:

1. **texto integral local**, com citação por página/parágrafo e aprovação
   humana explícita;
2. **decisões humanas de triagem**, lidas de `review.screen`, com conflitos e
   pendências;
3. **integridade editorial**, com consulta ao Crossref para retratações,
   correções e atualizações.

Ele também permite **atualizar** um projeto sem refazer a busca.

## Comandos

### Projeto com texto integral

```bash
python -m marceloclaro.scientific_lab research project \
  --theme "tema" \
  --out projects/tema-r1052 \
  --fulltext-dir /caminho/dos/pdfs \
  --check-integrity \
  --max-integrity-checks 20
```

### Aprovação humana

Depois da primeira execução, revise:

```text
07_validation/fulltext-approval.template.json
03_evidence/fulltext-candidates.json
```

Preencha o template com `reviewer`, `reviewed_at`, `decision`,
`approved_claim_ids` e `human_confirmation=true`. Salve como
`fulltext-approval.json` e rode:

```bash
python -m marceloclaro.scientific_lab research refresh \
  --out projects/tema-r1052 \
  --fulltext-dir /caminho/dos/pdfs \
  --fulltext-approval /caminho/fulltext-approval.json \
  --check-integrity
```

### Atualizar sem refazer a busca

```bash
python -m marceloclaro.scientific_lab research refresh \
  --out projects/tema-r1052 \
  --check-integrity
```

O `refresh` relê decisões, reaplica integridade, preserva claims/cartões e
regenera manuscrito, auditoria e manifesto. Ele **não** repete a busca.

## Texto integral

- Formatos: PDF, Markdown e TXT.
- PDF: extração por página via `pdf_pipeline.extract_pages` ou `pdftotext`.
- Markdown/TXT: extração por parágrafo.
- Casamento por DOI, título, nome de arquivo ou similaridade.
- Recortes com `p.N`/`par.N`, `quote_sha256` e `source_sha256`.
- Nenhum texto integral é copiado para os JSONs; os arquivos originais
  permanecem no diretório do operador.

### Estados de evidência

| Estado | Significado |
|---|---|
| `candidate` | recorte literal proposto, ainda não aprovado |
| `verified` | recorte aprovado por humano, com `source_file` e hash |
| `rejected` | recorte recusado explicitamente |

`verified` não é verdade científica nem validação externa. Significa apenas que
um humano confirmou o recorte contra o arquivo fornecido.

## Triagem humana

`02_screening/screening-summary.json` lê os arquivos gerados por
`review.screen --human` e reporta:

- estudos pendentes;
- decisões de título/resumo;
- decisões de texto integral;
- incluídos, excluídos e incertos;
- conflitos entre revisores;
- estudos com apenas um revisor.

`human_verified` só é verdadeiro quando:

- todos os estudos têm decisão de texto integral;
- há dois revisores;
- não há conflito;
- todas as decisões de texto integral são humanas.

Pendência não vira inclusão.

## Integridade

`03_evidence/integrity-checks.json` classifica cada estudo com DOI:

| Status | Significado |
|---|---|
| `retracted` | retratação registrada |
| `retracted_notice` | o próprio DOI é uma nota de retratação |
| `correction` | correção/errata registrada |
| `update` | atualização/versão registrada |
| `no_update_found` | nada encontrado no Crossref |
| `unchecked` | sem DOI ou orçamento esgotado |
| `error` | falha de consulta |

Estudo retratado é excluído dos claims e vira lacuna. `no_update_found` **não**
é certificado de integridade.

## Download aberto

`--allow-open-access` tenta baixar PDFs apenas por rotas abertas verificadas,
com `rights_basis` e SHA-256. O downloader não contorna paywall. Se a rota não
for aberta, o registro fica `not_open` e o pipeline continua sem PDF.

## Artefatos novos

```text
01_sources/downloads.json
03_evidence/fulltext-index.json
03_evidence/fulltext-candidates.json
03_evidence/fulltext-summary.json
03_evidence/integrity-checks.json
03_evidence/study-integrity.json
02_screening/screening-summary.json
02_screening/prisma-audit.json
07_validation/fulltext-approval.template.json
07_validation/fulltext-approval.json   # quando aplicado
```

## Auditoria

A auditoria agora verifica:

- downloads somente com `rights_basis` permitido e SHA-256;
- candidatos de texto integral com hash de arquivo, hash de trecho e localizador;
- `verified` de texto integral somente com aprovação humana;
- triagem pendente que não foi tratada como inclusão;
- integridade observacional, sem `truth_claim`.

## Limites

- A aprovação humana confirma o recorte contra o arquivo fornecido, não contra
  a versão publicada.
- PDFs digitalizados sem camada de texto podem produzir pouco texto.
- O casamento textual pode errar; ambiguidades são marcadas.
- Crossref pode não registrar toda retratação/correção.
- `refresh` não atualiza a literatura; isso exige nova busca.
- Meta-análise, risco de viés, GRADE e submissão continuam fora desta revisão.
- Nada é publicado.

## Evidência

- [README R1052](../reports/r1052/README.md)
- [Benchmark real](../reports/r1052/real-benchmark.json)
- [Regressão](../reports/r1052/final-regression.txt)
- [Spec R1052](../specs/SPEC-1052-texto-integral-triagem-integridade.md)
