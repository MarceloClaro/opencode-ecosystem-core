# SPEC-935-R469 — Pesquisador Universal v4.2 Native Scientific Runtime

## Objetivo
Internalizar no OpenCode Ecosystem Core o caminho científico mínimo de maior valor, sem duplicar o kernel e sem exigir instalação externa para busca/download OA, screening e Evidence Graph.

## Contrato arquitetural

1. `marceloclaro` permanece único orquestrador primário.
2. `research/articles`, `review` e `evidence` são executados no próprio checkout do Core.
3. módulos avançados (`mesh`, `mission`, `living`, `synthesis`, `grade`, `causal`, `federation`, `production`) usam fallback v4.1 somente se o release externo for verificado.
4. o downloader do Core é `open_science_only` e não executa mecanismo de bypass de paywall.
5. decisão de screening final requer humano; full text nunca é incluído automaticamente.
6. `EvidenceAnnotation=verified` exige `source_sha256` e confirmação humana.
7. arestas `candidate` não contam como evidência verificada.
8. nenhum score/ranking/consenso possui autoridade epistêmica automática.

## Contratos nativos

- ArticleSearchManifest
- ArticleDownloadReceipt
- SystematicReviewProtocol
- StudyRecord
- ScreeningDecision
- PrismaFlow
- EvidenceAnnotation
- ResearchEvidenceGraph

## Gates de aceite

- pesquisa nativa funciona sem `PESQUISADOR_UNIVERSAL_HOME`;
- downloader rejeita HTML e registros sem OA verificada;
- download sintético `%PDF-` registra SHA-256;
- deduplicação de ingest por DOI;
- screening sem `human=true` falha fechado;
- evidence `verified` sem source/humano falha fechado;
- Evidence Graph separa `candidate` e `verified`;
- módulos avançados continuam fail-closed sem release externo verificado;
- o código operacional de `research/downloader.py` não contém nem invoca mecanismo de bypass removido.
